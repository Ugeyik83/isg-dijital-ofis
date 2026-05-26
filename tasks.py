from crewai import Task


def olay_bildirimi_gorevi(
    olay_metni: str,
    gorsel_bulgular: str,
    medya_isimleri: list,
    ajanlar: tuple,
):
    """Görev zincirini oluşturur.

    Args:
        olay_metni: Kullanıcının metin açıklaması.
        gorsel_bulgular: Vision API'den gelen Türkçe bulgu metni (boş olabilir).
        medya_isimleri: Yüklenen dosya adları listesi.
        ajanlar: (isg_uzmani, isg_muduru, raporlama_ajani) tuple'ı.
    """
    isg_uzmani, isg_muduru, raporlama_ajani = ajanlar
    gorsel_var = bool(gorsel_bulgular)

    # ── Görsel bulgu bloğu ────────────────────────────────────────────────────
    if gorsel_var:
        gorsel_blok = (
            f"\n\n--- GÖRSEL KANIT ANALİZİ ({len(medya_isimleri)} dosya) ---\n"
            f"Yüklenen dosyalar: {', '.join(medya_isimleri)}\n\n"
            f"Vision AI bulguları:\n{gorsel_bulgular}\n"
            "--- GÖRSEL ANALİZ SONU ---\n"
        )
    else:
        gorsel_blok = ""

    # ── Görev 1: İSG Uzmanı ───────────────────────────────────────────────────
    analiz_gorevi = Task(
        description=(
            f"Aşağıdaki olay bildirimini Türkçe olarak analiz et:\n\n"
            f"OLAY AÇIKLAMASI:\n{olay_metni}"
            f"{gorsel_blok}\n\n"
            "Lütfen şunları yap:\n"
            "1. Olayın türünü belirle (iş kazası, ramak kala, meslek hastalığı)\n"
            "2. '5 Neden' yöntemiyle kök nedenleri sırala\n"
            "3. Acil önlem alınması gerekip gerekmediğini değerlendir\n"
            "4. İlgili İSG mevzuatına (6331 sayılı kanun) atıfta bulun\n"
            + ("5. Görsel kanıt analizindeki bulguları kök neden analizine dahil et\n"
               if gorsel_var else "")
            + "\nYanıtın tamamen Türkçe olmalı."
        ),
        expected_output=(
            "Olay türü, kök nedenler listesi, aciliyet durumu, mevzuat referansı"
            + (", görsel bulgular değerlendirmesi" if gorsel_var else "")
            + " içeren Türkçe analiz."
        ),
        agent=isg_uzmani,
    )

    # ── Görev 2: İSG Müdürü ──────────────────────────────────────────────────
    onay_ve_aksiyon_gorevi = Task(
        description=(
            "İSG Uzmanının yaptığı analizi değerlendir ve Türkçe olarak şunları yap:\n"
            "1. Kök nedenleri yeterli bulup bulmadığını belirt\n"
            "2. En az 2 düzeltici/önleyici faaliyet (DÖF) tanımla\n"
            "3. Her DÖF için sorumlu kişi/departman ve tahmini tamamlanma süresi belirle\n"
            "4. Bütçe gerekiyorsa yaklaşık maliyet öngör\n"
            "5. Uzmanın kök neden analizi 5 adımdan azsa veya mevzuat referansı eksikse, bunu DÖF önerilerinin başında açıkça belirt ve eksik analizi kendin tamamla.\n\n"
            "Resmi bir dil kullan ama anlaşılır ol. Türkçe yaz."
        ),
        expected_output="Onay durumu, en az 2 DÖF (açıklama, sorumlu, süre, bütçe), ek öneriler. Türkçe.",
        agent=isg_muduru,
    )

    # ── Görev 3: Raporlama ────────────────────────────────────────────────────
    rapor_gorevi = Task(
        description=(
            "Elindeki tüm bilgileri kullanarak Türkçe resmi rapor oluştur. "
            "Şu başlıkları içermeli:\n\n"
            "İŞ KAZASI / OLAY RAPORU\n"
            "- Olay Tarihi: (bugünün tarihi)\n"
            "- Olay Yeri ve Saati\n"
            "- Olayın Tanımı\n"
            "- Yaralanma/Hasar Durumu\n"
            "- Kök Neden Analizi\n"
            + ("- Görsel Kanıt Özeti\n" if gorsel_var else "")
            + "- Yapılan Müdahaleler\n\n"
            "DÜZELTİCİ FAALİYET FORMU\n"
            "- DÖF No, Açıklama, Sorumlu, Başlangıç, Bitiş, Durum\n\n"
            "Format temiz ve profesyonel olsun. Tamamen Türkçe."
        ),
        expected_output="Biçimlendirilmiş, başlıklar halinde düzenlenmiş tam Türkçe rapor.",
        agent=raporlama_ajani,
    )

    return [analiz_gorevi, onay_ve_aksiyon_gorevi, rapor_gorevi]