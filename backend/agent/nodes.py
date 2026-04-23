"""
Agent modülü — LangGraph graph node'ları.

Her node, agent pipeline'ında bir adımdır:
  1. context_builder  → Proje bağlamını topla
  2. planner          → Yapılacakları planla
  3. action           → Tool çağır (dosya yaz, komut çalıştır vb.)
  4. observer         → Sonucu değerlendir, devam/düzelt/bitir
  5. summary_updater  → Değiştirilen dosyaların özetini güncelle
"""

from datetime import datetime, timezone

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import structlog

from agent.memory.file_tree import get_file_tree
from agent.memory.summary import get_file_summaries, upsert_file_summary
from core.config import settings
from core.database import Database

logger = structlog.get_logger(__name__)

# LLM instance cache (modül başına bir kez oluştur)
_llm_instance = None


def _get_llm():
    """
    Google AI Studio üzerinden (Gemini vb.) model instance'ı.
    """
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    from langchain_google_genai import ChatGoogleGenerativeAI
    _llm_instance = ChatGoogleGenerativeAI(
        model=settings.AI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.1,
        max_tokens=8192,
    )

    return _llm_instance


def _extract_text(content) -> str:
    """
    LLM çıktısını güvenli şekilde string'e çevirir.
    'Thinking' modelleri liste formatında [{'type': 'thinking', ...}, {'type': 'text', 'text': '...'}] döner.
    """
    if isinstance(content, list):
        return " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
    return str(content)


# ═══════════════════════════════════════════════════════
# NODE 1: CONTEXT BUILDER
# ═══════════════════════════════════════════════════════


async def context_builder_node(state: dict) -> dict:
    """
    Proje bağlamını topla ve state'e yaz.

    1. Sidecar'dan dosya ağacını çek
    2. MongoDB'den dosya özetlerini al
    3. (RAG ile ilgili dosyaları bul — Qdrant aktifse)
    """
    project_id = state["project_id"]

    logger.info("node_context_builder", project_id=project_id)

    # 1. Dosya ağacı
    try:
        file_tree = await get_file_tree(project_id)
    except Exception as e:
        file_tree = f"(Dosya ağacı alınamadı: {e})"
        logger.warning("file_tree_failed", error=str(e))

    # 2. Dosya özetleri
    db = Database.get_db()
    summaries = await get_file_summaries(db, project_id)
    summaries_text = "\n".join(
        f"- {s['file_path']}: {s['summary']}"
        for s in summaries
    ) if summaries else "(Henüz dosya özeti yok)"

    # 3. RAG ile ilgili dosyalar (ileride Qdrant aktif olunca)
    relevant_files = []
    # try:
    #     from agent.rag.retriever import get_relevant_files
    #     query_embedding = await embed_query(state["user_request"])
    #     relevant_files = await get_relevant_files(project_id, query_embedding)
    # except Exception:
    #     pass

    return {
        **state,
        "file_tree": file_tree,
        "file_summaries": summaries_text,
        "relevant_files": relevant_files,
        "current_step": state.get("current_step", 0),
    }


# ═══════════════════════════════════════════════════════
# NODE 2: PLANNER
# ═══════════════════════════════════════════════════════


async def planner_node(state: dict) -> dict:
    """
    Kullanıcı isteğini analiz et ve yapılacakları planla.

    LLM'e proje bağlamı + istek gönderir, adım adım plan alır.
    """
    logger.info("node_planner", project_id=state["project_id"])

    llm = _get_llm()

    system_prompt = """Sen bir yazılım mühendisi AI agent'sın.
Kullanıcının isteğini analiz et ve bir aksiyon planı oluştur.

Kullanabileceğin araçlar:
- read_file(path): Dosya oku
- write_file(path, content): Dosya yaz
- delete_file(path): Dosya sil
- list_files(directory): Dizin listele
- run_command(command): Shell komutu çalıştır
- restart_service(): Servisi yeniden başlat
- get_logs(lines): Log oku

Kurallar:
1. Önce mevcut kodu anla, sonra değişiklik yap.
2. Minimum gerekli değişikliği yap, gereksiz dosyalara dokunma.
3. Her adımda ne yapacağını açıkla.
4. Hata olursa logları kontrol et ve düzelt.
5. İşin bitince restart_service() çağır.

Planını JSON formatında döndür:
{
    "analysis": "İsteğin kısa analizi",
    "steps": [
        {"action": "read_file", "target": "src/main.py", "reason": "Mevcut kodu anla"},
        {"action": "write_file", "target": "src/utils.py", "reason": "Yardımcı fonksiyon ekle"},
        ...
    ]
}"""

    context = f"""
PROJE DOSYA AĞACI:
{state.get('file_tree', '(yok)')}

DOSYA ÖZETLERİ:
{state.get('file_summaries', '(yok)')}

KULLANICI İSTEĞİ:
{state['user_request']}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=context),
    ]

    response = await llm.ainvoke(messages)
    content_str = _extract_text(response.content)

    return {
        **state,
        "plan": content_str,
        "messages": state.get("messages", []) + [
            {"role": "assistant", "content": content_str, "node": "planner"}
        ],
    }


# ═══════════════════════════════════════════════════════
# NODE 3: ACTION
# ═══════════════════════════════════════════════════════


async def action_node(state: dict) -> dict:
    """
    Plan'a göre tool çağrısı yap.

    LLM'e mevcut durumu ve planı vererek hangi tool'u
    hangi parametrelerle çağıracağını sorar.
    Tool'u çalıştırır ve sonucu state'e yazar.
    """
    step = state.get("current_step", 0) + 1
    logger.info(
        "node_action",
        project_id=state["project_id"],
        step=step,
    )

    llm = _get_llm()

    # Tool çağrısı için prompt
    action_prompt = f"""Mevcut adım: {step}
