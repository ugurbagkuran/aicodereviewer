"""
Agent modülü — Tool tanımları: Komut çalıştırma.

Container içinde shell komutları çalıştırır.
npm install, pip install, test süitleri vb.
"""

from langchain_core.tools import tool
import structlog

from sandbox.client import SandboxClient

logger = structlog.get_logger(__name__)


@tool
async def run_command(
    project_id: str,
    command: str,
    timeout: int = 30,
) -> str:
    """
    Container içinde bir shell komutu çalıştır.

    Args:
        project_id: Proje ID'si.
        command: Çalıştırılacak komut (ör: npm install, python -m pytest).
        timeout: Komut timeout süresi saniye cinsinden (varsayılan: 30).

    Returns:
        Komutun stdout ve stderr çıktısı.
    """
    client = SandboxClient(project_id)
    result = await client.exec_command(command, timeout=timeout)

    exit_code = result.get("exit_code", -1)
    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")

    logger.info(
        "tool_run_command",
        project_id=project_id,
        command=command[:100],
        exit_code=exit_code,
    )

    output = f"Exit Code: {exit_code}\n"
    if stdout:
        output += f"--- STDOUT ---\n{stdout}\n"
    if stderr:
        output += f"--- STDERR ---\n{stderr}\n"

    return output
