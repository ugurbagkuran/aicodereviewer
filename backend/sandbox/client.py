"""
Sandbox modülü — Sidecar API HTTP Client.

Container içinde çalışan sidecar FastAPI servisine
httpx ile async HTTP istekleri gönderir.

Kubernetes içinde sidecar URL:
  http://project-{id}-svc.project-{id}.svc.cluster.local:8080

Kullanım:
    from sandbox.client import SandboxClient

    client = SandboxClient(project_id="abc123")
    files = await client.list_files("/src")
    content = await client.read_file("/src/main.py")
    await client.write_file("/src/main.py", "print('hello')")
    result = await client.exec_command("npm install")
"""

import httpx
import structlog

from core.config import settings
from core.exceptions import BadRequestException, NotFoundException

logger = structlog.get_logger(__name__)


class SandboxClient:
    """
    Sidecar API ile iletişim kuran async HTTP client.

    Her proje için ayrı bir SandboxClient instance'ı oluşturulur.
    Kubernetes internal DNS ile sidecar servisine ulaşır.
    """

    def __init__(self, project_id: str) -> None:
        """
        Args:
            project_id: Hedef projenin ID'si.
        """
        self.project_id = project_id
        self.base_url = self._build_sidecar_url(project_id)
        self.timeout = httpx.Timeout(
            timeout=settings.SIDECAR_TIMEOUT,
            connect=5.0,
        )

    @staticmethod
    def _build_sidecar_url(project_id: str) -> str:
        """
        Kubernetes internal DNS üzerinden sidecar URL'i oluştur.

        Format:
          In-cluster:  http://{svc}.{ns}.svc.cluster.local:{port}
          Out-cluster: http://localhost:{port}  (dev mode)
        """
        prefix = settings.K8S_NAMESPACE_PREFIX
        port = settings.SIDECAR_PORT

        if settings.K8S_IN_CLUSTER:
            service = f"{prefix}{project_id}-svc"
            namespace = f"{prefix}{project_id}"
            return f"http://{service}.{namespace}.svc.cluster.local:{port}"
        else:
            # Development: localhost stub
            return f"http://localhost:{port}"

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict:
        """
        Sidecar'a HTTP isteği gönder.

        Args:
            method: HTTP metodu (GET, POST, DELETE).
            path: Endpoint path'i.
            **kwargs: httpx request parametreleri.

        Returns:
            Response JSON dict.

        Raises:
            BadRequestException: Sidecar erişilemezse veya hata dönerse.
        """
        url = f"{self.base_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, **kwargs)

                if response.status_code == 404:
                    raise NotFoundException(
                        f"Dosya veya kaynak bulunamadı: {path}"
                    )

                if response.status_code >= 400:
                    detail = response.text[:200]
                    raise BadRequestException(
                        f"Sidecar hatası ({response.status_code}): {detail}"
                    )

                return response.json()

        except httpx.ConnectError:
            logger.error(
                "sidecar_connection_failed",
                project_id=self.project_id,
                url=url,
            )
            raise BadRequestException(
                "Container'a bağlanılamıyor. "
                "Projenin çalışır durumda olduğundan emin olun."
            )
        except httpx.TimeoutException:
            logger.error(
                "sidecar_timeout",
                project_id=self.project_id,
                url=url,
            )
            raise BadRequestException(
                "Container yanıt vermedi (timeout). "
                "Lütfen tekrar deneyin."
            )
        except (NotFoundException, BadRequestException):
            raise
        except Exception as e:
            logger.error(
                "sidecar_unexpected_error",
                project_id=self.project_id,
                error=str(e),
            )
            raise BadRequestException(f"Sidecar iletişim hatası: {e}")

    # ── Dosya İşlemleri ──────────────────────────────────

    async def list_files(self, path: str = "/") -> dict:
        """
        Belirtilen dizindeki dosya ve klasörleri listele.

        Args:
            path: Dizin yolu (container içinde).

        Returns:
            {"path": "/src", "files": [...]}
        """
        logger.debug(
            "sandbox_list_files",
            project_id=self.project_id,
            path=path,
        )
        return await self._request("GET", "/files", params={"path": path})

    async def read_file(self, path: str) -> dict:
        """
        Dosya içeriğini oku.

        Args:
            path: Dosya yolu.

        Returns:
            {"path": "...", "content": "...", "size": 123}
        """
        logger.debug(
            "sandbox_read_file",
            project_id=self.project_id,
            path=path,
        )
        return await self._request(
            "GET", "/files/read", params={"path": path}
        )

    async def write_file(self, path: str, content: str) -> dict:
        """
        Dosya yaz veya oluştur.

        Args:
            path: Dosya yolu.
            content: Dosya içeriği.

        Returns:
            Sidecar response dict.
        """
        logger.debug(
            "sandbox_write_file",
            project_id=self.project_id,
            path=path,
            content_length=len(content),
        )
        return await self._request(
            "POST",
            "/files/write",
            json={"path": path, "content": content},
        )

    async def delete_file(self, path: str) -> dict:
        """
        Dosya sil.

        Args:
            path: Silinecek dosya yolu.

        Returns:
            Sidecar response dict.
        """
        logger.debug(
            "sandbox_delete_file",
            project_id=self.project_id,
            path=path,
        )
        return await self._request(
            "DELETE",
            "/files/delete",
            json={"path": path},
        )

    # ── Komut Çalıştırma ────────────────────────────────

    async def exec_command(
        self,
        command: str,
        timeout: int = 30,
    ) -> dict:
        """
        Shell komutu çalıştır.

        Args:
            command: Çalıştırılacak komut.
            timeout: Komut timeout süresi (saniye).

        Returns:
            {"command": "...", "exit_code": 0, "stdout": "...", "stderr": "..."}
        """
        logger.info(
            "sandbox_exec_command",
            project_id=self.project_id,
            command=command[:100],
        )
        return await self._request(
            "POST",
            "/exec",
            json={"command": command, "timeout": timeout},
        )

    # ── Log ve Servis ────────────────────────────────────

    async def get_logs(self, lines: int = 50) -> dict:
        """
        Uygulama loglarını getir.

        Args:
            lines: Son kaç satır log getirileceği.

        Returns:
            {"logs": "...", "lines": 50}
        """
        return await self._request(
            "GET", "/logs", params={"lines": lines}
        )

    async def restart_service(self) -> dict:
        """
        Container içindeki uygulamayı yeniden başlat.

        Returns:
            {"success": true, "message": "..."}
        """
        logger.info(
            "sandbox_restart_service",
            project_id=self.project_id,
        )
        return await self._request("POST", "/restart")
