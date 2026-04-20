"""
Agent RAG — Embedding indexer.

Dosyaları chunk'lara böler, Google text-embedding-004
ile embed eder ve Qdrant'a yazar.

Her proje için ayrı bir Qdrant collection kullanılır.
Collection adı: project_{project_id}
"""

from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
import structlog

from core.config import settings

logger = structlog.get_logger(__name__)

# Embedding boyutu (text-embedding-004)
EMBEDDING_DIMENSION = 768
CHUNK_SIZE = 500  # token (yaklaşık)
CHUNK_OVERLAP = 50


def _get_qdrant_client() -> QdrantClient:
    """Qdrant client oluştur."""
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Metni satır bazlı chunk'lara böl.

    Token sayısı yerine karakter sayısı kullanılır
    (yaklaşık 1 token ≈ 4 karakter).
    """
    char_limit = chunk_size * 4  # yaklaşık token→karakter
    lines = text.split("\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        line_len = len(line) + 1  # +1 for newline
        if current_length + line_len > char_limit and current_chunk:
            chunks.append("\n".join(current_chunk))
            # Overlap: son birkaç satırı tut
            overlap_lines = current_chunk[-(CHUNK_OVERLAP // 10):]
            current_chunk = overlap_lines
            current_length = sum(len(l) + 1 for l in current_chunk)

        current_chunk.append(line)
        current_length += line_len

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


async def ensure_collection(project_id: str) -> None:
    """
    Proje için Qdrant collection'ı oluştur (yoksa).

    Args:
        project_id: Proje ID'si.
    """
    client = _get_qdrant_client()
    collection_name = f"project_{project_id}"

    try:
        client.get_collection(collection_name)
        logger.debug("qdrant_collection_exists", collection=collection_name)
    except (UnexpectedResponse, Exception):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=models.Distance.COSINE,
            ),
        )
        logger.info("qdrant_collection_created", collection=collection_name)


async def index_file(
    project_id: str,
    file_path: str,
    content: str,
    embed_func,
) -> list[str]:
    """
    Dosyayı chunk'lara böl, embed et ve Qdrant'a yaz.

    Args:
        project_id: Proje ID'si.
        file_path: Dosya yolu.
        content: Dosya içeriği.
        embed_func: Embedding fonksiyonu (text → vector).

    Returns:
        Oluşturulan Qdrant point ID'leri.
    """
    client = _get_qdrant_client()
    collection_name = f"project_{project_id}"

    # Eski chunk'ları sil (bu dosyaya ait)
    try:
        client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_path",
                            match=models.MatchValue(value=file_path),
                        )
                    ]
                )
            ),
        )
    except Exception:
        pass

    # Chunk'la
    chunks = _chunk_text(content)
    if not chunks:
        return []

    # Embed et
    embeddings = await embed_func(chunks)

    # Qdrant'a yaz
    import uuid

    point_ids = []
    points = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point_id = str(uuid.uuid4())
        point_ids.append(point_id)

        points.append(
            models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "project_id": project_id,
                    "file_path": file_path,
                    "chunk_index": i,
                    "content": chunk,
                },
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points,
    )

    logger.info(
        "file_indexed",
        project_id=project_id,
        file_path=file_path,
        chunks=len(chunks),
    )

    return point_ids


async def delete_file_index(
    project_id: str,
    file_path: str,
) -> None:
    """Dosyanın Qdrant'taki tüm chunk'larını sil."""
    client = _get_qdrant_client()
    collection_name = f"project_{project_id}"

    try:
        client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_path",
                            match=models.MatchValue(value=file_path),
                        )
                    ]
                )
            ),
        )
        logger.info("file_index_deleted", file_path=file_path)
    except Exception as e:
        logger.warning("file_index_delete_failed", error=str(e))


async def delete_project_index(project_id: str) -> None:
    """Projenin tüm Qdrant collection'ını sil."""
    client = _get_qdrant_client()
    collection_name = f"project_{project_id}"

    try:
        client.delete_collection(collection_name)
        logger.info("project_index_deleted", project_id=project_id)
    except Exception as e:
        logger.warning("project_index_delete_failed", error=str(e))
