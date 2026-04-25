"""
Projects modülü — İş mantığı (business logic).

Proje CRUD operasyonları ve container yaşam döngüsü
burada yönetilir. Router bu fonksiyonları çağırır.

Fonksiyonlar:
  - ensure_indexes()         → MongoDB indekslerini oluştur
  - create_project()         → Yeni proje (sadece DB)
  - list_user_projects()     → Kullanıcının projeleri
  - get_project()            → Proje detayı (ownership kontrolü)
  - update_project()         → Proje adı güncelle
  - delete_project()         → Proje sil (+ k8s cleanup)
  - start_project()          → Container başlat
  - stop_project()           → Container durdur
  - update_last_activity()   → Idle timeout için aktivite güncelle
  - check_cluster_capacity() → Cluster kapasite kontrolü
  - idle_pod_checker()       → Background: idle pod'ları durdur
"""

import asyncio
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

from containers.service import create_pod, delete_pod
from core.config import settings
from core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from projects.models import (
    CreateProjectRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectStatus,
    UpdateProjectRequest,
)

logger = structlog.get_logger(__name__)


# ── Koleksiyon İsmi ──────────────────────────────────────

PROJECTS_COLLECTION = "projects"


# ── MongoDB İndeksleri ───────────────────────────────────


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """
    Projects modülü için gerekli MongoDB indekslerini oluştur.

    İdempotent: birden fazla çağrılsa bile sorun çıkarmaz.
    """
    projects = db[PROJECTS_COLLECTION]

    # user_id ile hızlı listeleme
    await projects.create_index("user_id")
    # Status ile aktif pod sayımı
    await projects.create_index("status")
    # Idle timeout için bileşik indeks
    await projects.create_index([("status", 1), ("last_activity_at", 1)])

    logger.info("projects_indexes_ensured")


# ── Yardımcı: MongoDB doc → Response ────────────────────


def _doc_to_response(doc: dict) -> ProjectResponse:
    """MongoDB dokümanını ProjectResponse'a dönüştür."""
    return ProjectResponse(
        id=str(doc["_id"]),
        user_id=doc["user_id"],
        name=doc["name"],
        status=doc["status"],
        preview_url=doc.get("preview_url"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


# ── Yardımcı: Ownership Kontrolü ────────────────────────


async def _get_project_with_ownership(
    db: AsyncIOMotorDatabase,
    project_id: str,
    user_id: str,
) -> dict:
    """
    Proje getir ve sahiplik kontrolü yap.

    Raises:
        NotFoundException: Proje bulunamazsa.
        ForbiddenException: Kullanıcı proje sahibi değilse.
    """
    try:
        doc = await db[PROJECTS_COLLECTION].find_one(
            {"_id": ObjectId(project_id)}
        )
    except Exception:
        raise NotFoundException("Proje bulunamadı.")

    if not doc:
        raise NotFoundException("Proje bulunamadı.")

    if doc["user_id"] != user_id:
        raise ForbiddenException("Bu proje size ait değil.")

    return doc


# ═══════════════════════════════════════════════════════
# CRUD İŞLEMLERİ
# ═══════════════════════════════════════════════════════


async def create_project(
    db: AsyncIOMotorDatabase,
    user_id: str,
    data: CreateProjectRequest,
) -> ProjectResponse:
    """
    Yeni proje oluştur (sadece MongoDB kaydı).

    Container başlatmak için ayrıca start_project() çağrılmalı.

    Args:
        db: MongoDB database instance.
        user_id: Proje sahibi kullanıcı ID'si.
        data: Proje oluşturma verisi.

    Returns:
        Oluşturulan projenin bilgisi.
    """
    now = datetime.now(timezone.utc)

    project_doc = {
        "user_id": user_id,
        "name": data.name,
        "status": ProjectStatus.CREATED.value,
        "preview_url": None,
        "last_activity_at": now,
        "created_at": now,
        "updated_at": now,
    }

    result = await db[PROJECTS_COLLECTION].insert_one(project_doc)
    project_doc["_id"] = result.inserted_id

    logger.info(
        "project_created",
        project_id=str(result.inserted_id),
        user_id=user_id,
        name=data.name,
    )

    return _doc_to_response(project_doc)


async def list_user_projects(
    db: AsyncIOMotorDatabase,
    user_id: str,
) -> ProjectListResponse:
    """
    Kullanıcının tüm projelerini listele.

    Args:
        db: MongoDB database instance.
        user_id: Kullanıcı ID'si.

    Returns:
        Proje listesi ve toplam sayısı.
    """
    cursor = db[PROJECTS_COLLECTION].find(
        {"user_id": user_id}
    ).sort("created_at", -1)

    projects = []
    async for doc in cursor:
        projects.append(_doc_to_response(doc))

    return ProjectListResponse(
        projects=projects,
        total=len(projects),
    )


async def get_project(
    db: AsyncIOMotorDatabase,
    project_id: str,
    user_id: str,
) -> ProjectResponse:
    """
    Proje detayını getir (ownership kontrolü ile).

    Args:
        db: MongoDB database instance.
        project_id: Proje ID'si.
        user_id: İstek yapan kullanıcı ID'si.

    Returns:
        Proje bilgisi.

    Raises:
        NotFoundException: Proje bulunamazsa.
        ForbiddenException: Yetki yoksa.
    """
    doc = await _get_project_with_ownership(db, project_id, user_id)
    return _doc_to_response(doc)


async def update_project(
    db: AsyncIOMotorDatabase,
    project_id: str,
    user_id: str,
    data: UpdateProjectRequest,
) -> ProjectResponse:
    """
    Proje adını güncelle.

    Args:
        db: MongoDB database instance.
        project_id: Proje ID'si.
        user_id: İstek yapan kullanıcı ID'si.
        data: Güncelleme verisi.

    Returns:
        Güncellenmiş proje bilgisi.
    """
    await _get_project_with_ownership(db, project_id, user_id)

    now = datetime.now(timezone.utc)

    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"name": data.name, "updated_at": now}},
    )

    logger.info(
        "project_updated",
        project_id=project_id,
        new_name=data.name,
    )

    # Güncellenmiş dokümanı getir
    updated_doc = await db[PROJECTS_COLLECTION].find_one(
        {"_id": ObjectId(project_id)}
    )
    return _doc_to_response(updated_doc)


