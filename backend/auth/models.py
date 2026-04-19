"""
Auth modülü — Pydantic modelleri.

Request/Response modelleri ve MongoDB doküman şemaları.
Şifre validasyonu burada yapılır (min 8 karakter, 1 büyük harf, 1 rakam).
"""

import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ═══════════════════════════════════════════════════════
# REQUEST MODELLERİ
# ═══════════════════════════════════════════════════════


class RegisterRequest(BaseModel):
    """Kullanıcı kayıt isteği."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Kullanıcı adı (3-30 karakter, harf/rakam/_/- )",
        examples=["john_doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Email adresi",
        examples=["john@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Şifre (min 8 karakter, 1 büyük harf, 1 rakam)",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Username sadece harf, rakam, _ ve - içerebilir."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Kullanıcı adı sadece harf, rakam, _ ve - içerebilir."
            )
        # İlk karakter harf veya rakam olmalı
        if not v[0].isalnum():
            raise ValueError(
                "Kullanıcı adı harf veya rakam ile başlamalıdır."
            )
        return v.lower()  # Küçük harfe çevir (case-insensitive)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Şifre politikası: min 8 karakter, 1 büyük harf, 1 rakam."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Şifre en az bir büyük harf içermelidir.")
        if not re.search(r"\d", v):
            raise ValueError("Şifre en az bir rakam içermelidir.")
        return v


class LoginRequest(BaseModel):
    """Kullanıcı giriş isteği."""

    email: EmailStr = Field(
        ...,
        description="Kayıtlı email adresi",
        examples=["john@example.com"],
    )
    password: str = Field(
        ...,
        description="Şifre",
    )


class RefreshRequest(BaseModel):
    """Access token yenileme isteği."""

    refresh_token: str = Field(
        ...,
        description="Geçerli refresh token",
    )


class LogoutRequest(BaseModel):
    """Çıkış isteği."""

    refresh_token: str = Field(
        ...,
        description="Revoke edilecek refresh token",
    )


# ═══════════════════════════════════════════════════════
# RESPONSE MODELLERİ
# ═══════════════════════════════════════════════════════


class TokenResponse(BaseModel):
    """JWT token çifti response'u."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        description="Access token'ın kaç saniye geçerli olduğu"
    )


class UserResponse(BaseModel):
    """Kullanıcı bilgisi response'u."""

    id: str
    username: str
    email: str
    auth_provider: str = "local"
    is_active: bool = True
    created_at: datetime


class MessageResponse(BaseModel):
    """Basit mesaj response'u."""

    message: str


# ═══════════════════════════════════════════════════════
# TOKEN PAYLOAD MODELLERİ
# ═══════════════════════════════════════════════════════


class TokenPayload(BaseModel):
    """
    Decode edilmiş JWT access token payload'ı.

    get_current_user dependency'sinde kullanılır.
    """

    sub: str  # user_id
    email: str
    username: str
    type: str = "access"
