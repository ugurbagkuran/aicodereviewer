"""
Structured JSON logging konfigürasyonu (structlog).

DEBUG=true  → Renkli, okunabilir konsol çıktısı (development)
DEBUG=false → JSON format (production, log aggregation uyumlu)

Kullanım:
    import structlog
    logger = structlog.get_logger(__name__)

    logger.info("user_created", user_id="abc123", email="x@y.com")
    logger.error("db_error", error=str(e), collection="users")
"""

import logging
import sys

import structlog


def setup_logging(debug: bool = False) -> None:
    """
    Uygulama genelinde logging'i ayarla.

    Args:
        debug: True ise renkli konsol, False ise JSON format.
    """
    log_level = logging.DEBUG if debug else logging.INFO

    # Tüm log processor'ları (her iki mod için ortak)
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if debug:
        # Development: renkli, okunabilir çıktı
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # Production: JSON — ELK, Loki, CloudWatch uyumlu
        renderer = structlog.processors.JSONRenderer()

    # structlog konfigürasyonu
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # stdlib logging formatter
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # Root handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Uvicorn ve FastAPI loglarını da structlog'a yönlendir
    for logger_name in (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
    ):
        named_logger = logging.getLogger(logger_name)
        named_logger.handlers.clear()
        named_logger.addHandler(handler)
        named_logger.propagate = False
