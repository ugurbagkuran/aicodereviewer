"""
Auth modülü — API endpoint'leri.

Tüm endpoint'ler /api/v1/auth prefix'i altında çalışır.
Rate limiting auth endpoint'lerine uygulanır (brute-force koruması).

Endpoint'ler:
  POST /register  → Yeni kullanıcı kaydı
  POST /login     → Giriş yap, token al
  POST /refresh   → Access token yenile
  POST /logout    → Çıkış yap, token'ları geçersiz kıl
  GET  /me        → Mevcut kullanıcı bilgisi
"""

from fastapi import APIRouter, Depends, Request
import structlog

from auth.dependencies import get_current_user
from auth.models import (
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenPayload,
    TokenResponse,
    UserResponse,
)
from auth.service import (
    authenticate_user,
    create_token_pair,
    get_user_by_id,
    logout_user,
    refresh_access_token,
    register_user,
)
from core.database import get_database
from core.exceptions import NotFoundException
from core.rate_limit import limiter

logger = structlog.get_logger(__name__)

router = APIRouter()


# ── POST /register ───────────────────────────────────────


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Yeni kullanıcı kaydı",
    description=(
        "Email, username ve şifre ile yeni kullanıcı oluşturur. "
        "Şifre politikası: min 8 karakter, 1 büyük harf, 1 rakam."
    ),
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
) -> UserResponse:
    """Yeni kullanıcı kaydı oluştur."""
    db = get_database()
    user = await register_user(db, data)

    logger.info(
        "register_endpoint",
        user_id=user.id,
        username=user.username,
    )
    return user


# ── POST /login ──────────────────────────────────────────


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Kullanıcı girişi",
    description=(
        "Email ve şifre ile giriş yapar. "
        "Access token (30 dk) ve refresh token (30 gün) döndürür."
    ),
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: LoginRequest,
) -> TokenResponse:
    """Email + şifre ile giriş yap, token çifti al."""
    db = get_database()

    # Kullanıcıyı doğrula
    user = await authenticate_user(db, data.email, data.password)

    # Token çifti oluştur
    tokens = await create_token_pair(
        db=db,
        user_id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
    )

    logger.info(
        "login_endpoint",
        user_id=str(user["_id"]),
    )
    return tokens


# ── POST /refresh ────────────────────────────────────────


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Access token yenileme",
    description=(
        "Geçerli bir refresh token ile yeni access token alır. "
        "Refresh Token Rotation uygulanır: eski refresh token "
        "geçersiz kılınır, yeni bir çift döndürülür."
    ),
)
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    data: RefreshRequest,
) -> TokenResponse:
    """Refresh token ile yeni token çifti al."""
    db = get_database()
    tokens = await refresh_access_token(db, data.refresh_token)

    logger.info("refresh_endpoint")
    return tokens


# ── POST /logout ─────────────────────────────────────────


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Kullanıcı çıkışı",
    description=(
        "Refresh token'ı revoke eder ve access token'ı "
        "blacklist'e ekler."
    ),
)
async def logout(
    request: Request,
    data: LogoutRequest,
    current_user: TokenPayload = Depends(get_current_user),
) -> MessageResponse:
    """Çıkış yap, token'ları geçersiz kıl."""
    db = get_database()

    # Authorization header'dan access token'ı al
    auth_header = request.headers.get("authorization", "")
    access_token = auth_header.replace("Bearer ", "")

    await logout_user(
        db=db,
        refresh_token_str=data.refresh_token,
        access_token_str=access_token,
    )

    logger.info("logout_endpoint", user_id=current_user.sub)
    return MessageResponse(message="Başarıyla çıkış yapıldı.")


# ── GET /me ──────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Mevcut kullanıcı bilgisi",
    description="JWT token'dan kullanıcı bilgilerini döndürür.",
)
async def me(
    current_user: TokenPayload = Depends(get_current_user),
) -> UserResponse:
    """Mevcut kullanıcının profil bilgisini getir."""
    db = get_database()
    user = await get_user_by_id(db, current_user.sub)

    if not user:
        raise NotFoundException("Kullanıcı bulunamadı.")

    return user
