"""
JWT Token Blacklist yöneticisi.

Logout yapıldığında access token'ı blacklist'e ekler.
Token süresi dolana kadar blacklist'te tutulur.

Şu an in-memory dict kullanır.
Redis'e geçiş için:
  1. RedisTokenBlacklist sınıfını aktif et
  2. .env'de USE_REDIS=true yap
  3. Başka hiçbir değişiklik gerekmez

Kullanım:
    from core.token_blacklist import token_blacklist

    # Token'ı blacklist'e ekle (logout'ta)
    await token_blacklist.add(token, expires_in=1800)

    # Token blacklist'te mi kontrol et (her istekte)
    if await token_blacklist.is_blacklisted(token):
        raise HTTPException(401)
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

import structlog

logger = structlog.get_logger(__name__)


class TokenBlacklistBackend(ABC):
    """
    Token blacklist soyut sınıfı.

    Yeni bir backend (Redis, Memcached, vb.) eklemek için
    bu sınıfı implement et.
    """

    @abstractmethod
    async def add(self, token: str, expires_in: int) -> None:
        """
        Token'ı blacklist'e ekle.

        Args:
            token: Blacklist'e eklenecek JWT token.
            expires_in: Token'ın kaç saniye sonra süresi dolacak.
        """
        ...

    @abstractmethod
    async def is_blacklisted(self, token: str) -> bool:
        """
        Token'ın blacklist'te olup olmadığını kontrol et.

        Args:
            token: Kontrol edilecek JWT token.

        Returns:
            True ise token blacklist'te.
        """
        ...


class InMemoryTokenBlacklist(TokenBlacklistBackend):
    """
    In-memory token blacklist.

    Development ve küçük ölçekli deploy için uygundur.
    Uygulama restart'ında blacklist sıfırlanır.

    NOT: Production'da Redis backend tercih edilmeli.
    """

    def __init__(self) -> None:
        # {token: expiry_datetime} formatında
        self._blacklist: dict[str, datetime] = {}

    async def add(self, token: str, expires_in: int) -> None:
        expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        self._blacklist[token] = expiry
        self._cleanup()
        logger.debug("token_blacklisted", backend="memory")

    async def is_blacklisted(self, token: str) -> bool:
        self._cleanup()
        return token in self._blacklist

    def _cleanup(self) -> None:
        """Süresi geçmiş token'ları bellekten temizle."""
        now = datetime.now(timezone.utc)
        expired_tokens = [
            t for t, exp in self._blacklist.items() if exp < now
        ]
        for t in expired_tokens:
            del self._blacklist[t]


# ─── Redis Backend (ileride aktif edilecek) ──────────────
#
# class RedisTokenBlacklist(TokenBlacklistBackend):
#     """Redis tabanlı token blacklist. Production için önerilir."""
#
#     def __init__(self, redis_url: str) -> None:
#         import redis.asyncio as redis
#         self.redis = redis.from_url(redis_url)
#
#     async def add(self, token: str, expires_in: int) -> None:
#         await self.redis.setex(
#             f"token_blacklist:{token}", expires_in, "1"
#         )
#         logger.debug("token_blacklisted", backend="redis")
#
#     async def is_blacklisted(self, token: str) -> bool:
#         result = await self.redis.exists(f"token_blacklist:{token}")
#         return bool(result)
# ──────────────────────────────────────────────────────────


def _create_token_blacklist() -> TokenBlacklistBackend:
    """
    Config'e göre uygun blacklist backend'ini oluştur.

    USE_REDIS=True olduğunda RedisTokenBlacklist'i
    aktif etmek için bu fonksiyonu güncelle.
    """
    from core.config import settings

    if settings.USE_REDIS:
        # Redis backend aktif edildiğinde:
        # return RedisTokenBlacklist(settings.REDIS_URL)
        logger.warning(
            "redis_blacklist_not_yet_implemented",
            fallback="memory",
        )

    logger.info("token_blacklist_init", backend="memory")
    return InMemoryTokenBlacklist()


# Singleton — tüm uygulama bu instance'ı kullanır
token_blacklist = _create_token_blacklist()
