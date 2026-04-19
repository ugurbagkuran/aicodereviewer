"""
Auth modülü — Kullanıcı kimlik doğrulama ve yetkilendirme.

Endpoint'ler:
  POST /api/v1/auth/register  → Yeni kullanıcı kaydı
  POST /api/v1/auth/login     → Giriş (access + refresh token)
  POST /api/v1/auth/refresh   → Access token yenileme
  POST /api/v1/auth/logout    → Çıkış (token revoke)
  GET  /api/v1/auth/me        → Mevcut kullanıcı bilgisi

Özellikler:
  - JWT tabanlı access token (30 dk)
  - Refresh token rotation (30 gün, MongoDB)
  - Password hashing (bcrypt)
  - Token blacklist (Redis-swappable)
  - Rate limiting (auth endpoint'leri)
  - auth_provider alanı (ileride OAuth için hazır)
"""
