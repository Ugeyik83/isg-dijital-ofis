import os

# ── Groq uyumluluk: tüm import'lardan ÖNCE set edilmeli ──────────────────────
# CrewAI 1.14.x mesajlara cache_breakpoint ekliyor; Groq bunu reddediyor.
# Bu env değişkenleri Python modülü yüklenmeden önce işletim sistemine yazılır.
os.environ["LITELLM_DROP_PARAMS"] = "true"
os.environ["ANTHROPIC_CACHE_ENABLED"] = "false"

import streamlit as st
import datetime

# ── Streamlit secrets → env (production) ─────────────────────────────────────
if hasattr(st, "secrets"):
    for key in ("GROQ_API_KEY", "LLM_PROVIDER", "LLM_MODEL_NAME"):
        if key in st.secrets:
            os.environ[key] = st.secrets[key]

# ── Sayfa yapılandırması ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sanal İSG Ofisi",
    page_icon="🦺",
    layout="wide"
)

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
    st.caption("v1.2 - Dijital İkiz Prototip")

# ── Session state başlatma ────────────────────────────────────────────────────
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
            "kolunu incitti. İlk yardım yapıldı. Zemin yeni temizlenmiş ama uyarı "
            "levhası konmamıştı."
        ),
        key="olay_input"
    )

baslat = st.button("🚀 Simülasyonu Başlat", type="primary", use_container_width=True)

# ── Simülasyon ────────────────────────────────────────────────────────────────
if baslat and olay.strip():
    try:
        from crew_setup import isg_ekibi_olustur
    except EnvironmentError as env_err:
        st.error(f"⚙️ Yapılandırma hatası: {env_err}")
        st.stop()

    with st.spinner("🔍 İSG Ekibi olayı değerlendiriyor..."):
        progress = st.progress(0, text="🔄 Ekip hazırlanıyor...")
        try:
            crew = isg_ekibi_olustur(olay)
            progress.progress(20, text="🔍 İSG Uzmanı kök neden analizi yapıyor...")

            crew_output = crew.kickoff()

            progress.progress(80, text="📋 Rapor hazırlanıyor...")

            # CrewAI 1.x: kickoff() → CrewOutput; .raw string içerir
            sonuc_metni = crew_output.raw if hasattr(crew_output, "raw") else str(crew_output)

            progress.progress(100, text="✅ Tamamlandı!")
            progress.empty()

        except Exception as e:
            progress.empty()
            st.error(f"❌ Hata oluştu: {e}")
            st.info(
                "💡 Kontrol listesi:\n"
                "- GROQ_API_KEY doğru mu? (Streamlit Cloud: Settings → Secrets)\n"
                "- Groq hesabınızın rate limit'i dolmadı mı?\n"
                "- İnternet bağlantısı var mı?"
            )
            st.stop()

    st.success("✅ İSG Değerlendirme Süreci Tamamlandı!")

    tab1, tab2 = st.tabs(["📋 Rapor", "📝 Ham Çıktı"])
    with tab1:
        st.markdown(sonuc_metni)
    with tab2:
        st.code(sonuc_metni, language="markdown")

    dosya_adi = f"isg_raporu_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    st.download_button(
        label="📥 Raporu İndir (TXT)",
        data=sonuc_metni,
        file_name=dosya_adi,
        mime="text/plain"
    )

elif baslat:
    st.warning("⚠️ Lütfen önce bir olay açıklaması girin.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("© 2025 Sanal İSG Ofisi | CrewAI + Groq + Streamlit ile geliştirilmiştir.")
