import os
from crewai import Crew, Process
from agents import isg_uzmani, isg_muduru, raporlama_ajani
from tasks import olay_bildirimi_gorevi

# ── Groq uyumluluk düzeltmesi ─────────────────────────────────────────────────
# CrewAI 1.14.x mesajlara Anthropic prompt-caching alanları (cache_breakpoint,
# cache_control) ekliyor. Groq bu alanları reddediyor → BadRequestError.
# LITELLM_DROP_PARAMS=true ile litellm bilinmeyen parametreleri sessizce atar.
os.environ["LITELLM_DROP_PARAMS"] = "true"


def isg_ekibi_olustur(olay_metni):
    """Verilen olay metni için İSG ekibini yapılandırıp döndürür."""
    gorevler = olay_bildirimi_gorevi(olay_metni)

    return Crew(
        agents=[isg_uzmani, isg_muduru, raporlama_ajani],
        tasks=gorevler,
        process=Process.sequential,
        verbose=True,
    )