async def delete_project(
    db: AsyncIOMotorDatabase,
    project_id: str,
    user_id: str,
) -> None:
    """
    Projeyi sil.

    Eğer container çalışıyorsa önce durdurulur,
    ardından MongoDB kaydı ve ilişkili veriler silinir.

    Args:
        db: MongoDB database instance.
        project_id: Proje ID'si.
        user_id: İstek yapan kullanıcı ID'si.

    Raises:
        NotFoundException: Proje bulunamazsa.
        ForbiddenException: Yetki yoksa.
    """
    doc = await _get_project_with_ownership(db, project_id, user_id)

    # Çalışıyorsa önce durdur
    if doc["status"] in (
        ProjectStatus.RUNNING.value,
        ProjectStatus.STARTING.value,
    ):
        logger.info("stopping_before_delete", project_id=project_id)
        await _stop_container(db, project_id)

    # Proje kaydını sil
    await db[PROJECTS_COLLECTION].delete_one({"_id": ObjectId(project_id)})

    # İlişkili verileri temizle
    # (agent_sessions, file_summaries vb. — modüller eklendikçe burayı genişlet)
    for collection_name in ("agent_sessions", "file_summaries"):
        await db[collection_name].delete_many({"project_id": project_id})

    logger.info("project_deleted", project_id=project_id, user_id=user_id)


# ═══════════════════════════════════════════════════════
# CONTAINER YAŞAM DÖNGÜSÜ
# ═══════════════════════════════════════════════════════


async def check_cluster_capacity(db: AsyncIOMotorDatabase) -> None:
    """
    Cluster'ın yeni pod kabul edip edemeyeceğini kontrol et.

    Aktif pod sayısı MAX_ACTIVE_PODS'u geçtiyse
    503 Service Unavailable fırlatır.

    Raises:
        BadRequestException: Kapasite doluysa (503 olarak override edilir).
    """
    active_count = await db[PROJECTS_COLLECTION].count_documents(
        {"status": {"$in": [
            ProjectStatus.STARTING.value,
            ProjectStatus.RUNNING.value,
        ]}}
    )

    if active_count >= settings.MAX_ACTIVE_PODS:
        logger.warning(
            "cluster_capacity_full",
            active_pods=active_count,
            max_pods=settings.MAX_ACTIVE_PODS,
        )
        raise BadRequestException(
            message=(
                f"Sistem kapasitesi dolu. "
                f"Aktif pod: {active_count}/{settings.MAX_ACTIVE_PODS}. "
                f"Lütfen daha sonra tekrar deneyin."
            ),
            error="capacity_full",
        )

    logger.debug(
        "cluster_capacity_ok",
        active_pods=active_count,
        max_pods=settings.MAX_ACTIVE_PODS,
    )


