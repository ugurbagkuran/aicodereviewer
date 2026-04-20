"""
Agent memory — Dosya özetleri.

Her dosyanın ne yaptığının kısa özetini oluşturur ve
MongoDB'de saklar. Agent'ın context window'unu verimli
kullanmasını sağlar.

MongoDB koleksiyonu (file_summaries):
  - project_id, file_path
  - summary (dosyanın ne yaptığının kısa özeti)
  - embedding_id (Qdrant'taki ID)
  - last_updated
"""

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

logger = structlog.get_logger(__name__)

FILE_SUMMARIES_COLLECTION = "file_summaries"


async def get_file_summaries(
    db: AsyncIOMotorDatabase,
    project_id: str,
) -> list[dict]:
    """
    Projedeki tüm dosya özetlerini getir.

    Args:
        db: MongoDB database instance.
        project_id: Proje ID'si.

    Returns:
        [{file_path: str, summary: str}, ...]
    """
    cursor = db[FILE_SUMMARIES_COLLECTION].find(
        {"project_id": project_id},
        {"_id": 0, "file_path": 1, "summary": 1},
    )
    return await cursor.to_list(length=500)


async def upsert_file_summary(
    db: AsyncIOMotorDatabase,
    project_id: str,
    file_path: str,
    summary: str,
    embedding_id: str | None = None,
) -> None:
    """
    Dosya özetini ekle veya güncelle (upsert).

    Args:
        db: MongoDB database instance.
        project_id: Proje ID'si.
        file_path: Dosyanın yolu.
        summary: Dosyanın ne yaptığının kısa özeti.
        embedding_id: Qdrant'taki embedding ID'si.
    """
    await db[FILE_SUMMARIES_COLLECTION].update_one(
        {"project_id": project_id, "file_path": file_path},
        {"$set": {
            "summary": summary,
            "embedding_id": embedding_id,
            "last_updated": datetime.now(timezone.utc),
        }},
        upsert=True,
    )

    logger.debug(
        "file_summary_upserted",
        project_id=project_id,
        file_path=file_path,
    )


async def delete_file_summary(
    db: AsyncIOMotorDatabase,
    project_id: str,
    file_path: str,
) -> None:
    """Dosya özetini sil."""
    await db[FILE_SUMMARIES_COLLECTION].delete_one(
        {"project_id": project_id, "file_path": file_path}
    )


async def delete_project_summaries(
    db: AsyncIOMotorDatabase,
    project_id: str,
) -> None:
    """Projenin tüm dosya özetlerini sil."""
    result = await db[FILE_SUMMARIES_COLLECTION].delete_many(
        {"project_id": project_id}
    )
    logger.info(
        "project_summaries_deleted",
        project_id=project_id,
        count=result.deleted_count,
    )
