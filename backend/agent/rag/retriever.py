"""
Agent RAG — Semantic search (retriever).

Kullanıcı isteğini embed eder ve Qdrant'ta
en ilgili dosya chunk'larını bulur.
"""

from qdrant_client import QdrantClient, models
import structlog

from core.config import settings

logger = structlog.get_logger(__name__)


def _get_qdrant_client() -> QdrantClient:
    """Qdrant client oluştur."""
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )


async def search_relevant_chunks(
    project_id: str,
    query_embedding: list[float],
    top_k: int = 10,
) -> list[dict]:
    """
    Semantic search ile en ilgili dosya chunk'larını bul.

    Args:
        project_id: Proje ID'si.
        query_embedding: Kullanıcı isteğinin embedding vektörü.
        top_k: Döndürülecek maksimum sonuç sayısı.

    Returns:
        [{file_path, content, score, chunk_index}, ...]
    """
    client = _get_qdrant_client()
    collection_name = f"project_{project_id}"

    try:
        results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k,
        )
    except Exception as e:
        logger.warning(
            "qdrant_search_failed",
            project_id=project_id,
            error=str(e),
        )
        return []

    chunks = []
    for result in results:
        payload = result.payload or {}
        chunks.append({
            "file_path": payload.get("file_path", ""),
            "content": payload.get("content", ""),
            "chunk_index": payload.get("chunk_index", 0),
            "score": result.score,
        })

    logger.info(
        "rag_search_complete",
        project_id=project_id,
        results_count=len(chunks),
        top_score=chunks[0]["score"] if chunks else 0,
    )

    return chunks


async def get_relevant_files(
    project_id: str,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[str]:
    """
    Semantic search ile en ilgili dosya yollarını bul (unique).

    Args:
        project_id: Proje ID'si.
        query_embedding: Kullanıcı isteğinin embedding vektörü.
        top_k: Döndürülecek maksimum dosya sayısı.

    Returns:
        Benzersiz dosya yolları listesi.
    """
    # Daha fazla chunk getir ki unique dosya sayısı yeterli olsun
    chunks = await search_relevant_chunks(
        project_id, query_embedding, top_k=top_k * 3
    )

    seen = set()
    unique_files = []
    for chunk in chunks:
        fp = chunk["file_path"]
        if fp not in seen:
            seen.add(fp)
            unique_files.append(fp)
            if len(unique_files) >= top_k:
                break

    return unique_files
