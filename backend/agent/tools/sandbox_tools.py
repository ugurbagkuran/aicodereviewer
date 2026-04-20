"""
Agent modülü — Tool tanımları: Sandbox / servis yönetimi.

Container servisinin yeniden başlatılması ve log okuma.
"""

from langchain_core.tools import tool
import structlog

from sandbox.client import SandboxClient

logger = structlog.get_logger(__name__)


@tool
async def restart_service(project_id: str) -> str:
    """
    Container içindeki uygulamayı yeniden başlat.
    Kod değişikliklerinin etkili olabilmesi için kullanılır.

    Args:
        project_id: Proje ID'si.

    Returns:
        Yeniden başlatma sonucu.
    """
    client = SandboxClient(project_id)
    result = await client.restart_service()

    logger.info("tool_restart_service", project_id=project_id)
    return result.get("message", "Servis yeniden başlatıldı.")


@tool
async def get_logs(project_id: str, lines: int = 50) -> str:
    """
    Container'daki uygulamanın son loglarını getir.
    Hata ayıklama ve durumu kontrol etmek için kullanılır.

    Args:
        project_id: Proje ID'si.
        lines: Son kaç satır log getirileceği (varsayılan: 50).

    Returns:
        Uygulama logları.
    """
    client = SandboxClient(project_id)
    result = await client.get_logs(lines=lines)

    logger.debug("tool_get_logs", project_id=project_id, lines=lines)
    return result.get("logs", "Log bulunamadı.")
