"""
Projects modülü — Pydantic modelleri.

Proje durumları, request/response modelleri ve
MongoDB doküman şemaları.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════
# PROJE DURUMLARI
# ═══════════════════════════════════════════════════════


class ProjectStatus(str, Enum):
    """
    Proje yaşam döngüsü durumları.

    created  → Pod yok, sadece DB kaydı var
    starting → Pod açılıyor (geçici durum)
    running  → Pod ayakta, preview URL aktif
    stopping → Pod kapatılıyor (geçici durum)
    stopped  → Pod silindi, DB kaydı duruyor
    error    → Bir şeyler ters gitti
    """

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


# ═══════════════════════════════════════════════════════
# REQUEST MODELLERİ
# ═══════════════════════════════════════════════════════


class CreateProjectRequest(BaseModel):
    """Yeni proje oluşturma isteği."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Proje adı",
        examples=["My Awesome App"],
    )


class UpdateProjectRequest(BaseModel):
    """Proje güncelleme isteği (şimdilik sadece isim)."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Yeni proje adı",
        examples=["My Updated App"],
    )


# ═══════════════════════════════════════════════════════
# RESPONSE MODELLERİ
# ═══════════════════════════════════════════════════════


class ProjectResponse(BaseModel):
    """Proje bilgisi response'u."""

    id: str
    user_id: str
    name: str
    status: ProjectStatus
    preview_url: str | None = None
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """Proje listesi response'u."""

    projects: list[ProjectResponse]
    total: int
