"""
Containers modülü — Kubernetes işlemleri.

ŞU AN STUB IMPLEMENTASYON.
Gerçek Kubernetes Python client entegrasyonu ileride yapılacak.

Her fonksiyon şu anki haliyle:
  - Loglama yapar
  - Kısa bir gecikme simüle eder
  - Başarılı sonuç döner

Gerçek implementasyonda:
  - kubernetes.client kullanarak API çağrısı yapar
  - Namespace, Deployment, Service, Ingress oluşturur/siler
  - Pod durumunu izler
"""

import asyncio

import structlog

from core.config import settings

logger = structlog.get_logger(__name__)


async def create_pod(
    project_id: str,
    namespace: str,
) -> dict:
    """
    STUB: Proje için Kubernetes pod (Deployment + Service + Ingress) oluştur.

    Gerçek implementasyonda:
      1. Namespace oluştur
      2. Deployment oluştur (ana container + sidecar)
         - Ana container: kullanıcı projesi
         - Sidecar: dosya/komut API'si
      3. Service oluştur (internal ClusterIP)
      4. Ingress oluştur (subdomain routing)

    Args:
        project_id: Proje ID'si.
        namespace: Kubernetes namespace adı.

    Returns:
        Pod bilgileri dict'i.
    """
    logger.info(
        "stub_create_pod",
        project_id=project_id,
        namespace=namespace,
        cpu_request=settings.POD_CPU_REQUEST,
        cpu_limit=settings.POD_CPU_LIMIT,
        memory_request=settings.POD_MEMORY_REQUEST,
        memory_limit=settings.POD_MEMORY_LIMIT,
    )

    # Kubernetes API çağrısını simüle et
    await asyncio.sleep(0.5)

    preview_url = f"http://project-{project_id}.{settings.BASE_DOMAIN}"

    return {
        "namespace": namespace,
        "deployment_name": f"project-{project_id}",
        "service_name": f"project-{project_id}-svc",
        "ingress_name": f"project-{project_id}-ingress",
        "preview_url": preview_url,
    }


async def delete_pod(
    project_id: str,
    namespace: str,
) -> bool:
    """
    STUB: Proje pod'unu (Deployment + Service + Ingress + Namespace) sil.

    Gerçek implementasyonda:
      1. Ingress sil
      2. Service sil
      3. Deployment sil
      4. Namespace sil (tüm kaynakları temizler)

    Args:
        project_id: Proje ID'si.
        namespace: Kubernetes namespace adı.

    Returns:
        True ise başarılı.
    """
    logger.info(
        "stub_delete_pod",
        project_id=project_id,
        namespace=namespace,
    )

    # Kubernetes API çağrısını simüle et
    await asyncio.sleep(0.3)

    return True


async def get_pod_status(
    project_id: str,
    namespace: str,
) -> str:
    """
    STUB: Pod'un çalışma durumunu kontrol et.

    Gerçek implementasyonda:
      - Pod phase'ini kontrol et (Pending, Running, Failed, etc.)
      - Container status'lerini kontrol et

    Args:
        project_id: Proje ID'si.
        namespace: Kubernetes namespace adı.

    Returns:
        Pod durumu string'i ("running", "pending", "failed", "not_found").
    """
    logger.debug(
        "stub_get_pod_status",
        project_id=project_id,
        namespace=namespace,
    )

    # Stub: her zaman "running" dön
    return "running"


async def get_active_pod_count() -> int:
    """
    STUB: Cluster'daki aktif pod sayısını döndür.

    Gerçek implementasyonda:
      - Tüm project-* namespace'lerindeki pod'ları say
      - Veya MongoDB'deki running durumundaki proje sayısını kullan

    Returns:
        Aktif pod sayısı.
    """
    logger.debug("stub_get_active_pod_count")

    # Stub: MongoDB'den sayılacak (service.py'de yapılıyor)
    return 0