async def check_user_pod_limit(
    db: AsyncIOMotorDatabase,
    user_id: str,
) -> None:
    """
    Kullanıcının aktif pod limitini kontrol et.

    MAX_PODS_PER_USER = 0 ise kontrol atlanır (sınırsız).
    İleride Redis ile birlikte per-user limit aktif edilecek.

    Raises:
        BadRequestException: Limit aşılmışsa.
    """
    if settings.MAX_PODS_PER_USER <= 0:
        return  # Sınırsız mod

    user_active_count = await db[PROJECTS_COLLECTION].count_documents({
        "user_id": user_id,
        "status": {"$in": [
            ProjectStatus.STARTING.value,
            ProjectStatus.RUNNING.value,
        ]},
    })

    if user_active_count >= settings.MAX_PODS_PER_USER:
        logger.warning(
            "user_pod_limit_reached",
            user_id=user_id,
            active_pods=user_active_count,
            max_pods=settings.MAX_PODS_PER_USER,
        )
        raise BadRequestException(
            message=(
                f"Aktif proje limitinize ulaştınız. "
                f"({user_active_count}/{settings.MAX_PODS_PER_USER}). "
                f"Başka bir projeyi durdurduktan sonra tekrar deneyin."
            ),
            error="user_pod_limit_reached",
        )


async def start_project(
    db: AsyncIOMotorDatabase,
    project_id: str,
    user_id: str,
) -> ProjectResponse:
    """
    Proje container'ını başlat.

    Akış:
      1. Proje ownership kontrolü
      2. Status kontrolü (created veya stopped olmalı)
      3. Cluster kapasite kontrolü
      4. Kullanıcı pod limit kontrolü (altyapı hazır)
      5. Status → starting
      6. Kubernetes pod oluştur
      7. Status → running + preview_url ayarla
      8. Hata olursa status → error

    Args:
        db: MongoDB database instance.
        project_id: Başlatılacak proje ID'si.
        user_id: İstek yapan kullanıcı ID'si.

    Returns:
        Güncellenmiş proje bilgisi.

    Raises:
        BadRequestException: Status uygun değilse veya kapasite doluysa.
    """
    doc = await _get_project_with_ownership(db, project_id, user_id)

    # Status kontrolü
    if doc["status"] not in (
        ProjectStatus.CREATED.value,
        ProjectStatus.STOPPED.value,
        ProjectStatus.ERROR.value,
    ):
        raise BadRequestException(
            f"Proje '{doc['status']}' durumunda. "
            f"Sadece 'created', 'stopped' veya 'error' durumundaki projeler başlatılabilir."
        )

    # Kapasite kontrolleri
    await check_cluster_capacity(db)
    await check_user_pod_limit(db, user_id)

    now = datetime.now(timezone.utc)
    namespace = f"{settings.K8S_NAMESPACE_PREFIX}{project_id}"

    # Status → starting
    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {
            "status": ProjectStatus.STARTING.value,
            "updated_at": now,
        }},
    )

    try:
        # Kubernetes pod oluştur
        pod_info = await create_pod(
            project_id=project_id,
            namespace=namespace,
        )

        # Status → running
        await db[PROJECTS_COLLECTION].update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "status": ProjectStatus.RUNNING.value,
                "preview_url": pod_info["preview_url"],
                "last_activity_at": now,
                "updated_at": now,
            }},
        )

        logger.info(
            "project_started",
            project_id=project_id,
            preview_url=pod_info["preview_url"],
        )

    except Exception as e:
        # Hata → status error
        await db[PROJECTS_COLLECTION].update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "status": ProjectStatus.ERROR.value,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        logger.error(
            "project_start_failed",
            project_id=project_id,
            error=str(e),
        )
        raise BadRequestException(
            f"Container başlatılamadı: {e}"
        )

    updated = await db[PROJECTS_COLLECTION].find_one(
        {"_id": ObjectId(project_id)}
    )
    return _doc_to_response(updated)


