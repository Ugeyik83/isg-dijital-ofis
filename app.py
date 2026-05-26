import os
import queue
import threading
import datetime
import base64
from pathlib import Path

# ── Groq uyumluluk: tüm import'lardan ÖNCE ───────────────────────────────────
def _noop_cache_breakpoint(message):
    return message

import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = _noop_cache_breakpoint
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

if hasattr(st, "secrets"):
    for key in ("GROQ_API_KEY", "LLM_PROVIDER", "LLM_MODEL_NAME"):
        if key in st.secrets:
            os.environ[key] = st.secrets[key]

st.set_page_config(page_title="Sanal İSG Ofisi", page_icon="🦺", layout="wide")

st.title("🦺 Sanal İSG Ofisi (Dijital İkiz Prototip)")
st.markdown(
    "Bir iş kazası, ramak kala veya sağlık olayı bildirimi yapın; "
    "**İSG Uzmanı**, **İSG Müdürü** ve **Raporlama Sorumlusu** ajanları iş başına geçsin."
)

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
    st.caption("v1.6 - Dijital İkiz Prototip")

# ── Girdi alanı ───────────────────────────────────────────────────────────────
olay = st.text_area(
    "📝 Olay Açıklaması",
    height=180,
    placeholder=(
        "Örn: Dün vardiyada depo bölümünde bir çalışan ıslak zeminde kaydı, "
        "kolunu incitti. Zemin yeni temizlenmiş ama uyarı levhası konmamıştı."
    ),
)

# ── Medya yükleme ─────────────────────────────────────────────────────────────
yuklenen_dosyalar = st.file_uploader(
    "📎 Olay fotoğrafı veya videosu ekleyin (opsiyonel)",
    type=["jpg", "jpeg", "png", "webp", "gif", "mp4", "mov", "avi"],
    accept_multiple_files=True,
    help="Fotoğraf: JPG, PNG, WEBP — Video: MP4, MOV, AVI (ilk kare analiz edilir)"
)

medya_verileri = []

if yuklenen_dosyalar:
    onizleme_cols = st.columns(min(len(yuklenen_dosyalar), 4))
    for i, dosya in enumerate(yuklenen_dosyalar):
        mime = dosya.type
        veri = dosya.read()
        b64 = base64.b64encode(veri).decode("utf-8")

        if mime.startswith("image/"):
            with onizleme_cols[i % 4]:
                st.image(veri, caption=dosya.name, use_container_width=True)
            medya_verileri.append({"mime_type": mime, "b64": b64, "isim": dosya.name})

        elif mime.startswith("video/"):
            with onizleme_cols[i % 4]:
                st.video(veri)
                st.caption(dosya.name)
            try:
                import tempfile, cv2
                from PIL import Image
                import io

                with tempfile.NamedTemporaryFile(suffix=Path(dosya.name).suffix, delete=False) as tmp:
                    tmp.write(veri)
                    tmp_path = tmp.name

                cap = cv2.VideoCapture(tmp_path)
                ret, frame = cap.read()
                cap.release()
                os.unlink(tmp_path)

                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=85)
                    kare_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                    medya_verileri.append({
                        "mime_type": "image/jpeg",
                        "b64": kare_b64,
                        "isim": f"{dosya.name} (ilk kare)"
                    })
                    st.caption(f"ℹ️ {dosya.name}: İlk kare analiz edilecek")
                else:
                    st.warning(f"⚠️ {dosya.name}: Video karesi okunamadı.")
            except ImportError:
                st.warning(f"⚠️ Video işleme için `opencv-python-headless` ve `Pillow` gerekli.")
            except Exception as ex:
                st.warning(f"⚠️ {dosya.name} işlenirken hata: {ex}")

    if medya_verileri:
        st.info("🔍 Görsel içerik tespit edildi — vision modeli ile ön analiz yapılacak.")

baslat = st.button("🚀 Simülasyonu Başlat", type="primary", use_container_width=True)

# ── Simülasyon ────────────────────────────────────────────────────────────────
if baslat and olay.strip():
    try:
        from crew_setup import isg_ekibi_olustur
    except EnvironmentError as env_err:
        st.error(f"⚙️ Yapılandırma hatası: {env_err}")
        st.stop()

    result_holder: dict = {}

    with st.spinner("🔍 İSG Ekibi olayı değerlendiriyor..."):
        try:
            if medya_verileri:
                st.toast("🖼️ Görseller analiz ediliyor...", icon="🔍")

            crew = isg_ekibi_olustur(
                olay_metni=olay,
                medya_verileri=medya_verileri,
            )
            crew_output = crew.kickoff()
            result_holder["output"] = (
                crew_output.raw if hasattr(crew_output, "raw") else str(crew_output)
            )
        except Exception as e:
            st.error(f"❌ Hata oluştu: {e}")
            st.info(
                "💡 Kontrol listesi:\n"
                "- GROQ_API_KEY doğru mu?\n"
                "- Groq rate limit dolmadı mı?\n"
                "- İnternet bağlantısı var mı?"
            )
            st.stop()

    st.success("✅ İSG Değerlendirme Süreci Tamamlandı!")

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

st.divider()
st.caption("© 2025 Sanal İSG Ofisi | CrewAI + Groq + Streamlit ile geliştirilmiştir.")