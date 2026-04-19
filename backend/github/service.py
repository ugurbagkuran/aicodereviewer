"""
GitHub modülü — İş mantığı.

Public repo clone, dosya kopyalama ve
(ileride) RAG indexleme tetikleme.

Akış:
  1. gitpython ile temp dizine clone
  2. Dosya ağacını tara (exclude pattern'lere göre filtrele)
  3. Her dosyayı sidecar API üzerinden container'a yaz
  4. (ileride) RAG indexleme tetikle
  5. Temp dizini temizle
"""

import os
import shutil
import tempfile
from pathlib import Path

from git import Repo as GitRepo
from git.exc import GitCommandError, InvalidGitRepositoryError
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from core.config import settings
from core.exceptions import BadRequestException, NotFoundException
from github.models import CloneResponse
from projects.models import ProjectStatus
from sandbox.client import SandboxClient

logger = structlog.get_logger(__name__)

# ── Koleksiyon İsmi ──────────────────────────────────────

PROJECTS_COLLECTION = "projects"


def _should_exclude(path: str) -> bool:
    """
    Dosya/dizin yolunun exclude listesinde olup olmadığını kontrol et.

    Args:
        path: Kontrol edilecek yol (relative).

    Returns:
        True ise bu yol atlanmalı.
    """
    parts = Path(path).parts
    for part in parts:
        if part in settings.GITHUB_EXCLUDE_DIRS:
            return True
    return False


def _is_text_file(file_path: str) -> bool:
    """
    Dosyanın metin dosyası olup olmadığını basitçe kontrol et.

    Binary dosyaları atlamak için kullanılır.
    """
    text_extensions = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css",
        ".scss", ".sass", ".less", ".json", ".yaml", ".yml",
        ".toml", ".ini", ".cfg", ".conf", ".env", ".md",
        ".txt", ".rst", ".xml", ".svg", ".sh", ".bash",
        ".zsh", ".fish", ".ps1", ".bat", ".cmd", ".dockerfile",
        ".gitignore", ".editorconfig", ".eslintrc", ".prettierrc",
        ".vue", ".svelte", ".astro", ".go", ".rs", ".rb",
        ".java", ".kt", ".swift", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".php", ".r", ".sql", ".graphql", ".proto",
        ".tf", ".hcl", ".lock",
    }

    ext = Path(file_path).suffix.lower()
    name = Path(file_path).name.lower()

    # Uzantısız bilinen dosyalar
    known_names = {
        "makefile", "dockerfile", "procfile", "gemfile",
        "rakefile", "vagrantfile", ".gitignore", ".dockerignore",
        ".env.example", ".env.local", "license", "readme",
    }

    return ext in text_extensions or name in known_names


