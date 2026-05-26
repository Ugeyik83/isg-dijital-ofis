import os
import json
import requests
from crewai import Crew, Process
from agents import ajanlar_olustur
from tasks import olay_bildirimi_gorevi


def gorsel_on_analizi(medya_verileri: list) -> str:
    """Groq vision API ile görselleri önceden analiz eder.

    CrewAI'nin multimodal mesaj desteği Groq için sınırlı olduğundan,
    görselleri önce vision API'ye gönderip metin bulgusunu döndürüyoruz.
    Bu metin daha sonra task description'a ekleniyor.

    Args:
        medya_verileri: [{"mime_type": ..., "b64": ..., "isim": ...}]

    Returns:
        Vision modelin Türkçe bulgu metni.
    """
    if not medya_verileri:
        return ""

    api_key = os.getenv("GROQ_API_KEY")
    vision_model = os.getenv("LLM_VISION_MODEL", "llama-3.2-11b-vision-preview")

    # Multimodal mesaj: tüm görselleri tek sorguda gönder
    content = [
        {
            "type": "text",
            "text": (
                "Sen deneyimli bir İSG (İş Sağlığı ve Güvenliği) uzmanısın. "
                "Aşağıdaki olay görsel(ler)ini incele ve Türkçe olarak şunları belirt:\n"
                "1. Tespit ettiğin tehlike kaynakları ve güvensiz durumlar\n"
                "2. KKD (Kişisel Koruyucu Donanım) eksiklikleri\n"
                "3. Çevre koşulları (zemin, aydınlatma, düzen)\n"
                "4. Hasar veya yaralanma boyutu (görünür ise)\n"
                "5. Dikkat çeken diğer İSG bulgular\n\n"
                "Sadece görselde net olarak gördüklerini belirt, tahmin etme."
            )
        }
    ]
    for m in medya_verileri:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{m['mime_type']};base64,{m['b64']}"}
        })

    payload = {
        "model": vision_model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 1024,
        "temperature": 0.1,
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Görsel analiz başarısız: {e}]"


def isg_ekibi_olustur(
    olay_metni: str,
    medya_verileri: list = None,
    step_callback=None,
    task_callback=None,
):
    """İSG ekibini yapılandırıp döndürür."""
    medya_verileri = medya_verileri or []

    # Görsel varsa önce vision API ile analiz et → metne çevir
    gorsel_bulgular = ""
    if medya_verileri:
        print(f"🔍 {len(medya_verileri)} görsel/video vision API ile analiz ediliyor...")
        gorsel_bulgular = gorsel_on_analizi(medya_verileri)
        print(f"✅ Görsel ön analiz tamamlandı.")

    # Standart model — artık tüm ajanlar text-only çalışır, görsel bulgular metin olarak geçti
    ajanlar = ajanlar_olustur(vision=False)

    gorevler = olay_bildirimi_gorevi(
        olay_metni=olay_metni,
        gorsel_bulgular=gorsel_bulgular,   # vision API çıktısı
        medya_isimleri=[m["isim"] for m in medya_verileri],
        ajanlar=ajanlar,
    )

    return Crew(
        agents=list(ajanlar),
        tasks=gorevler,
        process=Process.sequential,
        verbose=True,
        step_callback=step_callback,
        task_callback=task_callback,
    )