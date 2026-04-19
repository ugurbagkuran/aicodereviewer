"""
GitHub modülü — Public repo clone ve proje import.

Endpoint:
  POST /api/v1/github/clone → Public repo'yu clone edip
                               container'a kopyalar.

Akış:
  1. Public repo URL'i al
  2. gitpython ile temp dizine clone et
  3. Dosyaları sidecar API üzerinden container'a kopyala
  4. RAG indexlemeyi tetikle (ileride)
  5. Dosya summary'lerini oluştur (ileride)
  6. Temp dizini temizle
"""