Plan: {state.get('plan', '')}

Önceki mesajlar:
{_format_messages(state.get('messages', []))}

Şimdi hangi aksiyonu alman gerekiyor? Tek bir tool çağrısı yap.
Respond with a JSON:
{{
    "tool": "tool_name",
    "args": {{"arg1": "value1"}},
    "reason": "Bu adımı neden yapıyorum"
}}
"""

    messages = [
        SystemMessage(content="Sen bir kod yazma agent'sın. Verilen plan doğrultusunda tek bir adım gerçekleştir."),
        HumanMessage(content=action_prompt),
    ]

    response = await llm.ainvoke(messages)
    content_str = _extract_text(response.content)

    # Tool çağrısını gerçekleştir
    tool_result = await _execute_tool(
        state["project_id"],
        content_str,
    )

    return {
        **state,
        "current_step": step,
        "last_action": content_str,
        "last_result": tool_result,
        "messages": state.get("messages", []) + [
            {"role": "assistant", "content": content_str, "node": "action"},
            {"role": "tool", "content": tool_result, "node": "action"},
        ],
    }


# ═══════════════════════════════════════════════════════
# NODE 4: OBSERVER
# ═══════════════════════════════════════════════════════


async def observer_node(state: dict) -> dict:
    """
    Action sonucunu değerlendir ve karar ver:
    - continue: Devam et (sıradaki adım)
    - fix: Hata var, düzelt
    - done: İş bitti
    """
    logger.info(
        "node_observer",
        project_id=state["project_id"],
        step=state.get("current_step", 0),
    )

    llm = _get_llm()

    observe_prompt = f"""Son aksiyonun sonucu:
{state.get('last_result', '')}

Plan: {state.get('plan', '')}

Mevcut adım: {state.get('current_step', 0)}
Maksimum adım: {state.get('max_steps', 25)}

Değerlendir:
1. Hata var mı?
2. Plan tamamlandı mı?
3. Bir sonraki adım ne olmalı?

CEVABINI ZORUNLU OLARAK AŞAĞIDAKİ EXACT JSON FORMATINDA VER:
{{
    "decision": "continue" | "fix" | "done",
    "reasoning": "Plan başarıyla tamamlandı, bu yüzden done dönüyorum.",
    "error": null
}}
Hiçbir tool, komut veya dosya yazma JSON'u DÖNDÜRME. Sistem şu an senin kod yazmanı DEĞİL, çalışmanı bitirip bitirmediğini puanlamanı bekliyor.
"""

    messages = [
        SystemMessage(content="DİKKAT: Sen sadece bir denetçisin (OBSERVER). Kod yazmamalısın. Çıktın 'continue', 'fix' ya da 'done' seçeneklerinden birini içeren basit bir JSON olmalıdır."),
        HumanMessage(content=observe_prompt),
    ]

    response = await llm.ainvoke(messages)
    content_str = _extract_text(response.content)

    return {
        **state,
        "observation": content_str,
        "messages": state.get("messages", []) + [
            {"role": "assistant", "content": content_str, "node": "observer"}
        ],
    }


# ═══════════════════════════════════════════════════════
# NODE 5: SUMMARY UPDATER
# ═══════════════════════════════════════════════════════


async def summary_updater_node(state: dict) -> dict:
    """
    Değiştirilen dosyaların özetlerini güncelle.

    Agent'ın bir sonraki çalışmasında bağlam olarak
    kullanılacak dosya özetlerini MongoDB'ye yazar.
    """
    logger.info("node_summary_updater", project_id=state["project_id"])

    # Değiştirilen dosyaları bul (mesajlardan)
    modified_files = _extract_modified_files(state.get("messages", []))

    if not modified_files:
        return {**state, "status": "completed"}

    db = Database.get_db()
    llm = _get_llm()

    for file_path in modified_files:
        try:
            # Dosya içeriğini oku
            from sandbox.client import SandboxClient
            client = SandboxClient(state["project_id"])
            result = await client.read_file(file_path)
            content = result.get("content", "")

            if not content:
                continue

            # LLM ile özet oluştur
            summary_prompt = f"""Bu dosyanın ne yaptığını tek cümlede özetle:

