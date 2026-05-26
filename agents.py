import os
from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

# ── API anahtarı ve model yapılandırması ──────────────────────────────────────
groq_api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-versatile")

if not groq_api_key:
    raise EnvironmentError(
        "GROQ_API_KEY bulunamadı. "
        "Streamlit Cloud: Settings → Secrets → GROQ_API_KEY = 'gsk_...'"
    )

# "groq/" prefix yoksa ekle — LiteLLM provider routing için gerekli
if not model_name.startswith("groq/"):
    model_name = f"groq/{model_name}"

# ── Groq uyumluluk düzeltmesi ─────────────────────────────────────────────────
# CrewAI 1.14.x, Anthropic prompt-caching için mesajlara cache_breakpoint /
# cache_control alanları ekliyor. Groq bu alanları reddediyor.
# Çözüm 1: LITELLM_DROP_PARAMS — LiteLLM bilinmeyen parametreleri atar.
# Çözüm 2: ANTHROPIC_CACHE_ENABLED=false — CrewAI cache injection'ı kapatır.
# İkisini birden set ediyoruz; hangisi önce devreye girirse kazanır.
os.environ["LITELLM_DROP_PARAMS"] = "true"
os.environ["ANTHROPIC_CACHE_ENABLED"] = "false"

# ── LLM nesnesi (CrewAI 1.x — crewai.LLM) ────────────────────────────────────
llm = LLM(
    model=model_name,
    api_key=groq_api_key,
    temperature=0.1,
)

print(f"✅ CrewAI LLM başarıyla yapılandırıldı: {model_name}")

# ── Ortak ajan parametreleri ──────────────────────────────────────────────────
_base = {
    "llm": llm,
    "verbose": True,
    "allow_delegation": False,
}

# ── Ajan Tanımları ────────────────────────────────────────────────────────────

isg_uzmani = Agent(
    role="İSG Uzmanı",
    goal=(
        "Olayları yerinde inceleyerek kök neden analizi yapmak "
        "ve ilk değerlendirme raporu hazırlamak."
    ),
    backstory=(
        "Sen, sahada aktif çalışan deneyimli bir İSG uzmanısın. Her olayda hemen "
        "olay yerine gider, tanık ifadelerini toplar, fiziksel kanıtları inceler ve "
        "'5 Neden' gibi yöntemlerle temel nedeni bulursun. Teknik ve objektif bir dil "
        "kullanırsın.\n\n"
        "Önemli: Yanıtlarını her zaman Türkçe ver. İş Sağlığı ve Güvenliği "
        "terminolojisini Türkçe kullan (örneğin: DÖF, KKD, LOTO)."
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
        "Sen 15 yıllık İSG yönetimi tecrübesine sahip bir müdürsün. Şirketin tüm "
        "İSG politikalarından sorumlusun. Uzmanın bulgularını değerlendirir, yasal "
        "mevzuata (4857, 6331 sayılı kanunlar) uygunluğu kontrol eder, bütçe ve iş "
        "gücü planlaması yaparak DÖF'leri onaylar ve gerektiğinde diğer departmanlara "
        "iş atarsın.\n\n"
        "Önemli: Yanıtlarını her zaman Türkçe ver. Resmi bir dil kullan ama anlaşılır ol."
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
        "bilirsin. Elindeki verilerle 'İş Kazası Bildirim Formu' ve 'Düzeltici Faaliyet "
        "Talimatı'nı hatasız doldurursun. Her raporu Türkçe ve resmi formatta "
        "hazırlarsın.\n\n"
        "Önemli: Tüm çıktılarını Türkçe oluştur. Tarih formatı GG.AA.YYYY olmalı."
    ),
    **_base
)
