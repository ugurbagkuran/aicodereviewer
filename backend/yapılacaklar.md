# AI-Powered Cloud Development Platform — Backend

## Proje Özeti
FastAPI ile yazılmış modüler bir monolitik backend. 
Kullanıcılar bu platform üzerinden:
- Sıfırdan full-stack proje oluşturabilir (AI agent yazar)
- GitHub public repo URL'i ile proje import edebilir
- Container içinde çalışan projeyi canlı preview URL'inden izleyebilir
- AI agent ile kod düzenlemeleri yapabilir

---

## Teknoloji Stack

- **Backend:** Python, FastAPI, async
- **AI Agent:** LangGraph + LangChain, model olarak 
  OpenRouter üzerinden Gemma 4 27B
- **Embedding:** Google text-embedding-004
- **Vector DB:** Qdrant (Docker container)
- **Database:** MongoDB (Motor async driver)
- **Container Orchestration:** Kubernetes (DOKS)
- **Reverse Proxy:** Nginx (subdomain routing)
- **Auth:** JWT (access token kısa ömürlü, 
  refresh token MongoDB'de)

---

## Proje Klasör Yapısı

Aşağıdaki modüler yapıyı kur, her modül 
kendi içinde kapalı olsun:

backend/
├── main.py
├── core/
│   ├── config.py         # env değişkenleri
│   ├── database.py       # MongoDB bağlantısı
│   ├── kubernetes.py     # k8s client setup
│   └── qdrant.py         # Qdrant client setup
├── auth/
│   ├── router.py
│   ├── service.py
│   ├── models.py
│   └── utils.py          # JWT işlemleri
├── projects/
│   ├── router.py
│   ├── service.py
│   └── models.py
├── agent/
│   ├── graph.py          # LangGraph graph tanımı
│   ├── nodes.py          # graph node'ları
│   ├── tools/
│   │   ├── file_tools.py
│   │   ├── command_tools.py
│   │   └── sandbox_tools.py
│   ├── memory/
│   │   ├── summary.py    # dosya özetleri
│   │   └── file_tree.py  # proje dosya ağacı
│   └── rag/
│       ├── indexer.py    # embedding + qdrant'a yaz
│       └── retriever.py  # semantic search
├── containers/
│   ├── service.py        # kubernetes işlemleri
│   └── models.py
├── sandbox/
│   ├── client.py         # sidecar API iletişimi
│   └── models.py
└── github/
    ├── service.py        # public repo clone
    └── models.py

---

## MongoDB Koleksiyonları

**users:**
- id, email, hashed_password
- created_at, updated_at

**refresh_tokens:**
- token, user_id, expires_at, revoked

**projects:**
- id, user_id, name, status
- kubernetes_deployment_name
- kubernetes_namespace
- preview_url (proje-{id}.domain.com formatında)
- created_at, updated_at

**agent_sessions:**
- id, project_id, user_id
- status (running / completed / failed)
- steps: [ {step_no, action, tool_used, 
            result, error, timestamp} ]
- created_at

**file_summaries:**
- project_id, file_path
- summary (dosyanın ne yaptığının kısa özeti)
- embedding_id (Qdrant'taki ID)
- last_updated

---

## Auth Modülü

- POST /auth/register
- POST /auth/login → access_token + refresh_token döner
- POST /auth/refresh → yeni access_token
- POST /auth/logout → refresh_token'ı revoke et
- Access token: 30 dakika, JWT
- Refresh token: 30 gün, MongoDB'de saklanır
- Tüm diğer endpoint'ler JWT middleware ile korunur

---

## Projects Modülü

- POST /projects → yeni proje oluştur
  (isim alır, MongoDB'ye kaydeder, 
   Kubernetes'te namespace açar)
- GET /projects → kullanıcının projeleri
- GET /projects/{id} → proje detayı
- DELETE /projects/{id} → projeyi sil
  (Kubernetes deployment + service + ingress sil,
   MongoDB kayıtlarını temizle)

---

## Containers Modülü

Kubernetes Python client kullanarak:

- Her proje için şunları oluştur:
  - Namespace (proje id'si ile)
  - Deployment (2 container: kullanıcı projesi 
    + sidecar API)
  - Service (internal)
  - Ingress (subdomain routing için)

- Sidecar container:
  - Python FastAPI tabanlı küçük servis
  - Sadece cluster içinden erişilebilir
  - Şu endpoint'leri sunar:
    - GET  /files?path=        → dosya listesi
    - GET  /files/read?path=   → dosya içeriği
    - POST /files/write        → dosya yaz
    - DELETE /files/delete     → dosya sil
    - POST /exec               → komut çalıştır
    - GET  /logs               → uygulama logları
    - POST /restart            → servisi yeniden başlat

- Subdomain routing:
  proje-{project_id}.domain.com → ilgili pod

---

## Agent Modülü

### LangGraph Graph Yapısı

State:
```python
class AgentState(TypedDict):
    messages: list
    project_id: str
    user_request: str
    file_tree: dict
    relevant_files: list
    current_step: int
    max_steps: int  # 25
    errors: list
    status: str
    session_id: str
```

Node'lar:
1. **context_builder_node**
   - Dosya ağacını sidecar'dan çek
   - File summary'leri MongoDB'den al
   - RAG ile ilgili dosyaları bul
   - State'e yaz

2. **planner_node**
   - Gemma 4'e context + user_request gönder
   - Ne yapılacağını adım adım planla
   - Planı state'e yaz

3. **action_node**
   - Tool seç ve çalıştır
   - (write_file, read_file, run_command, 
      restart_service)
   - Sonucu state'e yaz

4. **observer_node**
   - Action sonucunu değerlendir
   - Hata var mı kontrol et
   - Devam mı, düzelt mi, bitir mi kararı ver

5. **summary_updater_node**
   - Değiştirilen dosyaların özetini güncelle
   - Qdrant'taki embedding'i güncelle

Edge mantığı:
- observer → action (devam et)
- observer → action (hata varsa düzelt)
- observer → END (bitti)
- current_step >= max_steps → END (timeout)

### Tools

**file_tools.py:**
- read_file(project_id, path)
- write_file(project_id, path, content)
- delete_file(project_id, path)
- list_files(project_id, directory)

**command_tools.py:**
- run_command(project_id, command)
  → stdout + stderr döner

**sandbox_tools.py:**
- restart_service(project_id)
- get_logs(project_id, lines=50)

### RAG

- Indexleme: Proje ilk yüklendiğinde veya 
  dosya değiştiğinde çalışır
  - Dosyayı chunk'lara böl (500 token)
  - Google text-embedding-004 ile embed et
  - Qdrant'a yaz (collection: project_id)

- Retrieval: Agent context_builder_node'unda
  - User request'i embed et
  - Qdrant'ta semantic search yap
  - En ilgili 5-10 chunk'ı döndür

---

## WebSocket Endpoint'leri

### Agent Stream
WS /ws/agent/{session_id}

Her agent adımında şu formatı gönder:
```json
{
  "type": "step",
  "step_no": 3,
  "action": "write_file",
  "file": "src/main.py",
  "status": "success",
  "message": "main.py güncellendi"
}
```

Biterken:
```json
{
  "type": "complete",
  "preview_url": "proje-abc.domain.com",
  "total_steps": 12
}
```

### Log Stream
WS /ws/logs/{project_id}

Sidecar'ın /logs endpoint'ini sürekli 
poll ederek WebSocket üzerinden ilet.

---

## GitHub Modülü

- POST /github/clone
  Body: { "repo_url": "https://github.com/...",
          "project_id": "..." }
  
  - Sadece public repo destekle (şimdilik)
  - gitpython ile clone et
  - Dosyaları container'a sidecar üzerinden kopyala
  - RAG indexlemeyi tetikle
  - Dosya summary'lerini oluştur

---

## Agent Endpoint'leri

- POST /agent/run
  Body: { "project_id": "...", 
          "message": "kullanıcının isteği" }
  → session_id döner, WS üzerinden takip edilir

- GET /agent/sessions/{project_id}
  → Proje için tüm agent session geçmişi

- GET /agent/sessions/{session_id}/steps
  → Bir session'ın tüm adımları

---

## Önemli Notlar

1. Tüm I/O operasyonları async olsun
2. Her modülün kendi exception handler'ı olsun
3. Pydantic v2 kullan
4. Her endpoint için temel error handling yap
5. Environment variable'lar için .env + 
   pydantic-settings kullan
6. requirements.txt oluştur
7. Her modül için temel docstring'ler yaz
8. Kubernetes namespace isimleri: 
   "project-{project_id}" formatında olsun
9. Sidecar servisinin ayrı bir 
   Dockerfile'ı olsun (sidecar/Dockerfile)
10. Ana backend için de Dockerfile olsun