async def clone_repo_to_project(
    db: AsyncIOMotorDatabase,
    repo_url: str,
    project_id: str,
    user_id: str,
) -> CloneResponse:
    """
    Public GitHub repo'sunu clone edip projeye kopyala.

    Args:
        db: MongoDB database instance.
        repo_url: GitHub repo URL'i.
        project_id: Hedef proje ID'si.
        user_id: İstek yapan kullanıcı ID'si.

    Returns:
        Clone sonuç bilgisi.

    Raises:
        NotFoundException: Proje bulunamazsa.
        BadRequestException: Repo clone edilemezse veya proje uygun değilse.
    """
    from bson import ObjectId

    # Proje kontrolü
    project = await db[PROJECTS_COLLECTION].find_one(
        {"_id": ObjectId(project_id)}
    )
    if not project:
        raise NotFoundException("Proje bulunamadı.")

    if project["user_id"] != user_id:
        raise BadRequestException("Bu proje size ait değil.")

    if project["status"] not in (
        ProjectStatus.RUNNING.value,
        ProjectStatus.CREATED.value,
        ProjectStatus.STOPPED.value,
    ):
        raise BadRequestException(
            f"Proje '{project['status']}' durumunda. "
            f"Clone işlemi için proje 'running', 'created' veya 'stopped' olmalı."
        )

    # Proje running değilse sidecar'a ulaşamayız
    if project["status"] != ProjectStatus.RUNNING.value:
        raise BadRequestException(
            "Clone işlemi için projenin çalışıyor olması gerekir. "
            "Önce projeyi başlatın."
        )

    logger.info(
        "github_clone_start",
        repo_url=repo_url,
        project_id=project_id,
    )

    # Temp dizin oluştur
    temp_dir = tempfile.mkdtemp(prefix="github_clone_")

    try:
        # 1. Repo'yu clone et
        logger.info("github_cloning", repo_url=repo_url)

        try:
            GitRepo.clone_from(
                repo_url,
                temp_dir,
                depth=1,  # Shallow clone (hız için)
                no_checkout=False,
            )
        except GitCommandError as e:
            logger.error(
                "github_clone_failed",
                repo_url=repo_url,
                error=str(e),
            )
            raise BadRequestException(
                f"Repo clone edilemedi. "
                f"URL'in doğru ve repo'nun public olduğundan emin olun. "
                f"Hata: {str(e)[:200]}"
            )
        except InvalidGitRepositoryError:
            raise BadRequestException("Geçersiz Git repository.")

        # 2. Dosya ağacını tara ve container'a kopyala
        sandbox = SandboxClient(project_id)
        files_copied = 0
        files_skipped = 0

        for root, dirs, files in os.walk(temp_dir):
            # Exclude dizinleri filtreле
            rel_root = os.path.relpath(root, temp_dir)

            if _should_exclude(rel_root):
                dirs.clear()  # Alt dizinlere girme
                continue

            # Exclude dizinlerini dirs'den de çıkar (os.walk optimizasyonu)
            dirs[:] = [
                d for d in dirs
                if d not in settings.GITHUB_EXCLUDE_DIRS
            ]

            for file_name in files:
                abs_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(abs_path, temp_dir)

                # Exclude kontrolü
                if _should_exclude(rel_path):
                    files_skipped += 1
                    continue

                # Boyut kontrolü
                try:
                    file_size = os.path.getsize(abs_path)
                except OSError:
                    files_skipped += 1
                    continue

                if file_size > settings.GITHUB_MAX_FILE_SIZE:
                    logger.debug(
                        "github_file_too_large",
                        path=rel_path,
                        size=file_size,
                    )
                    files_skipped += 1
                    continue

                # Text dosya kontrolü
                if not _is_text_file(rel_path):
                    files_skipped += 1
                    continue

                # Dosyayı oku ve container'a yaz
                try:
                    with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # Path'i Unix formatına çevir
                    unix_path = rel_path.replace("\\", "/")
                    await sandbox.write_file(unix_path, content)
                    files_copied += 1

                    if files_copied % 20 == 0:
                        logger.info(
                            "github_copy_progress",
                            files_copied=files_copied,
                        )

                except Exception as e:
                    logger.warning(
                        "github_file_copy_failed",
                        path=rel_path,
                        error=str(e),
                    )
                    files_skipped += 1

        # 3. İleride: RAG indexleme tetikle
        # from agent.rag.indexer import index_project
        # await index_project(project_id)

        # 4. İleride: Dosya summary'lerini oluştur
        # from agent.memory.summary import generate_summaries
        # await generate_summaries(project_id)

        logger.info(
            "github_clone_complete",
            project_id=project_id,
            repo_url=repo_url,
            files_copied=files_copied,
            files_skipped=files_skipped,
        )

        return CloneResponse(
            project_id=project_id,
            repo_url=repo_url,
            files_copied=files_copied,
            files_skipped=files_skipped,
            message=(
                f"Repo başarıyla import edildi. "
                f"{files_copied} dosya kopyalandı, "
                f"{files_skipped} dosya atlandı."
            ),
        )

    finally:
        # Temp dizini temizle
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
