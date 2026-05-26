import streamlit as st
import os
from crew_setup import isg_ekibi_olustur

# Streamlit secrets'tan yapılandırma (production için)
if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
    os.environ['GROQ_API_KEY'] = st.secrets['GROQ_API_KEY']
    os.environ['LLM_PROVIDER'] = st.secrets.get('LLM_PROVIDER', 'groq')
    os.environ['LLM_MODEL_NAME'] = st.secrets.get('LLM_MODEL_NAME', 'llama-3.3-70b-versatile')

st.set_page_config(
    page_title="Sanal İSG Ofisi",
    page_icon="🦺",
    layout="wide"
)

st.title("🦺 Sanal İSG Ofisi (Dijital İkiz Prototip)")
st.markdown("""
Bir iş kazası, ramak kala veya sağlık olayı bildirimi yapın; 
**İSG Uzmanı**, **İSG Müdürü** ve **Raporlama Sorumlusu** ajanları iş başına geçsin.
""")

# Sidebar bilgi
with st.sidebar:
    st.header("⚙️ Sistem Bilgisi")
    st.info(f"""
    **Kullanılan Model:** {os.getenv('LLM_MODEL_NAME', 'llama-3.3-70b-versatile')}
    
    **Aktif Ajanlar:**
    - 🧑‍🔧 İSG Uzmanı
    - 👨‍💼 İSG Müdürü
    - 📋 Raporlama Sorumlusu
    """)
    
    st.divider()
    st.caption("v1.0 - Dijital İkiz Prototip")

# Ana girdi alanı
col1, col2 = st.columns([2, 1])

with col1:
    olay = st.text_area(
        "📝 Olay Açıklaması",
        height=180,
        placeholder="Örn: Dün vardiyada depo bölümünde bir çalışan ıslak zeminde kaydı, "
                   "kolunu incitti. İlk yardım yapıldı. Zemin yeni temizlenmiş ama uyarı "
                   "levhası konmamıştı. Çalışanın kaymaz ayakkabısı vardı."
    )

with col2:
    st.markdown("### Örnek Senaryolar")
    st.button(
        "🏭 Makine Kazası",
        help="Operatör koruyucusuz makinede parmağını sıkıştırdı",
        on_click=lambda: st.session_state.update(
            {'olay_ornek': "Pazartesi sabahı, üretim hattında bir operatör koruyucu siperi "
                          "kaldırılmış makineye parça yerleştirirken parmağını sıkıştırdı. "
                          "İş ayakkabısı ve eldiveni vardı ancak siper devre dışı bırakılmış."}
        )
    )
    st.button(
        "🧪 Kimyasal Sızıntı",
        help="Laboratuvarda asit buharı soluyan teknisyen",
        on_click=lambda: st.session_state.update(
            {'olay_ornek': "Kimya laboratuvarında çalışan bir teknisyen, çeker ocak "
                          "çalışmadığı için asit buharına maruz kaldı. Solunum zorluğu "
                          "şikayetiyle revire gitti."}
        )
    )

# Buton
baslat = st.button("🚀 Simülasyonu Başlat", type="primary", use_container_width=True)

# Otomatik doldurma
if 'olay_ornek' in st.session_state and not olay:
    olay = st.session_state['olay_ornek']

if baslat and olay.strip():
    with st.spinner("🔍 İSG Ekibi olayı değerlendiriyor..."):
        try:
            # Progress bar
            progress_bar = st.progress(0, text="🔄 Olay analiz ediliyor...")
            
            crew = isg_ekibi_olustur(olay)
            
            progress_bar.progress(30, text="🔍 İSG Uzmanı kök neden analizi yapıyor...")
            sonuc = crew.kickoff()
            
            progress_bar.progress(80, text="📋 Rapor hazırlanıyor...")
            progress_bar.progress(100, text="✅ Tamamlandı!")
            progress_bar.empty()
            
        except Exception as e:
            st.error(f"❌ Hata oluştu: {str(e)}")
            st.info("💡 Kontrol edin: GROQ_API_KEY doğru mu? İnternet bağlantınız var mı?")
            st.stop()
    
    # Sonuç gösterimi
    st.success("✅ İSG Değerlendirme Süreci Tamamlandı!")
    
    # Sekmeler halinde göster
    tab1, tab2 = st.tabs(["📋 Rapor", "📝 Ham Çıktı"])
    
    with tab1:
        st.markdown(sonuc)
    
    with tab2:
        st.code(sonuc, language="markdown")
    
    # İndirme butonu
    st.download_button(
        label="📥 Raporu İndir (TXT)",
        data=str(sonuc),
        file_name=f"isg_raporu_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
    
elif baslat:
    st.warning("⚠️ Lütfen önce bir olay açıklaması girin.")

# Footer
st.divider()
st.caption("© 2024 Sanal İSG Ofisi | CrewAI + Groq + Streamlit ile geliştirilmiştir.")
