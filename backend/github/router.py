"""
GitHub modülü — API endpoint'leri.

Tüm endpoint'ler /api/v1/github prefix'i altında çalışır.

Endpoint'ler:
  POST /clone → Public repo'yu clone edip projeye kopyala
"""

from fastapi import APIRouter, Depends
import structlog

from auth.dependencies import get_current_user
from auth.models import TokenPayload
from core.database import get_database
from github.models import CloneRequest, CloneResponse
from github.service import clone_repo_to_project

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "/clone",
    response_model=CloneResponse,
    summary="GitHub repo import",
    description=(
        "Public GitHub repo'sunu clone eder ve "
        "projenin container'ına kopyalar. "
        "Proje çalışıyor (running) durumda olmalıdır."
    ),
)
async def clone_repo_endpoint(
    data: CloneRequest,
    current_user: TokenPayload = Depends(get_current_user),
) -> CloneResponse:
    """Public GitHub repo'sunu projeye import et."""
    db = get_database()

    result = await clone_repo_to_project(
        db=db,
        repo_url=data.repo_url,
        project_id=data.project_id,
        user_id=current_user.sub,
    )

    logger.info(
        "clone_endpoint",
        project_id=data.project_id,
        repo_url=data.repo_url,
        files_copied=result.files_copied,
    )

    return result
