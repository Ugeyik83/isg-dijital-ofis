import streamlit as st
from crew_setup import isg_ekibi_olustur
import time

st.set_page_config(page_title="Sanal İSG Ofisi", layout="wide")
st.title("🦺 Sanal İSG Ofisi (Dijital İkiz Prototip)")
st.markdown("Bir iş kazası, ramak kala veya sağlık olayı bildirimi yapın; ajanlar iş başına geçsin.")

# Kullanıcıdan olay açıklaması al
olay = st.text_area("Olay Açıklaması", height=150, 
                    placeholder="Örn: Dün vardiyada depo bölümünde bir çalışan ıslak zeminde kaydı, kolunu incitti. İlk yardım yapıldı.")

if st.button("🚀 Simülasyonu Başlat") and olay.strip():
    # Ajanların çıktılarını saklamak için bir konteyner
    output_container = st.empty()
    logs = []
    
    # CrewAI'nin verbose çıktısını yakalamak ve göstermek zor, bu yüzden adım adım 
    # görselleştireceğiz. Crew çalıştırıldığında sırayla ajanlar konuşacak.
    with st.spinner("🔍 İSG Ekibi olayı değerlendiriyor..."):
        try:
            crew = isg_ekibi_olustur(olay)
            # CrewAI 'kickoff' doğrudan sonucu döndürür, ara çıktıları almak için
            # biraz hack gerekebilir. Bu basit örnekte son raporu göstereceğiz.
            sonuc = crew.kickoff()
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
            st.stop()
    
    # Sonucu göster
    st.success("✅ İSG Süreci Tamamlandı!")
    st.markdown("### 📋 Nihai Rapor ve DÖF Formu")
    st.markdown(sonuc)
    
    # Eğer ara adımları da sohbet şeklinde göstermek isterseniz, CrewAI'nin 
    # callback'lerini kullanarak ajan konuşmalarını yakalayıp sohbet baloncukları 
    # olarak ekleyebiliriz. İlk prototipte son rapor yeterlidir.
else:
    st.info("Lütfen bir olay açıklaması girin ve butona tıklayın.")