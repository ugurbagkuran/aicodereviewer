"""
Core modülü — Uygulama altyapısı.

Bu modül şunları içerir:
- config: Environment variable yönetimi (pydantic-settings)
- database: MongoDB Atlas async bağlantısı (Motor)
- logging: Structured JSON logging (structlog)
- rate_limit: Rate limiting (slowapi, Redis-swappable)
- token_blacklist: JWT blacklist (in-memory → Redis-swappable)
"""
