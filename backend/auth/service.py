"""
Auth modülü — İş mantığı (business logic).

Tüm veritabanı işlemleri ve auth akışları burada yönetilir.
Router bu fonksiyonları çağırır, doğrudan DB erişimi yapmaz.

Fonksiyonlar:
  - ensure_indexes()       → MongoDB indekslerini oluştur
  - register_user()        → Yeni kullanıcı kaydı
  - authenticate_user()    → Email + şifre doğrulama
  - create_token_pair()    → Access + refresh token üret
  - refresh_access_token() → Refresh token ile yeni access token
  - logout_user()          → Token'ları revoke et
  - get_user_by_id()       → ID ile kullanıcı getir
"""

from datetime import datetime, timedelta, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from auth.models import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from auth.utils import (
    create_access_token,
    generate_refresh_token,
    get_access_token_expire_seconds,
    hash_password,
    verify_password,
)
from core.config import settings
from core.exceptions import ConflictException, UnauthorizedException
from core.token_blacklist import token_blacklist

logger = structlog.get_logger(__name__)


# ── Koleksiyon İsimleri ──────────────────────────────────

USERS_COLLECTION = "users"
REFRESH_TOKENS_COLLECTION = "refresh_tokens"


# ── MongoDB İndeksleri ───────────────────────────────────


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """
    Auth modülü için gerekli MongoDB indekslerini oluştur.

    Uygulama startup'ında çağrılır.
    İdempotent: birden fazla çağrılsa bile sorun çıkarmaz.
    """
    users = db[USERS_COLLECTION]
    refresh_tokens = db[REFRESH_TOKENS_COLLECTION]

    # users: email ve username için unique index
    await users.create_index("email", unique=True)
    await users.create_index("username", unique=True)

    # refresh_tokens: token ile hızlı arama
    await refresh_tokens.create_index("token", unique=True)
    # refresh_tokens: user_id ile arama (logout all devices)
    await refresh_tokens.create_index("user_id")
    # refresh_tokens: TTL index — süresi dolan token'lar otomatik silinir
    await refresh_tokens.create_index(
        "expires_at",
        expireAfterSeconds=0,
    )

    logger.info("auth_indexes_ensured")


# ── Kullanıcı Kaydı ─────────────────────────────────────


