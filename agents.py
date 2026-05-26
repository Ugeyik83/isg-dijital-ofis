import os
from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise EnvironmentError(
        "GROQ_API_KEY bulunamadı. "
        "Streamlit Cloud: Settings → Secrets → GROQ_API_KEY = 'gsk_...'"
    )

# ── LLM fabrikası ─────────────────────────────────────────────────────────────
# Görsel varsa vision modeli, yoksa standart model kullanılır.
# Groq vision: llama-3.2-11b-vision-preview
# Groq standart: llama-3.3-70b-versatile

STANDART_MODEL = os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-versatile")
VISION_MODEL   = os.getenv("LLM_VISION_MODEL", "llama-3.2-11b-vision-preview")


def llm_olustur(vision: bool = False) -> LLM:
    """Standart veya vision LLM nesnesi döndürür."""
    model_adi = VISION_MODEL if vision else STANDART_MODEL
    if not model_adi.startswith("groq/"):
        model_adi = f"groq/{model_adi}"
    return LLM(model=model_adi, api_key=groq_api_key, temperature=0.1)


def ajanlar_olustur(vision: bool = False):
    """İSG ajan üçlüsünü oluşturup döndürür.

    Args:
        vision: True ise vision modeli kullanılır (görsel içerik varsa).

    Returns:
        (isg_uzmani, isg_muduru, raporlama_ajani) tuple'ı.
    """
    llm = llm_olustur(vision=vision)
    model_log = VISION_MODEL if vision else STANDART_MODEL
    print(f"✅ CrewAI LLM başarıyla yapılandırıldı: groq/{model_log}")

    _base = {"llm": llm, "verbose": True, "allow_delegation": False}

    isg_uzmani = Agent(
        role="İSG Uzmanı",
        goal=(
            "Olayları yerinde inceleyerek kök neden analizi yapmak "
            "ve ilk değerlendirme raporu hazırlamak."
        ),
        backstory=(
            "Sen, sahada aktif çalışan deneyimli bir İSG uzmanısın. Her olayda hemen "
            "olay yerine gider, tanık ifadelerini toplar, fiziksel kanıtları ve "
            "varsa fotoğraf/video kayıtlarını inceler; '5 Neden' yöntemiyle temel "
            "nedeni bulursun. Teknik ve objektif bir dil kullanırsın.\n\n"
            "Önemli: Yanıtlarını her zaman Türkçe ver (DÖF, KKD, LOTO vb.)."
        ),
        **_base
    )

    isg_muduru = Agent(
        role="İSG Müdürü",
        goal=(
            "İSG süreçlerini yönetmek, yasal uygunluğu sağlamak, "
            "düzeltici faaliyetleri onaylamak ve üst yönetime raporlamak."
        ),
        backstory=(
            "Sen 15 yıllık İSG yönetimi tecrübesine sahip bir müdürsün. "
            "Uzmanın bulgularını değerlendirir, 4857 ve 6331 sayılı kanunlara "
            "uygunluğu kontrol eder, DÖF'leri onaylar.\n\n"
            "Önemli: Yanıtlarını her zaman Türkçe ver."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )

    raporlama_ajani = Agent(
        role="Raporlama ve Dokümantasyon Sorumlusu",
        goal="Resmi olay kaydı ve düzeltici faaliyet formunu kusursuz şekilde hazırlamak.",
        backstory=(
            "Sen titiz bir dokümantasyon uzmanısın. İSG mevzuatına uygun formatları "
            "bilirsin. Her raporu Türkçe ve resmi formatta hazırlarsın. "
            "Tarih formatı GG.AA.YYYY olmalı."
        ),
        **_base
    )

    return isg_uzmani, isg_muduru, raporlama_ajani