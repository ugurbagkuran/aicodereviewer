"""
Agent modülü — AI destekli kod düzenleme.

LangGraph tabanlı agent, projeleri analiz eder ve kod değişiklikleri yapar.

Bileşenler:
  graph.py       → LangGraph graph tanımı ve orchestration
  nodes.py       → Graph node'ları (context_builder, planner, action, observer, summary_updater)
  tools/         → Agent'ın kullandığı araçlar
    file_tools.py     → Dosya okuma/yazma/silme
    command_tools.py  → Shell komutu çalıştırma
    sandbox_tools.py  → Servis yönetimi
  memory/        → Proje bağlam yönetimi
    summary.py   → Dosya özetleri
    file_tree.py → Proje dosya ağacı
  rag/           → Retrieval Augmented Generation
    indexer.py   → Embedding + Qdrant'a yazma
    retriever.py → Semantic search
"""
