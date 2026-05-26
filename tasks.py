from crewai import Task
from agents import isg_uzmani, isg_muduru, raporlama_ajani

def olay_bildirimi_gorevi(olay_metni):
    """Kullanıcının girdiği olay metnini alan görev zinciri."""
    
    analiz_gorevi = Task(
        description=f"""Aşağıdaki olay bildirimini analiz et:
        
        OLAY: {olay_metni}
        
        - Olayın türünü (iş kazası, ramak kala, meslek hastalığı) belirle.
        - Olası kök nedenleri '5 Neden' ile sırala.
        - Acil önlem alınması gerekip gerekmediğini söyle.""",
        expected_output="Olay türü, kök nedenler listesi, aciliyet durumu.",
        agent=isg_uzmani
    )
    
    onay_ve_aksiyon_gorevi = Task(
        description="""İSG Uzmanının yaptığı analizi değerlendir:
        - Kök nedenleri yeterli buluyor musun?
        - En az iki düzeltici/önleyici faaliyet (DÖF) tanımla.
        - Faaliyetlerin sorumlusunu ve tahmini tamamlanma süresini belirle.""",
        expected_output="Onay durumu, 2 adet DÖF (açıklama, sorumlu, süre), ek öneriler.",
        agent=isg_muduru
    )
    
    rapor_gorevi = Task(
        description="""Elindeki tüm bilgileri kullanarak resmi bir 'İş Kazası / Olay Raporu' 
        ve 'Düzeltici Faaliyet Formu' oluştur. Formatta şu başlıklar bulunsun: 
        Olay Tarihi, Olay Yeri, Açıklama, Kök Neden, Yapılan DÖF'ler, Sorumlu, Son Tarih.""",
        expected_output="Biçimlendirilmiş, başlıklar halinde düzenlenmiş tam rapor metni.",
        agent=raporlama_ajani
    )
    
    return [analiz_gorevi, onay_ve_aksiyon_gorevi, rapor_gorevi]