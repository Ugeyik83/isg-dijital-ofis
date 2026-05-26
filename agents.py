import os
from crewai import Agent
from dotenv import load_dotenv

load_dotenv()

# Groq API anahtarını al
groq_api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-versatile")

# CrewAI 0.30+ sürümünde LLM string olarak belirtilebilir
# veya uyumlu bir LangChain LLM nesnesi kullanılabilir
try:
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        temperature=0.1,
        groq_api_key=groq_api_key,
        model_name=model_name
    )
    print(f"✅ Groq LLM başarıyla yüklendi: {model_name}")
except ImportError:
    print("⚠️ langchain-groq bulunamadı, varsayılan yapılandırma kullanılıyor")
    # Alternatif: CrewAI'nin kendi LLM yapılandırmasını kullan
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_API_KEY"] = groq_api_key
    os.environ["OPENAI_MODEL_NAME"] = model_name
    llm = None  # CrewAI varsayılan olarak OPENAI_* env değişkenlerini kullanır

# Ajanları oluştur
agent_kwargs = {
    "verbose": True,
    "allow_delegation": False
}

# Eğer LLM başarıyla yüklendiyse ekle
if llm is not None:
    agent_kwargs["llm"] = llm

isg_uzmani = Agent(
    role="İSG Uzmanı",
    goal="Olayları yerinde inceleyerek kök neden analizi yapmak ve ilk değerlendirme raporu hazırlamak.",
    backstory="""Sen, sahada aktif çalışan deneyimli bir İSG uzmanısın. Her olayda hemen 
    olay yerine gider, tanık ifadelerini toplar, fiziksel kanıtları inceler ve '5 Neden' 
    gibi yöntemlerle temel nedeni bulursun. Teknik ve objektif bir dil kullanırsın.
    
    Önemli: Yanıtlarını her zaman Türkçe ver. İş Sağlığı ve Güvenliği terminolojisini
    Türkçe kullan (örneğin: DÖF - Düzeltici Önleyici Faaliyet, KKD - Kişisel Koruyucu Donanım).""",
    **agent_kwargs
)

isg_muduru = Agent(
    role="İSG Müdürü",
    goal="İSG süreçlerini yönetmek, yasal uygunluğu sağlamak, düzeltici faaliyetleri onaylamak ve üst yönetime raporlamak.",
    backstory="""Sen 15 yıllık İSG yönetimi tecrübesine sahip bir müdürsün. Şirketin tüm 
    İSG politikalarından sorumlusun. Uzmanın bulgularını değerlendirir, yasal mevzuata 
    (4857, 6331 sayılı kanunlar vb.) uygunluğu kontrol eder, bütçe ve iş gücü planlaması 
    yaparak DÖF'leri onaylar ve gerektiğinde üretim müdürü gibi diğer departmanlara iş atarsın.
    
    Önemli: Yanıtlarını her zaman Türkçe ver. Resmi bir dil kullan ama anlaşılır ol.""",
    allow_delegation=True,
    **{k: v for k, v in agent_kwargs.items() if k != "allow_delegation"}
)

raporlama_ajani = Agent(
    role="Raporlama ve Dokümantasyon Sorumlusu",
    goal="Resmi olay kaydı ve düzeltici faaliyet formunu kusursuz şekilde hazırlamak.",
    backstory="""Sen titiz bir dokümantasyon uzmanısın. İSG mevzuatına uygun formatları bilirsin. 
    Elindeki verilerle 'İş Kazası Bildirim Formu' ve 'Düzeltici Faaliyet Talimatı'nı 
    hatasız doldurursun. Her raporu Türkçe ve resmi formatta hazırlarsın.
    
    Önemli: Tüm çıktılarını Türkçe oluştur. Tarih formatı GG.AA.YYYY şeklinde olmalı.""",
    **agent_kwargs
)