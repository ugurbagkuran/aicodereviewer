"""
Sandbox modülü — Pydantic modelleri.

Sidecar API ile iletişimde kullanılan
request/response modelleri.
"""

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════
# DOSYA İŞLEMLERİ
# ═══════════════════════════════════════════════════════


class FileInfo(BaseModel):
    """Dosya/klasör bilgisi."""

    name: str
    path: str
    is_dir: bool = False
    size: int | None = None  # byte cinsinden (dosyalar için)


class FileListResponse(BaseModel):
    """Dosya listesi response'u."""

    path: str
    files: list[FileInfo]


class FileContentResponse(BaseModel):
    """Dosya içeriği response'u."""

    path: str
    content: str
    size: int


class WriteFileRequest(BaseModel):
    """Dosya yazma isteği."""

    path: str = Field(
        ...,
        description="Dosya yolu (container içinde)",
        examples=["src/main.py"],
    )
    content: str = Field(
        ...,
        description="Dosya içeriği",
    )


class DeleteFileRequest(BaseModel):
    """Dosya silme isteği."""

    path: str = Field(
        ...,
        description="Silinecek dosya yolu",
        examples=["src/old_file.py"],
    )


# ═══════════════════════════════════════════════════════
# KOMUT ÇALIŞTIRMA
# ═══════════════════════════════════════════════════════


class ExecCommandRequest(BaseModel):
    """Komut çalıştırma isteği."""

    command: str = Field(
        ...,
        description="Çalıştırılacak shell komutu",
        examples=["npm install", "python -m pytest"],
    )
    timeout: int = Field(
        default=30,
        description="Komut timeout süresi (saniye)",
        ge=1,
        le=300,
    )


class ExecCommandResponse(BaseModel):
    """Komut çalıştırma sonucu."""

    command: str
    exit_code: int
    stdout: str
    stderr: str


# ═══════════════════════════════════════════════════════
# LOG ve SERVİS
# ═══════════════════════════════════════════════════════


class LogsResponse(BaseModel):
    """Uygulama logları response'u."""

    logs: str
    lines: int


class RestartResponse(BaseModel):
    """Servis yeniden başlatma response'u."""

    success: bool
    message: str
