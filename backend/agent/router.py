"""
Agent modülü — API endpoint'leri & WebSocket.

REST Endpoint'ler:
  POST /api/v1/agent/run                       → Agent çalıştır
  GET  /api/v1/agent/sessions/{project_id}     → Session geçmişi
  GET  /api/v1/agent/sessions/{session_id}/steps → Session adımları

WebSocket Endpoint'ler:
  WS /ws/agent/{session_id}   → Agent adım stream
  WS /ws/logs/{project_id}    → Container log stream
"""

import asyncio
import uuid

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from auth.dependencies import get_current_user
from auth.models import TokenPayload
from core.database import Database, get_database
from core.exceptions import NotFoundException
from projects.models import ProjectStatus
from sandbox.client import SandboxClient

logger = structlog.get_logger(__name__)

router = APIRouter()


# ── Request/Response Modelleri ───────────────────────────


class RunAgentRequest(BaseModel):
    """Agent çalıştırma isteği."""

    project_id: str = Field(..., description="Hedef proje ID'si")
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Kullanıcının isteği",
        examples=["Login sayfası ekle"],
    )


class RunAgentResponse(BaseModel):
    """Agent çalıştırma başlatma response'u."""

    session_id: str
    message: str


class SessionResponse(BaseModel):
    """Agent session bilgisi."""

    session_id: str
    project_id: str
    user_request: str
    status: str
    steps_count: int
    created_at: str


class StepResponse(BaseModel):
    """Agent adım bilgisi."""

    step_no: int
    node: str
    action: str
    result: str
    timestamp: str


# ── POST /run ────────────────────────────────────────────


@router.post(
    "/run",
    response_model=RunAgentResponse,
    summary="Agent çalıştır",
    description=(
        "Proje için AI agent çalıştırır. "
        "Arka planda asenkron çalışır, sonuçlar "
        "WebSocket üzerinden stream edilir."
    ),
)
async def run_agent_endpoint(
    data: RunAgentRequest,
    current_user: TokenPayload = Depends(get_current_user),
) -> RunAgentResponse:
    """Agent'ı başlat, session_id döndür."""
    db = get_database()

    # Proje kontrolü
    from bson import ObjectId

    project = await db["projects"].find_one(
        {"_id": ObjectId(data.project_id)}
    )
    if not project:
        raise NotFoundException("Proje bulunamadı.")

    if project["user_id"] != current_user.sub:
        raise NotFoundException("Proje bulunamadı.")

    # if project["status"] != ProjectStatus.RUNNING.value:
    #     from core.exceptions import BadRequestException
    #     raise BadRequestException(
    #         "Agent çalıştırmak için proje 'running' durumunda olmalıdır."
    #     )

    # Session oluştur
    session_id = str(uuid.uuid4())
    from datetime import datetime, timezone

    # Session dokümanını doğrudan id, user ve request ile ekle
    session_doc = {
        "session_id": session_id,
        "project_id": data.project_id,
        "user_id": current_user.sub,
        "user_request": data.message,
        "status": "running",
        "steps": [],
        "created_at": datetime.now(timezone.utc),
    }
    await db["agent_sessions"].insert_one(session_doc)

    # Agent'ı arka planda çalıştır
    from agent.graph import run_agent
    asyncio.create_task(
        run_agent(
            project_id=data.project_id,
            user_request=data.message,
            session_id=session_id,
        )
    )

    logger.info(
        "agent_run_initiated",
        session_id=session_id,
        project_id=data.project_id,
    )

    return RunAgentResponse(
        session_id=session_id,
        message="Agent başlatıldı. WebSocket ile takip edebilirsiniz.",
    )


# ── GET /sessions/{project_id} ──────────────────────────


@router.get(
    "/sessions/{project_id}",
    response_model=list[SessionResponse],
    summary="Proje session geçmişi",
    description="Bir projenin tüm agent session'larını listeler.",
)
async def list_sessions_endpoint(
    project_id: str,
    current_user: TokenPayload = Depends(get_current_user),
) -> list[SessionResponse]:
    """Projenin agent session geçmişini getir."""
    db = get_database()

    cursor = db["agent_sessions"].find(
        {"project_id": project_id, "user_id": current_user.sub}
    ).sort("created_at", -1)

    sessions = []
    async for doc in cursor:
        sessions.append(SessionResponse(
            session_id=doc["session_id"],
            project_id=doc["project_id"],
            user_request=doc.get("user_request", ""),
            status=doc.get("status", "unknown"),
            steps_count=len(doc.get("steps", [])),
            created_at=doc["created_at"].isoformat(),
        ))

    return sessions


