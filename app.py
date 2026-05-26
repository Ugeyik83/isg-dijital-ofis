import os
import queue
import threading
import datetime

# ── Groq uyumluluk: tüm import'lardan ÖNCE ───────────────────────────────────
def _noop_cache_breakpoint(message):
    return message

import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = _noop_cache_breakpoint
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

# ── Streamlit secrets → env ───────────────────────────────────────────────────
if hasattr(st, "secrets"):
    for key in ("GROQ_API_KEY", "LLM_PROVIDER", "LLM_MODEL_NAME"):
        if key in st.secrets:
            os.environ[key] = st.secrets[key]

# ── Sayfa yapılandırması ──────────────────────────────────────────────────────
st.set_page_config(page_title="Sanal İSG Ofisi", page_icon="🦺", layout="wide")

st.title("🦺 Sanal İSG Ofisi (Dijital İkiz Prototip)")
st.markdown(
    "Bir iş kazası, ramak kala veya sağlık olayı bildirimi yapın; "
    "**İSG Uzmanı**, **İSG Müdürü** ve **Raporlama Sorumlusu** ajanları iş başına geçsin."
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Sistem Bilgisi")
    model = os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-versatile")
    st.info(
        f"**Kullanılan Model:** {model}\n\n"
        "**Aktif Ajanlar:**\n"
        "- 🧑‍🔧 İSG Uzmanı\n"
        "- 👨‍💼 İSG Müdürü\n"
        "- 📋 Raporlama Sorumlusu"
    )
    st.divider()
    st.caption("v1.4 - Dijital İkiz Prototip")

# ── Session state ─────────────────────────────────────────────────────────────
if "olay_metni" not in st.session_state:
    st.session_state["olay_metni"] = ""

# ── Örnek senaryolar ──────────────────────────────────────────────────────────
ORNEKLER = {
    "🏭 Makine Kazası": (
        "Pazartesi sabahı, üretim hattında bir operatör koruyucu siperi kaldırılmış "
        "makineye parça yerleştirirken parmağını sıkıştırdı. "
        "İş ayakkabısı ve eldiveni vardı ancak siper devre dışı bırakılmış."
    ),
    "🧪 Kimyasal Sızıntı": (
        "Kimya laboratuvarında çalışan bir teknisyen, çeker ocak çalışmadığı için "
        "asit buharına maruz kaldı. Solunum zorluğu şikayetiyle revire gitti."
    ),
    "🚧 Düşme Kazası": (
        "İnşaat alanında 4. katta çalışan bir işçi, güvenlik halatını takmadan "
        "iskeleye çıktı. Denge kaybederek 1 metre aşağıdaki platforma düştü. "
        "Sol kolunda kırık tespit edildi."
    ),
}

col1, col2 = st.columns([2, 1])
with col2:
    st.markdown("### Örnek Senaryolar")
    for etiket, metin in ORNEKLER.items():
        if st.button(etiket, use_container_width=True):
            st.session_state["olay_metni"] = metin

with col1:
    olay = st.text_area(
        "📝 Olay Açıklaması",
        value=st.session_state["olay_metni"],
        height=180,
        placeholder=(
            "Örn: Dün vardiyada depo bölümünde bir çalışan ıslak zeminde kaydı, "
            "kolunu incitti. Zemin yeni temizlenmiş ama uyarı levhası konmamıştı."
        ),
        key="olay_input"
    )

baslat = st.button("🚀 Simülasyonu Başlat", type="primary", use_container_width=True)

# ── Ajan ikonu eşleme ─────────────────────────────────────────────────────────
AJAN_IKON = {
    "İSG Uzmanı": "🧑‍🔧",
    "İSG Müdürü": "👨‍💼",
    "Raporlama ve Dokümantasyon Sorumlusu": "📋",
}

# ── Simülasyon ────────────────────────────────────────────────────────────────
if baslat and olay.strip():
    try:
        from crew_setup import isg_ekibi_olustur
        from crewai.agents.crew_agent_executor import AgentAction, AgentFinish
    except EnvironmentError as env_err:
        st.error(f"⚙️ Yapılandırma hatası: {env_err}")
        st.stop()

    # ── Queue tabanlı thread-safe callback mekanizması ────────────────────────
    # CrewAI farklı bir thread'de çalışıyor; doğrudan st.* çağıramazsınız.
    # Mesajları bir queue'ya koyup ana thread'den okuyoruz.
    step_queue: queue.Queue = queue.Queue()
    result_holder: dict = {}

    # Her ajan adımında çağrılır (AgentAction = düşünme, AgentFinish = bitiş)
    def step_callback(step_output):
        if isinstance(step_output, AgentAction):
            step_queue.put({
                "type": "action",
                "thought": step_output.thought,
                "tool": step_output.tool,
                "tool_input": step_output.tool_input,
                "result": step_output.result or "",
            })
        elif isinstance(step_output, AgentFinish):
            step_queue.put({
                "type": "finish",
                "thought": step_output.thought,
                "output": str(step_output.output),
            })

    # Her görev bittiğinde çağrılır
    def task_callback(task_output):
        step_queue.put({
            "type": "task_done",
            "agent": task_output.agent or "Ajan",
            "summary": task_output.summary or str(task_output.raw)[:200],
        })

    def run_crew():
        try:
            crew = isg_ekibi_olustur(
                olay,
                step_callback=step_callback,
                task_callback=task_callback,
            )
            output = crew.kickoff()
            result_holder["output"] = output.raw if hasattr(output, "raw") else str(output)
        except Exception as e:
            result_holder["error"] = str(e)
        finally:
            step_queue.put({"type": "done"})  # sentinel

    # ── Arayüz ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔄 Canlı Ajan Akışı")

    # Sohbet geçmişini tutacak container
    chat_container = st.container()

    # Crew'i arka planda çalıştır
    thread = threading.Thread(target=run_crew, daemon=True)
    thread.start()

    # Ana thread: queue'yu boşalt ve mesajları sohbet baloncuğu olarak göster
    adim_sayaci = 0
    with chat_container:
        while True:
            try:
                msg = step_queue.get(timeout=60)  # max 60s bekle
            except queue.Empty:
                st.warning("⏱️ Zaman aşımı — ajan yanıt vermedi.")
                break

            if msg["type"] == "done":
                break

            adim_sayaci += 1

            if msg["type"] == "action":
                with st.chat_message("assistant"):
                    st.markdown(
                        f"**💭 Düşünce:** {msg['thought']}\n\n"
                        f"**🔧 Araç:** `{msg['tool']}`\n\n"
                        f"**📥 Girdi:** {msg['tool_input']}"
                        + (f"\n\n**📤 Sonuç:** {msg['result']}" if msg["result"] else "")
                    )

            elif msg["type"] == "finish":
                with st.chat_message("assistant"):
                    st.markdown(
                        f"**✅ Tamamlandı**\n\n"
                        f"**💭 Düşünce:** {msg['thought']}\n\n"
                        f"**📋 Çıktı:** {msg['output'][:500]}{'...' if len(msg['output']) > 500 else ''}"
                    )

            elif msg["type"] == "task_done":
                ikon = AJAN_IKON.get(msg["agent"], "🤖")
                with st.chat_message("user"):
                    st.markdown(
                        f"**{ikon} {msg['agent']} görevi tamamladı**\n\n"
                        f"{msg['summary']}"
                    )

    thread.join(timeout=5)

    # ── Sonuç gösterimi ───────────────────────────────────────────────────────
    if "error" in result_holder:
        st.error(f"❌ Hata oluştu: {result_holder['error']}")
        st.info(
            "💡 Kontrol listesi:\n"
            "- GROQ_API_KEY doğru mu?\n"
            "- Groq rate limit dolmadı mı?\n"
            "- İnternet bağlantısı var mı?"
        )
    elif "output" in result_holder:
        st.success("✅ İSG Değerlendirme Süreci Tamamlandı!")
        st.markdown("---")
        st.markdown("### 📄 Final Rapor")

        tab1, tab2 = st.tabs(["📋 Rapor", "📝 Ham Çıktı"])
        with tab1:
            st.markdown(result_holder["output"])
        with tab2:
            st.code(result_holder["output"], language="markdown")

        dosya_adi = f"isg_raporu_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        st.download_button(
            label="📥 Raporu İndir (TXT)",
            data=result_holder["output"],
            file_name=dosya_adi,
            mime="text/plain"
        )

elif baslat:
    st.warning("⚠️ Lütfen önce bir olay açıklaması girin.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("© 2025 Sanal İSG Ofisi | CrewAI + Groq + Streamlit ile geliştirilmiştir.")