"""
AI Code Reviewer — Backend Ana Uygulama.

FastAPI tabanlı modüler monolitik backend.
Tüm modüller /api/v1/ prefix'i altında çalışır.

Çalıştırma:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import structlog

from core.config import settings
from core.database import Database
from core.exceptions import AppException, app_exception_handler
from core.logging import setup_logging
from core.rate_limit import limiter, rate_limit_exceeded_handler


# ── Logging Başlat ───────────────────────────────────────
setup_logging(debug=settings.DEBUG)
logger = structlog.get_logger(__name__)


# ── Yaşam Döngüsü ───────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Uygulama yaşam döngüsü yöneticisi.

    Startup:
      - MongoDB Atlas bağlantısı
      - MongoDB indekslerini oluştur
      - Idle pod checker background task başlat

    Shutdown:
      - Background task'ları iptal et
      - Tüm bağlantıları güvenle kapat
    """
    # ── Startup ──
    logger.info(
        "app_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    await Database.connect()

    # MongoDB indekslerini oluştur
    db = Database.get_db()

    from auth.service import ensure_indexes as auth_ensure_indexes
    from projects.service import ensure_indexes as projects_ensure_indexes

    try:
        await auth_ensure_indexes(db)
        await projects_ensure_indexes(db)
    except Exception as e:
        logger.error("index_creation_failed", error=str(e))

    # Idle pod checker background task
    from projects.service import idle_pod_checker
    idle_task = asyncio.create_task(idle_pod_checker())

    logger.info("app_started", api_prefix=settings.API_V1_PREFIX)

    yield

    # ── Shutdown ──
    logger.info("app_shutting_down")

    # Background task'ları iptal et
    idle_task.cancel()
    try:
        await idle_task
    except asyncio.CancelledError:
        pass

    await Database.disconnect()
    logger.info("app_stopped")


# ── Uygulama Factory ────────────────────────────────────
def create_app() -> FastAPI:
    """
    FastAPI uygulama factory.

    Middleware'leri, exception handler'ları ve
    router'ları tek bir noktadan yapılandırır.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI destekli kod inceleme ve geliştirme platformu. "
            "Sıfırdan proje oluşturma, GitHub import, "
            "canlı preview ve AI agent ile kod düzenleme."
        ),
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware: CORS ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Middleware: Rate Limiting ──
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ── Exception Handler: AppException ──
    app.add_exception_handler(AppException, app_exception_handler)

    # ── Health Check (Kubernetes probes) ──
    @app.get(
        "/health",
        tags=["Health"],
        summary="Sağlık kontrolü",
        description="Kubernetes liveness/readiness probe endpoint'i.",
    )
    async def health_check():
        """
        Uygulama ve bağımlılıkların durumunu kontrol eder.

        Returns:
            - status: healthy | degraded
            - database: connected | disconnected
        """
        try:
            db = Database.get_db()
            await db.command("ping")
            db_status = "connected"
        except Exception:
            db_status = "disconnected"

        overall = "healthy" if db_status == "connected" else "degraded"

        return {
            "status": overall,
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "components": {
                "database": db_status,
                # İleride eklenecek:
                # "qdrant": qdrant_status,
                # "redis": redis_status,
            },
        }

    # ── Router'lar ──
    from auth.router import router as auth_router
    from projects.router import router as projects_router
    from github.router import router as github_router
    from agent.router import router as agent_router

    app.include_router(
        auth_router,
        prefix=f"{settings.API_V1_PREFIX}/auth",
        tags=["Auth"],
    )

    app.include_router(
        projects_router,
        prefix=f"{settings.API_V1_PREFIX}/projects",
        tags=["Projects"],
    )

    app.include_router(
        github_router,
        prefix=f"{settings.API_V1_PREFIX}/github",
        tags=["GitHub"],
    )

    app.include_router(
        agent_router,
        prefix=f"{settings.API_V1_PREFIX}/agent",
        tags=["Agent"],
    )

    return app


# ── App Instance ─────────────────────────────────────────
app = create_app()
