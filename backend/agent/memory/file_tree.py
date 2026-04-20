"""
Agent memory — Proje dosya ağacı.

Sidecar API üzerinden projenin dosya yapısını çeker
ve agent'a bağlam olarak sunar.
"""

import structlog

from sandbox.client import SandboxClient

logger = structlog.get_logger(__name__)


async def get_file_tree(
    project_id: str,
    root_path: str = "/",
    max_depth: int = 4,
) -> str:
    """
    Projenin dosya ağacını çek ve metin formatında döndür.

    Args:
        project_id: Proje ID'si.
        root_path: Başlangıç dizini.
        max_depth: Maksimum derinlik.

    Returns:
        tree formatında dosya ağacı string'i.
    """
    client = SandboxClient(project_id)
    tree_lines = []

    async def _walk(path: str, depth: int, prefix: str = "") -> None:
        if depth > max_depth:
            return

        try:
            result = await client.list_files(path)
        except Exception:
            return

        files = result.get("files", [])

        # Dizinleri önce, dosyaları sonra sırala
        dirs = sorted([f for f in files if f.get("is_dir")], key=lambda x: x["name"])
        regular = sorted([f for f in files if not f.get("is_dir")], key=lambda x: x["name"])
        items = dirs + regular

        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            icon = "📂" if item.get("is_dir") else ""

            tree_lines.append(f"{prefix}{connector}{icon}{item['name']}")

            if item.get("is_dir"):
                extension = "    " if is_last else "│   "
                child_path = f"{path.rstrip('/')}/{item['name']}"
                await _walk(child_path, depth + 1, prefix + extension)

    tree_lines.append(f"📁 {root_path}")
    await _walk(root_path, 1)

    logger.debug(
        "file_tree_fetched",
        project_id=project_id,
        total_entries=len(tree_lines),
    )

    return "\n".join(tree_lines)
