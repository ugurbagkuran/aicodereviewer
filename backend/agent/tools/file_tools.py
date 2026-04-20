"""
Agent modülü — Tool tanımları: Dosya işlemleri.

Sidecar API üzerinden container içindeki dosyaları
okur, yazar ve siler. LangGraph agent bu tool'ları kullanır.
"""

from langchain_core.tools import tool
import structlog

from sandbox.client import SandboxClient

logger = structlog.get_logger(__name__)


@tool
async def read_file(project_id: str, path: str) -> str:
    """
    Container içindeki bir dosyanın içeriğini oku.

    Args:
        project_id: Proje ID'si.
        path: Okunacak dosya yolu (ör: src/main.py).

    Returns:
        Dosya içeriği.
    """
    client = SandboxClient(project_id)
    result = await client.read_file(path)
    logger.debug("tool_read_file", project_id=project_id, path=path)
    return result.get("content", "")


@tool
async def write_file(project_id: str, path: str, content: str) -> str:
    """
    Container içine dosya yaz veya mevcut dosyayı güncelle.
    Gerekli dizinler otomatik oluşturulur.

    Args:
        project_id: Proje ID'si.
        path: Yazılacak dosya yolu (ör: src/utils.py).
        content: Dosyanın tam içeriği.

    Returns:
        İşlem sonucu mesajı.
    """
    client = SandboxClient(project_id)
    await client.write_file(path, content)
    logger.info(
        "tool_write_file",
        project_id=project_id,
        path=path,
        size=len(content),
    )
    return f"Dosya yazıldı: {path} ({len(content)} karakter)"


@tool
async def delete_file(project_id: str, path: str) -> str:
    """
    Container içindeki bir dosyayı sil.

    Args:
        project_id: Proje ID'si.
        path: Silinecek dosya yolu.

    Returns:
        İşlem sonucu mesajı.
    """
    client = SandboxClient(project_id)
    await client.delete_file(path)
    logger.info("tool_delete_file", project_id=project_id, path=path)
    return f"Dosya silindi: {path}"


@tool
async def list_files(project_id: str, directory: str = "/") -> str:
    """
    Container içindeki bir dizindeki dosya ve klasörleri listele.

    Args:
        project_id: Proje ID'si.
        directory: Listelenecek dizin yolu (varsayılan: kök dizin).

    Returns:
        Dosya ve klasör listesi (metin formatında).
    """
    client = SandboxClient(project_id)
    result = await client.list_files(directory)
    files = result.get("files", [])

    # Okunabilir format
    output_lines = [f"📁 {directory}"]
    for f in files:
        icon = "📂" if f.get("is_dir") else "📄"
        size = f.get("size", "")
        size_str = f" ({size} bytes)" if size else ""
        output_lines.append(f"  {icon} {f['name']}{size_str}")

    logger.debug(
        "tool_list_files",
        project_id=project_id,
        directory=directory,
        count=len(files),
    )
    return "\n".join(output_lines)
