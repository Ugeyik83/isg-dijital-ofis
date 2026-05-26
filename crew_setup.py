import os
from crewai import Crew, Process
from agents import isg_uzmani, isg_muduru, raporlama_ajani
from tasks import olay_bildirimi_gorevi

# agents.py içinde zaten set ediliyor; burada da güvence olarak tekrarlıyoruz.
# (Streamlit bazı durumlarda modülleri farklı sırada import edebiliyor.)
os.environ["LITELLM_DROP_PARAMS"] = "true"
os.environ["ANTHROPIC_CACHE_ENABLED"] = "false"


def isg_ekibi_olustur(olay_metni):
    """Verilen olay metni için İSG ekibini yapılandırıp döndürür."""
    gorevler = olay_bildirimi_gorevi(olay_metni)

    return Crew(
        agents=[isg_uzmani, isg_muduru, raporlama_ajani],
        tasks=gorevler,
        process=Process.sequential,
        verbose=True,
    )