async def register_user(
    db: AsyncIOMotorDatabase,
    data: RegisterRequest,
) -> UserResponse:
    """
    Yeni kullanıcı oluştur.

    Args:
        db: MongoDB database instance.
        data: Kayıt form verisi.

    Returns:
        Oluşturulan kullanıcının bilgisi.

    Raises:
        ConflictException: Email veya username zaten kayıtlıysa.
    """
    users = db[USERS_COLLECTION]

    # Email kontrolü
    existing_email = await users.find_one({"email": data.email})
    if existing_email:
        raise ConflictException("Bu email adresi zaten kayıtlı.")

    # Username kontrolü
    existing_username = await users.find_one({"username": data.username})
    if existing_username:
        raise ConflictException("Bu kullanıcı adı zaten alınmış.")

    # Kullanıcı dokümanı oluştur
    now = datetime.now(timezone.utc)
    user_doc = {
        "username": data.username,
        "email": data.email,
        "hashed_password": hash_password(data.password),
        "auth_provider": "local",  # İleride: "github", "google"
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    result = await users.insert_one(user_doc)

    logger.info(
        "user_registered",
        user_id=str(result.inserted_id),
        username=data.username,
        auth_provider="local",
    )

    return UserResponse(
        id=str(result.inserted_id),
        username=data.username,
        email=data.email,
        auth_provider="local",
        is_active=True,
        created_at=now,
    )


# ── Kimlik Doğrulama ────────────────────────────────────


async def authenticate_user(
    db: AsyncIOMotorDatabase,
    email: str,
    password: str,
) -> dict:
    """
    Email ve şifre ile kullanıcıyı doğrula.

    Args:
        db: MongoDB database instance.
        email: Kullanıcının email adresi.
        password: Düz metin şifre.

    Returns:
        MongoDB user dokümanı.

    Raises:
        UnauthorizedException: Kullanıcı bulunamazsa veya şifre yanlışsa.
    """
    users = db[USERS_COLLECTION]

    user = await users.find_one({"email": email})
    if not user:
        # Timing attack'ı önlemek için sahte hash kontrolü yap
        verify_password("dummy", hash_password("dummy"))
        raise UnauthorizedException("Email veya şifre hatalı.")

    if not verify_password(password, user["hashed_password"]):
        raise UnauthorizedException("Email veya şifre hatalı.")

    if not user.get("is_active", True):
        raise UnauthorizedException("Hesabınız devre dışı bırakılmış.")

    logger.info("user_authenticated", user_id=str(user["_id"]))
    return user


# ── Token Üretimi ────────────────────────────────────────


async def create_token_pair(
    db: AsyncIOMotorDatabase,
    user_id: str,
    email: str,
    username: str,
) -> TokenResponse:
    """
    Access token + refresh token çifti oluştur.

    Refresh token MongoDB'ye kaydedilir.

    Args:
        db: MongoDB database instance.
        user_id: Kullanıcının MongoDB _id'si (string).
        email: Kullanıcının email adresi.
        username: Kullanıcı adı.

    Returns:
        TokenResponse: access_token, refresh_token, token_type, expires_in
    """
    refresh_tokens = db[REFRESH_TOKENS_COLLECTION]

    # Access token (JWT)
    access_token = create_access_token(
        user_id=user_id,
        email=email,
        username=username,
    )

    # Refresh token (random string)
    refresh_token = generate_refresh_token()

    # Refresh token'ı MongoDB'ye kaydet
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    await refresh_tokens.insert_one({
        "token": refresh_token,
        "user_id": user_id,
        "expires_at": expires_at,
        "revoked": False,
        "created_at": now,
    })

    logger.debug("token_pair_created", user_id=user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=get_access_token_expire_seconds(),
    )


# ── Token Yenileme ──────────────────────────────────────


async def refresh_access_token(
    db: AsyncIOMotorDatabase,
    refresh_token_str: str,
) -> TokenResponse:
    """
    Refresh token kullanarak yeni bir token çifti oluştur.

    Refresh Token Rotation uygulanır:
      1. Eski refresh token revoke edilir
      2. Yeni bir refresh token oluşturulur
      3. Yeni access token oluşturulur

    Bu sayede çalınan bir refresh token ile
    yapılan ilk kullanımda, gerçek kullanıcının
    sonraki isteği başarısız olur ve saldırı tespit edilir.

    Args:
        db: MongoDB database instance.
        refresh_token_str: Mevcut refresh token.

    Returns:
        Yeni TokenResponse.

    Raises:
        UnauthorizedException: Token geçersiz, revoke edilmiş
            veya süresi dolmuşsa.
    """
    refresh_tokens = db[REFRESH_TOKENS_COLLECTION]
    users = db[USERS_COLLECTION]

    # Refresh token'ı bul
    token_doc = await refresh_tokens.find_one({"token": refresh_token_str})

    if not token_doc:
        raise UnauthorizedException("Geçersiz refresh token.")

    if token_doc.get("revoked"):
        # Token zaten revoke edilmiş — olası token hırsızlığı!
        # Güvenlik: Bu kullanıcının TÜM refresh token'larını revoke et
        logger.warning(
            "refresh_token_reuse_detected",
            user_id=token_doc["user_id"],
            token_hint=refresh_token_str[:10] + "...",
        )
        await refresh_tokens.update_many(
            {"user_id": token_doc["user_id"]},
            {"$set": {"revoked": True}},
        )
        raise UnauthorizedException(
            "Güvenlik ihlali tespit edildi. Lütfen tekrar giriş yapın."
        )

    # Süre kontrolü
    now = datetime.now(timezone.utc)
    if token_doc["expires_at"].replace(tzinfo=timezone.utc) < now:
        raise UnauthorizedException("Refresh token süresi dolmuş.")

    # Eski token'ı revoke et (rotation)
    await refresh_tokens.update_one(
        {"_id": token_doc["_id"]},
        {"$set": {"revoked": True}},
    )

    # Kullanıcıyı getir
    user = await users.find_one({"_id": ObjectId(token_doc["user_id"])})
    if not user:
        raise UnauthorizedException("Kullanıcı bulunamadı.")

    if not user.get("is_active", True):
        raise UnauthorizedException("Hesabınız devre dışı bırakılmış.")

    # Yeni token çifti oluştur
    logger.info("token_refreshed", user_id=token_doc["user_id"])

    return await create_token_pair(
        db=db,
        user_id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
    )


# ── Çıkış ────────────────────────────────────────────────


async def logout_user(
    db: AsyncIOMotorDatabase,
    refresh_token_str: str,
    access_token_str: str,
) -> None:
    """
    Kullanıcıyı çıkış yaptır.

    1. Refresh token'ı revoke et (MongoDB)
    2. Access token'ı blacklist'e ekle (memory/Redis)

    Args:
        db: MongoDB database instance.
        refresh_token_str: Revoke edilecek refresh token.
        access_token_str: Blacklist'e eklenecek access token.
    """
    refresh_tokens = db[REFRESH_TOKENS_COLLECTION]

    # Refresh token'ı revoke et
    result = await refresh_tokens.update_one(
        {"token": refresh_token_str, "revoked": False},
        {"$set": {"revoked": True}},
    )

    if result.modified_count > 0:
        logger.info(
            "refresh_token_revoked",
            token_hint=refresh_token_str[:10] + "...",
        )

    # Access token'ı blacklist'e ekle
    # (Token'ın kalan ömrü kadar blacklist'te tutulur)
    await token_blacklist.add(
        access_token_str,
        expires_in=get_access_token_expire_seconds(),
    )

    logger.info("user_logged_out")


# ── Kullanıcı Getirme ───────────────────────────────────


async def get_user_by_id(
    db: AsyncIOMotorDatabase,
    user_id: str,
) -> UserResponse | None:
    """
    ID ile kullanıcı bilgisini getir.

    Args:
        db: MongoDB database instance.
        user_id: Kullanıcının MongoDB _id'si (string).

    Returns:
        UserResponse veya None.
    """
    users = db[USERS_COLLECTION]

    try:
        user = await users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None

    if not user:
        return None

    return UserResponse(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        auth_provider=user.get("auth_provider", "local"),
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
    )