# ── GET /sessions/{session_id}/steps ─────────────────────


@router.get(
    "/sessions/{session_id}/steps",
    response_model=list[StepResponse],
    summary="Session adımları",
    description="Bir session'ın tüm adımlarını döndürür.",
)
async def get_session_steps_endpoint(
    session_id: str,
    current_user: TokenPayload = Depends(get_current_user),
) -> list[StepResponse]:
    """Session'ın tüm adımlarını getir."""
    db = get_database()

    session = await db["agent_sessions"].find_one(
        {"session_id": session_id, "user_id": current_user.sub}
    )

    if not session:
        raise NotFoundException("Session bulunamadı.")

    steps = []
    for step in session.get("steps", []):
        steps.append(StepResponse(
            step_no=step.get("step_no", 0),
            node=step.get("node", ""),
            action=step.get("action", ""),
            result=step.get("result", ""),
            timestamp=step.get("timestamp", "").isoformat()
            if hasattr(step.get("timestamp", ""), "isoformat")
            else str(step.get("timestamp", "")),
        ))

    return steps


# ═══════════════════════════════════════════════════════
# WEBSOCKET ENDPOINT'LERİ
# ═══════════════════════════════════════════════════════


@router.websocket("/{session_id}/stream")
async def agent_stream_ws(
    websocket: WebSocket,
    session_id: str,
) -> None:
    """
    Agent adım stream WebSocket'i.

    URL: ws://host/api/v1/agent/{session_id}/stream

    Agent her adımda şu formatı gönderir:
    {
        "type": "step",
        "step_no": 3,
        "node": "action",
        "action": "write_file src/main.py",
        "status": "success"
    }

    Tamamlandığında:
    {
        "type": "complete",
        "total_steps": 12
    }
    """
    await websocket.accept()
    logger.info("ws_agent_connected", session_id=session_id)

    db = get_database()

    try:
        last_step_count = 0

        while True:
            await asyncio.sleep(1)  # Poll interval

            session = await db["agent_sessions"].find_one(
                {"session_id": session_id}
            )

            if not session:
                await websocket.send_json({
                    "type": "error",
                    "message": "Session bulunamadı.",
                })
                break

            # Yeni adımları gönder
            steps = session.get("steps", [])
            if len(steps) > last_step_count:
                for step in steps[last_step_count:]:
                    await websocket.send_json({
                        "type": "step",
                        "step_no": step.get("step_no", 0),
                        "node": step.get("node", ""),
                        "action": step.get("action", "")[:200],
                        "status": "success",
                    })
                last_step_count = len(steps)

            # Session bitti mi?
            status = session.get("status", "running")
            if status in ("completed", "failed"):
                await websocket.send_json({
                    "type": "complete" if status == "completed" else "error",
                    "total_steps": len(steps),
                    "status": status,
                    "error": session.get("error"),
                })
                break

    except WebSocketDisconnect:
        logger.info("ws_agent_disconnected", session_id=session_id)
    except Exception as e:
        logger.error("ws_agent_error", error=str(e))
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


@router.websocket("/logs/{project_id}/stream")
async def logs_stream_ws(
    websocket: WebSocket,
    project_id: str,
) -> None:
    """
    Container log stream WebSocket'i.

    URL: ws://host/api/v1/agent/logs/{project_id}/stream

    Sidecar'ın /logs endpoint'ini sürekli poll ederek
    yeni logları WebSocket üzerinden iletir.
    """
    await websocket.accept()
    logger.info("ws_logs_connected", project_id=project_id)

    client = SandboxClient(project_id)
    last_logs = ""

    try:
        while True:
            await asyncio.sleep(2)  # Poll interval

            try:
                result = await client.get_logs(lines=50)
                current_logs = result.get("logs", "")

                # Sadece yeni logları gönder
                if current_logs != last_logs:
                    await websocket.send_json({
                        "type": "logs",
                        "content": current_logs,
                    })
                    last_logs = current_logs
            except Exception:
                # Sidecar'a ulaşılamıyorsa sessizce devam et
                pass

    except WebSocketDisconnect:
        logger.info("ws_logs_disconnected", project_id=project_id)
    except Exception as e:
        logger.error("ws_logs_error", error=str(e))
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
