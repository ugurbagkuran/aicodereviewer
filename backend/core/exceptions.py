"""
Uygulama genelinde kullanılan özel exception sınıfları.

Tüm modüller bu exception'ları fırlatır,
main.py'deki handler bunları yakalayıp tutarlı
JSON response döndürür.

Response formatı:
    {
        "error": "conflict",
        "message": "Bu email adresi zaten kayıtlı."
    }
"""

from fastapi import Request
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger(__name__)


class AppException(Exception):
    """Tüm uygulama exception'larının base sınıfı."""

    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
    ) -> None:
        self.status_code = status_code
        self.error = error
        self.message = message
        super().__init__(message)


class BadRequestException(AppException):
    """400 — Geçersiz istek."""

    def __init__(
        self,
        message: str = "Geçersiz istek.",
        error: str = "bad_request",
    ) -> None:
        super().__init__(400, error, message)


class UnauthorizedException(AppException):
    """401 — Kimlik doğrulama başarısız."""

    def __init__(
        self,
        message: str = "Kimlik doğrulama başarısız.",
        error: str = "unauthorized",
    ) -> None:
        super().__init__(401, error, message)


class ForbiddenException(AppException):
    """403 — Yetkisiz erişim."""

    def __init__(
        self,
        message: str = "Bu işlem için yetkiniz yok.",
        error: str = "forbidden",
    ) -> None:
        super().__init__(403, error, message)


class NotFoundException(AppException):
    """404 — Kaynak bulunamadı."""

    def __init__(
        self,
        message: str = "İstenen kaynak bulunamadı.",
        error: str = "not_found",
    ) -> None:
        super().__init__(404, error, message)


class ConflictException(AppException):
    """409 — Çakışma (ör: duplicate email/username)."""

    def __init__(
        self,
        message: str = "Bu kayıt zaten mevcut.",
        error: str = "conflict",
    ) -> None:
        super().__init__(409, error, message)


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """
    Tüm AppException'ları yakalayıp tutarlı JSON döndüren handler.

    main.py'de şu şekilde kayıt edilir:
        app.add_exception_handler(AppException, app_exception_handler)
    """
    logger.warning(
        "app_exception",
        status_code=exc.status_code,
        error=exc.error,
        message=exc.message,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error,
            "message": exc.message,
        },
    )
