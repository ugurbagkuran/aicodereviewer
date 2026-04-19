"""
GitHub modülü — Pydantic modelleri.
"""

from pydantic import BaseModel, Field, field_validator


class CloneRequest(BaseModel):
    """GitHub repo clone isteği."""

    repo_url: str = Field(
        ...,
        description="Public GitHub repo URL'i",
        examples=["https://github.com/user/repo"],
    )
    project_id: str = Field(
        ...,
        description="Hedef proje ID'si (dosyalar buraya kopyalanır)",
    )

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v: str) -> str:
        """Sadece GitHub URL'lerini kabul et."""
        v = v.strip().rstrip("/")

        # .git uzantısını temizle
        if v.endswith(".git"):
            v = v[:-4]

        if not v.startswith("https://github.com/"):
            raise ValueError(
                "Sadece GitHub URL'leri desteklenir. "
                "Örnek: https://github.com/user/repo"
            )

        # user/repo formatını kontrol et
        parts = v.replace("https://github.com/", "").split("/")
        if len(parts) < 2 or not parts[0] or not parts[1]:
            raise ValueError(
                "Geçersiz repo URL'i. "
                "Format: https://github.com/{user}/{repo}"
            )

        return v


class CloneResponse(BaseModel):
    """GitHub clone sonucu."""

    project_id: str
    repo_url: str
    files_copied: int
    files_skipped: int
    message: str


class CloneProgress(BaseModel):
    """Clone ilerleme durumu (WebSocket için)."""

    stage: str  # "cloning" | "copying" | "indexing" | "done"
    progress: float  # 0.0 - 1.0
    message: str
    files_copied: int = 0
    total_files: int = 0
