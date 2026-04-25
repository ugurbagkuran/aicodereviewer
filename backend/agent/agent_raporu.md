# Agent Sorun ve Cozum Raporu

Tarih: 2026-04-24

## Kapsam

Bu rapor, backend tarafindaki agent calisma sorunlarini, kok nedenlerini,
yapilan kod duzeltmelerini ve agent odakli test sonuclarini dokumante eder.

## Tespit Edilen Sorunlar

1. Observer adiminda action JSON tekrar gorunuyordu.
2. Agent bazi akislarda `running` durumunda takili kaliyordu.
3. HTML/sayfa isteklerinde `index.html` icerigi bazen sadece duz metin oluyordu.
4. Preview root (`/`) endpoint'i 404 donuyordu.
5. Duzeltme sirasinda bir asamada `run_agent` cagrisi 500 dondu (runtime NameError).

## Kok Nedenler

1. Step kayitlarinda `action` alani node-ozel degil, her zaman `last_action` ile
   dolduruldugu icin observer satirlarinda onceki action gorunuyordu.
2. Observer kararinda model sapmasi ve tekrarli tool akislari, done kararina
   ulasilamadiginda dongu olusturabiliyordu.
3. `list_files` tool cagrisi yalnizca `directory` argumanini beklerken model
   cogu kez `path` gonderiyordu.
4. Sidecar API'de root (`/`) endpoint'i olmadigi icin preview host'ta ana sayfa
   acilmiyordu.
5. `graph.py` icinde, `AgentState` tanimindan once yazilan fonksiyonlarda
   `state: AgentState` annotation'i runtime'da NameError uretti.

## Uygulanan Duzeltmeler

1. Node-ozel step/action kaydi duzeltildi.
   - Dosya: `backend/agent/graph.py`
2. Write+verify tamamlaninca zorunlu bitis (done) ve tekrarli dongu korumasi eklendi.
   - Dosya: `backend/agent/graph.py`
3. HTML istekleri icin write_file icerigi tam HTML dokumanina normalize edildi.
   - Dosya: `backend/agent/nodes.py`
4. Observer promptu, karar kalitesini arttirmak icin son action/tool izi ile
   guclendirildi.
   - Dosya: `backend/agent/nodes.py`
5. `list_files` tool'u hem `directory` hem `path` argumanini destekleyecek sekilde
   guncellendi.
   - Dosya: `backend/agent/nodes.py`
6. Preview root icin sidecar'a `/` endpoint'i eklendi; `index.html` varsa direkt
   HTML olarak servis edilmeye baslandi.
   - Dosya: `backend/sidecar/main.py`
7. Runtime NameError duzeltildi (`AgentState` ileri referans sorunu).
   - Dosya: `backend/agent/graph.py`

## Agent Odakli Test Senaryosu

1. Yeni kullanici kaydi + login
2. Yeni proje olusturma ve proje start
3. Agent run: "Tam bir HTML sayfasi yaz, dosya index.html olsun"
4. WebSocket adim takibi (`context_builder -> planner -> action -> observer -> ...`)
5. Session adimlari API dogrulamasi
6. Dosya sistemi dogrulamasi (`index.html` varligi ve icerigi)
7. Preview dogrulamasi
   - `Host: project-<id>.localhost` ile `GET /`
   - `Host: project-<id>.localhost` ile `GET /files/read?path=index.html`

## Test Sonuclari (Son Gecerli Kosu)

1. `run_agent`: 200
2. WebSocket: `complete` eventi alindi
3. Session status: `completed`
4. Session adim sayisi: 7
5. `index.html` olustu ve dogrulandi:
   - `<!doctype html` var
   - `<html` etiketi var
   - `Hello World` icerigi var
6. Preview root (`/`) status: 200
7. Ingress uzerinden `files/read` status: 200

## Takip Notlari

1. LLM ciktilari dogasi geregi degisken oldugu icin observer/route korumalari
   korunmali.
2. Agent davranis degisikliginde, en az bir agent odakli E2E testi tekrar
   calistirilmali.