async def _stop_container(
    db: AsyncIOMotorDatabase,
    project_id: str,
) -> None:
    """
    Internal: Container'ı durdur (ownership kontrolü YAPMAZ).

    delete_project ve idle_pod_checker tarafından kullanılır.
    """
    namespace = f"{settings.K8S_NAMESPACE_PREFIX}{project_id}"
    now = datetime.now(timezone.utc)

    # Status → stopping
    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {
            "status": ProjectStatus.STOPPING.value,
            "updated_at": now,
        }},
    )

    try:
        await delete_pod(
            project_id=project_id,
            namespace=namespace,
        )

        # Status → stopped
        await db[PROJECTS_COLLECTION].update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "status": ProjectStatus.STOPPED.value,
                "preview_url": None,
                "updated_at": datetime.now(timezone.utc),
            }},
        )

        logger.info("project_stopped", project_id=project_id)

    except Exception as e:
        await db[PROJECTS_COLLECTION].update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {
                "status": ProjectStatus.ERROR.value,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        logger.error(
            "project_stop_failed",
            project_id=project_id,
            error=str(e),
        )


async def stop_project(
    db: AsyncIOMotorDatabase,
    project_id: str,
    user_id: str,
) -> ProjectResponse:
    """
    Proje container'ını durdur.

    Akış:
      1. Proje ownership kontrolü
      2. Status kontrolü (running olmalı)
      3. Status → stopping
      4. Kubernetes pod sil
      5. Status → stopped + preview_url temizle

    Args:
        db: MongoDB database instance.
        project_id: Durdurulacak proje ID'si.
        user_id: İstek yapan kullanıcı ID'si.

    Returns:
        Güncellenmiş proje bilgisi.

    Raises:
        BadRequestException: Status uygun değilse.
    """
    doc = await _get_project_with_ownership(db, project_id, user_id)

    if doc["status"] != ProjectStatus.RUNNING.value:
        raise BadRequestException(
            f"Proje '{doc['status']}' durumunda. "
            f"Sadece 'running' durumundaki projeler durdurulabilir."
        )

    await _stop_container(db, project_id)

    updated = await db[PROJECTS_COLLECTION].find_one(
        {"_id": ObjectId(project_id)}
    )
    return _doc_to_response(updated)


# ── Aktivite Güncelleme ──────────────────────────────────


async def update_last_activity(
    db: AsyncIOMotorDatabase,
    project_id: str,
) -> None:
    """
    Projenin son aktivite zamanını güncelle.

    Agent tool çağrıları, dosya işlemleri vb. her
    etkileşimde çağrılır. Idle timeout sayacını sıfırlar.
    """
    await db[PROJECTS_COLLECTION].update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"last_activity_at": datetime.now(timezone.utc)}},
    )


# ═══════════════════════════════════════════════════════
# BACKGROUND TASK: IDLE POD CHECKER
# ═══════════════════════════════════════════════════════


async def idle_pod_checker() -> None:
    """
    Background task: Idle pod'ları otomatik durdur.

    Her 60 saniyede bir çalışır.
    IDLE_TIMEOUT_MINUTES süre boyunca aktivite olmayan
    running pod'ları otomatik durdurur.

    Uygulama lifespan'ında asyncio.create_task() ile başlatılır.
    """
    logger.info(
        "idle_pod_checker_started",
        interval_seconds=60,
        timeout_minutes=settings.IDLE_TIMEOUT_MINUTES,
    )

    while True:
        try:
            await asyncio.sleep(60)  # Her dakika kontrol et

            # Lazy import — circular import'u önle
            from core.database import Database

            db = Database.get_db()
            threshold = datetime.now(timezone.utc) - timedelta(
                minutes=settings.IDLE_TIMEOUT_MINUTES
            )

            # Idle pod'ları bul
            idle_cursor = db[PROJECTS_COLLECTION].find({
                "status": ProjectStatus.RUNNING.value,
                "last_activity_at": {"$lt": threshold},
            })

            idle_projects = await idle_cursor.to_list(length=100)

            if idle_projects:
                logger.info(
                    "idle_pods_found",
                    count=len(idle_projects),
                )

            for project in idle_projects:
                project_id = str(project["_id"])
                try:
                    await _stop_container(db, project_id)
                    logger.info(
                        "idle_pod_auto_stopped",
                        project_id=project_id,
                        idle_since=project["last_activity_at"].isoformat(),
                    )
                except Exception as e:
                    logger.error(
                        "idle_pod_stop_failed",
                        project_id=project_id,
                        error=str(e),
                    )

        except asyncio.CancelledError:
            logger.info("idle_pod_checker_stopped")
            break
        except Exception as e:
            # Checker asla crash etmemeli
            logger.error("idle_pod_checker_error", error=str(e))
            await asyncio.sleep(10)  # Hata sonrası kısa bekleme
