"""
Auth modülü — JWT ve şifre yardımcı fonksiyonları.

JWT İşlemleri:
  - Access token oluşturma / decode etme
  - Refresh token üretme (random, JWT değil)

Şifre İşlemleri:
  - bcrypt ile hash'leme
  - Hash doğrulama
"""

import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
import structlog

from core.config import settings

logger = structlog.get_logger(__name__)


# ── Şifre Hashing (bcrypt) ──────────────────────────────

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Şifreyi bcrypt ile hash'le.

    Args:
        password: Düz metin şifre.

    Returns:
        bcrypt hash string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Düz metin şifreyi hash ile karşılaştır.

    Args:
        plain_password: Kullanıcının girdiği şifre.
        hashed_password: Veritabanındaki hash.

    Returns:
        True ise şifre doğru.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Access Token ─────────────────────────────────────


def create_access_token(
    user_id: str,
    email: str,
    username: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    JWT access token oluştur.

    Payload:
        {
            "sub": "user_id",
            "email": "user@example.com",
            "username": "testuser",
            "type": "access",
            "iat": 1234567890,
            "exp": 1234567890
        }

    Args:
        user_id: Kullanıcının MongoDB _id'si (string).
        email: Kullanıcının email adresi.
        username: Kullanıcı adı.
        expires_delta: Özel süre (None ise config'den alınır).

    Returns:
        Encoded JWT string.
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": user_id,
        "email": email,
        "username": username,
        "type": "access",
        "iat": now,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    logger.debug("access_token_created", user_id=user_id)
    return token


def decode_access_token(token: str) -> dict:
    """
    JWT access token'ı decode et ve doğrula.

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded payload dict.

    Raises:
        JWTError: Token geçersiz veya süresi dolmuşsa.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    # Token tipi kontrolü
    if payload.get("type") != "access":
        raise JWTError("Token tipi 'access' değil.")

    return payload


# ── Refresh Token ────────────────────────────────────────


def generate_refresh_token() -> str:
    """
    Cryptographically secure refresh token üret.

    JWT kullanmıyoruz çünkü refresh token MongoDB'de
    saklanıyor ve server-side validasyon yapılıyor.

    Returns:
        86 karakter URL-safe random string.
    """
    return secrets.token_urlsafe(64)


def get_access_token_expire_seconds() -> int:
    """Access token'ın kaç saniye geçerli olduğunu döndür."""
    return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
