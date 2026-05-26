from crewai import Task
from agents import isg_uzmani, isg_muduru, raporlama_ajani

def olay_bildirimi_gorevi(olay_metni):
    """Kullanıcının girdiği olay metnini alan görev zinciri."""
    
    analiz_gorevi = Task(
        description=f"""Aşağıdaki olay bildirimini Türkçe olarak analiz et:
        
        OLAY: {olay_metni}
        
        Lütfen şunları yap:
        1. Olayın türünü belirle (iş kazası, ramak kala, meslek hastalığı)
        2. '5 Neden' yöntemiyle kök nedenleri sırala
        3. Acil önlem alınması gerekip gerekmediğini değerlendir
        4. İlgili İSG mevzuatına (6331 sayılı kanun) atıfta bulun
        
        Yanıtın tamamen Türkçe olmalı.""",
        expected_output="Olay türü, kök nedenler listesi, aciliyet durumu ve mevzuat referansı içeren Türkçe analiz.",
        agent=isg_uzmani
    )
    
    onay_ve_aksiyon_gorevi = Task(
        description="""İSG Uzmanının yaptığı analizi değerlendir ve Türkçe olarak şunları yap:
        1. Kök nedenleri yeterli bulup bulmadığını belirt
        2. En az 2 düzeltici/önleyici faaliyet (DÖF) tanımla
        3. Her DÖF için sorumlu kişi/departman ve tahmini tamamlanma süresi belirle
        4. Bütçe gerekiyorsa yaklaşık maliyet öngör
        
        Resmi bir dil kullan ama anlaşılır ol. Türkçe yaz.""",
        expected_output="Onay durumu, en az 2 DÖF (açıklama, sorumlu, süre, bütçe), ek öneriler. Türkçe.",
        agent=isg_muduru
    )
    
    rapor_gorevi = Task(
        description="""Elindeki tüm bilgileri kullanarak Türkçe resmi rapor oluştur. Şu başlıkları içermeli:
        
        İŞ KAZASI / OLAY RAPORU
        - Olay Tarihi: (bugünün tarihi)
        - Olay Yeri ve Saati
        - Olayın Tanımı
        - Yaralanma/Hasar Durumu
        - Kök Neden Analizi
        - Yapılan Müdahaleler
        
        DÜZELTİCİ FAALİYET FORMU
        - DÖF No, Açıklama, Sorumlu, Başlangıç, Bitiş, Durum
        
        Format temiz ve profesyonel olsun. Tamamen Türkçe.""",
        expected_output="Biçimlendirilmiş, başlıklar halinde düzenlenmiş tam Türkçe rapor.",
        agent=raporlama_ajani
    )
    
    return [analiz_gorevi, onay_ve_aksiyon_gorevi, rapor_gorevi]
