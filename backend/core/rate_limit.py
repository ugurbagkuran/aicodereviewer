"""
Rate limiting altyapısı (slowapi).

Şu an in-memory backend kullanır.
Redis'e geçiş için:
  1. .env'de USE_REDIS=true ve REDIS_URL ayarla
  2. Bu modül otomatik olarak Redis backend'e geçer

Kullanım (router'larda):
    from core.rate_limit import limiter
    from core.config import settings

    @router.post("/login")
    @limiter.limit(settings.RATE_LIMIT_AUTH)
    async def login(request: Request, ...):
        ...
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import structlog

from core.config import settings

logger = structlog.get_logger(__name__)


def _create_limiter() -> Limiter:
    """
    Rate limiter oluştur.

    USE_REDIS=True → Redis backend (production)
    USE_REDIS=False → In-memory backend (development)

    Redis'e geçiş için kod değişikliği gerekmez,
    sadece .env ayarları yeterli.
    """
    if settings.USE_REDIS:
        storage_uri = settings.REDIS_URL
        logger.info("rate_limiter_init", backend="redis")
    else:
        storage_uri = "memory://"
        logger.info("rate_limiter_init", backend="memory")

    return Limiter(
        key_func=get_remote_address,
        default_limits=[settings.RATE_LIMIT_DEFAULT],
        storage_uri=storage_uri,
    )


# Singleton limiter instance
limiter = _create_limiter()


async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    """
    Rate limit aşıldığında döndürülecek özel JSON response.

    429 Too Many Requests status kodu ile birlikte
    kullanıcıya anlamlı bir hata mesajı döner.
    """
    logger.warning(
        "rate_limit_exceeded",
        client_ip=get_remote_address(request),
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Çok fazla istek gönderdiniz. Lütfen biraz bekleyin.",
            "detail": str(exc),
        },
    )
