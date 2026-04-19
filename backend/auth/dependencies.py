"""
Auth modülü — FastAPI dependency'leri.

get_current_user: Tüm korumalı endpoint'lerde kullanılır.
Her istekte JWT token'ı doğrular ve kullanıcı bilgisini döndürür.

Kullanım:
    from auth.dependencies import get_current_user
    from auth.models import TokenPayload

    @router.get("/protected")
    async def protected_route(
        current_user: TokenPayload = Depends(get_current_user),
    ):
        return {"user_id": current_user.sub}
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import structlog

from auth.models import TokenPayload
from auth.utils import decode_access_token
from core.config import settings
from core.exceptions import UnauthorizedException
from core.token_blacklist import token_blacklist

logger = structlog.get_logger(__name__)

# OAuth2 şeması — Swagger UI'da "Authorize" butonu sağlar
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> TokenPayload:
    """
    JWT Bearer token'ı doğrula ve kullanıcı bilgisini döndür.

    Bu dependency korumalı endpoint'lere eklenir:
        @router.get("/me")
        async def me(user: TokenPayload = Depends(get_current_user)):
            ...

    Kontroller:
      1. Token blacklist'te mi? (logout kontrolü)
      2. JWT geçerli mi? (imza + süre)
      3. Token tipi "access" mi?

    Args:
        token: Authorization header'dan çıkarılan Bearer token.

    Returns:
        TokenPayload: Decode edilmiş kullanıcı bilgisi.

    Raises:
        UnauthorizedException: Token geçersiz, süresi dolmuş
            veya blacklist'te ise.
    """
    # 1. Blacklist kontrolü
    if await token_blacklist.is_blacklisted(token):
        logger.warning("blacklisted_token_used")
        raise UnauthorizedException("Token geçersiz kılınmış.")

    # 2. JWT decode + doğrulama
    try:
        payload = decode_access_token(token)
    except JWTError as e:
        logger.warning("invalid_token", error=str(e))
        raise UnauthorizedException("Geçersiz veya süresi dolmuş token.")

    # 3. Gerekli alanları kontrol et
    user_id = payload.get("sub")
    email = payload.get("email")
    username = payload.get("username")

    if not all([user_id, email, username]):
        raise UnauthorizedException("Token payload eksik.")

    return TokenPayload(
        sub=user_id,
        email=email,
        username=username,
        type=payload.get("type", "access"),
    )
