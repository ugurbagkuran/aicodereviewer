"""
Sandbox modülü — Sidecar API client.

Container içinde çalışan sidecar servisine HTTP istekleri gönderir.
Dosya okuma/yazma, komut çalıştırma ve servis yönetimi sağlar.

Sidecar Endpoint'leri:
  GET  /files?path=        → Dosya/klasör listesi
  GET  /files/read?path=   → Dosya içeriği oku
  POST /files/write        → Dosya yaz/oluştur
  DELETE /files/delete     → Dosya sil
  POST /exec               → Shell komutu çalıştır
  GET  /logs               → Uygulama logları
  POST /restart            → Servisi yeniden başlat
"""