Dosya: {file_path}
İçerik:
{content[:2000]}
"""
            response = await llm.ainvoke([
                HumanMessage(content=summary_prompt)
            ])
            content_str = _extract_text(response.content)

            await upsert_file_summary(
                db=db,
                project_id=state["project_id"],
                file_path=file_path,
                summary=content_str.strip(),
            )

        except Exception as e:
            logger.warning(
                "summary_update_failed",
                file_path=file_path,
                error=str(e),
            )

    return {**state, "status": "completed"}


# ═══════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR
# ═══════════════════════════════════════════════════════


def _format_messages(messages: list[dict]) -> str:
    """Mesaj geçmişini okunabilir formata çevir."""
    lines = []
    for msg in messages[-10:]:  # Son 10 mesaj
        role = msg.get("role", "unknown")
        node = msg.get("node", "")
        content = msg.get("content", "")[:500]
        lines.append(f"[{role}/{node}]: {content}")
    return "\n".join(lines) if lines else "(boş)"


def _extract_modified_files(messages: list[dict]) -> list[str]:
    """
    Mesaj geçmişinden değiştirilen dosya yollarını çıkar.

    write_file tool çağrılarından dosya yollarını toplar.
    """
    modified = set()
    for msg in messages:
        content = msg.get("content", "")
        if "write_file" in content and "path" in content:
            # Basit çıkarım — LLM çıktısından path'i bul
            import re
            paths = re.findall(r'"path":\s*"([^"]+)"', content)
            modified.update(paths)

            # "Dosya yazıldı:" formatından da çıkar
            written = re.findall(r"Dosya yazıldı:\s*(\S+)", content)
            modified.update(written)

    return list(modified)


async def _execute_tool(project_id: str, llm_response: str) -> str:
    """
    LLM'in JSON çıktısını parse edip ilgili tool'u çalıştır.

    Args:
        project_id: Proje ID'si.
        llm_response: LLM'den gelen JSON string.

    Returns:
        Tool çalıştırma sonucu.
    """
    import json

    try:
        # Gemini bazı durumlarda response.content'i string yerine list döndürebilir.
        if isinstance(llm_response, list):
            llm_response = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in llm_response])

        # JSON'u parse et (markdown code block içinde olabilir)
        import re
        clean = llm_response.strip()

        # Önce ```json ... ``` veya ``` ... ``` pattern'ini dene
        match = re.search(r"```(?:json)?\s*({.*?})\s*```", clean, re.DOTALL)
        if match:
            clean = match.group(1).strip()
        elif "{" in clean:
            # Düz JSON bloğu bul
            start = clean.index("{")
            end = clean.rindex("}") + 1
            clean = clean[start:end]

        data = json.loads(clean)
        tool_name = data.get("tool", "")
        args = data.get("args", {})
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        return f"Tool parse hatası: {e}. LLM çıktısı: {llm_response[:200]}"

    from sandbox.client import SandboxClient
    client = SandboxClient(project_id)

    try:
        if tool_name == "read_file":
            result = await client.read_file(args.get("path", ""))
            return result.get("content", "")

        elif tool_name == "write_file":
            await client.write_file(
                args.get("path", ""),
                args.get("content", ""),
            )
            return f"Dosya yazıldı: {args.get('path', '')}"

        elif tool_name == "delete_file":
            await client.delete_file(args.get("path", ""))
            return f"Dosya silindi: {args.get('path', '')}"

        elif tool_name == "list_files":
            result = await client.list_files(args.get("directory", "/"))
            files = result.get("files", [])
            return "\n".join(
                item.get("name", str(item)) if isinstance(item, dict) else str(item)
                for item in files
            )

        elif tool_name == "run_command":
            result = await client.exec_command(
                args.get("command", ""),
                timeout=args.get("timeout", 30),
            )
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")
            exit_code = result.get("exit_code", -1)
            return f"Exit: {exit_code}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"

        elif tool_name == "restart_service":
            result = await client.restart_service()
            return result.get("message", "Servis yeniden başlatıldı.")

        elif tool_name == "get_logs":
            result = await client.get_logs(args.get("lines", 50))
            return result.get("logs", "")

        else:
            return f"Bilinmeyen tool: {tool_name}"

    except Exception as e:
        logger.error(
            "tool_execution_failed",
            tool=tool_name,
            error=str(e),
        )
        return f"Tool hatası ({tool_name}): {e}"
