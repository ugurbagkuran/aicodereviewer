"""
Projects modülü — Proje CRUD ve container yaşam döngüsü.

Endpoint'ler:
  POST   /api/v1/projects              → Yeni proje oluştur (sadece DB)
  GET    /api/v1/projects              → Kullanıcının projeleri
  GET    /api/v1/projects/{id}         → Proje detayı
  PATCH  /api/v1/projects/{id}         → Proje adı güncelle
  DELETE /api/v1/projects/{id}         → Projeyi sil
  POST   /api/v1/projects/{id}/start   → Container başlat
  POST   /api/v1/projects/{id}/stop    → Container durdur

Durum Akışı:
  created → starting → running → stopping → stopped
                                          → error
"""
