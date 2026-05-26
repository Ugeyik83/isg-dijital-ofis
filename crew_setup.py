from crewai import Crew, Process
from agents import isg_uzmani, isg_muduru, raporlama_ajani
from tasks import olay_bildirimi_gorevi

def isg_ekibi_olustur(olay_metni):
    """Verilen olay için İSG ekibini döndürür."""
    gorevler = olay_bildirimi_gorevi(olay_metni)
    
    return Crew(
        agents=[isg_uzmani, isg_muduru, raporlama_ajani],
        tasks=gorevler,
        process=Process.sequential,  # Sıralı iş akışı
        verbose=True
    )