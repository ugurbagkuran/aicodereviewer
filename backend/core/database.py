"""
MongoDB Atlas async bağlantı yöneticisi.

Motor (async driver) kullanarak MongoDB Atlas'a bağlanır.
Uygulama yaşam döngüsüne entegre çalışır:
  - Startup'ta connect()
  - Shutdown'da disconnect()

Kullanım:
    from core.database import Database, get_database

    # FastAPI dependency olarak
    db = Depends(get_database)

    # Doğrudan koleksiyon erişimi
    db = Database.get_db()
    users = db["users"]
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import structlog

from core.config import settings

logger = structlog.get_logger(__name__)


class Database:
    """
    MongoDB Atlas bağlantı yöneticisi.

    Singleton pattern ile tek bir client instance'ı üzerinden
    tüm uygulama çalışır. Connection pooling Motor tarafından
    otomatik yönetilir.
    """

    client: AsyncIOMotorClient | None = None

    @classmethod
    async def connect(cls) -> None:
        """
        MongoDB Atlas'a bağlan ve bağlantıyı doğrula.

        Raises:
            ConnectionError: Atlas'a ulaşılamazsa.
        """
        # URI'nin tamamını loglamıyoruz (güvenlik)
        masked_uri = settings.MONGODB_URI[:30] + "..."
        logger.info("mongodb_connecting", uri=masked_uri)

        cls.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            # Atlas için önerilen ayarlar
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True,
        )

        # Bağlantıyı test et
        try:
            await cls.client.admin.command("ping")
            logger.info(
                "mongodb_connected",
                db=settings.MONGODB_DB_NAME,
                pool_size=50,
            )
        except Exception as e:
            logger.error("mongodb_connection_failed", error=str(e))
            raise ConnectionError(f"MongoDB Atlas'a bağlanılamadı: {e}") from e

    @classmethod
    async def disconnect(cls) -> None:
        """MongoDB bağlantısını güvenle kapat."""
        if cls.client:
            cls.client.close()
            cls.client = None
            logger.info("mongodb_disconnected")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """
        Database instance'ını döndür.

        Returns:
            AsyncIOMotorDatabase: Aktif database referansı.

        Raises:
            RuntimeError: Bağlantı henüz kurulmadıysa.
        """
        if cls.client is None:
            raise RuntimeError(
                "MongoDB bağlantısı henüz kurulmadı. "
                "Database.connect() çağrılmalı."
            )
        return cls.client[settings.MONGODB_DB_NAME]


def get_database() -> AsyncIOMotorDatabase:
    """
    FastAPI Depends() ile kullanılacak dependency.

    Kullanım:
        @router.get("/items")
        async def get_items(db = Depends(get_database)):
            items = await db["items"].find().to_list(100)
    """
    return Database.get_db()
