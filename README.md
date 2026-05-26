# 🦺 Sanal İSG Ofisi (Dijital İkiz Prototip)

**İş Sağlığı ve Güvenliği süreçlerini yapay zeka ajanlarıyla simüle eden, Streamlit tabanlı bir dijital ikiz prototipi.**

Bu proje, bir şirketteki İSG Müdürü, İSG Uzmanı ve Raporlama Sorumlusu rollerini otonom yapay zeka ajanları olarak modeller. Kullanıcının bildirdiği bir iş kazası veya ramak kala olayı, ajanlar tarafından analiz edilir, düzeltici/önleyici faaliyetler (DÖF) oluşturulur ve resmi bir rapor hazırlanır. Amaç, kurumsal İSG süreçlerinin yapay zeka ile nasıl otomatize edilebileceğini göstermektir.

## 🎯 Proje Amacı

- Şirket pozisyonlarının görev tanımlarını temel alan otonom ajanlar oluşturmak.
- İş kazası bildirimlerinde hızlı, tutarlı ve mevzuata uygun analiz, karar ve raporlama sürecini simüle etmek.
- Çok ajanlı sistemlerin (CrewAI) kurumsal iş akışlarına nasıl entegre edilebileceğini göstermek.
- Streamlit ile son kullanıcıya basit bir web arayüzü sunmak.

## 🧠 Mimari ve Kullanılan Teknolojiler

- **[CrewAI](https://www.crewai.com/):** Çoklu yapay zeka ajanlarını roller, hedefler ve görevlerle tanımlamak ve yönetmek için.
- **[Streamlit](https://streamlit.io/):** Kullanıcı etkileşimi için hızlı web arayüzü.
- **[LangChain](https://www.langchain.com/) (CrewAI altında kullanılır):** LLM entegrasyonu ve bellek yönetimi.
- **OpenAI API (GPT-4 önerilir):** Ajanların dil modeli olarak. (Opsiyonel: Azure OpenAI, Gemini, vb.)
- **Python 3.10+**

**Ajanlar ve Sorumlulukları:**
| Ajan | Rolü | Sorumlulukları |
|------|------|----------------|
| İSG Uzmanı | Olay yeri inceleme | Olayı sınıflandırma, kök neden analizi (5 Neden), aciliyet belirleme |
| İSG Müdürü | Yönetim ve onay | Uzman analizini denetleme, DÖF tanımlama, sorumlu atama, yasal uygunluk kontrolü |
| Raporlama Sorumlusu | Dokümantasyon | Resmi İş Kazası Raporu ve Düzeltici Faaliyet Formu oluşturma |

**İş Akışı:**  
Olay Bildirimi → Uzman Analizi → Müdür Değerlendirmesi ve DÖF → Resmi Rapor

## 📁 Proje Yapısı
isg-dijital-ofis/
├── agents.py # Ajan tanımları (roller, hedefler, background)
├── tasks.py # Görev zincirleri (olay analizi, onay, raporlama)
├── crew_setup.py # Crew (ekip) ve süreç konfigürasyonu
├── app.py # Streamlit web arayüzü
├── requirements.txt # Python bağımlılıkları
├── .env.example # API anahtarı örnek dosyası
└── README.md


## 🚀 Kurulum ve Çalıştırma

### 1. Gereksinimler
- Python 3.10 veya üstü
- Git (opsiyonel)
- OpenAI API anahtarı (veya diğer LLM sağlayıcısı)

### 2. Repoyu Klonlayın
```bash
git clone https://github.com/kullaniciadi/isg-dijital-ofis.git
cd isg-dijital-ofis

### 3. Sanal Ortam ve Bağımlılıklar

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

4. API Anahtarını Tanımlayın
.env.example dosyasını .env olarak kopyalayın ve kendi OpenAI API anahtarınızı yazın:

bash
cp .env.example .env
.env dosyası içeriği:

text
OPENAI_API_KEY=sk-...
(.env dosyası zaten .gitignore içinde olmalı, asla paylaşmayın!)

5. Uygulamayı Başlatın
bash
streamlit run app.py
Tarayıcınızda açılan arayüze bir iş kazası bildirimi yazın ve simülasyonu başlatın.

🧪 Örnek Senaryo
Girdi:
"Pazartesi sabahı, üretim hattında bir operatör, koruyucu siperi kaldırılmış makineye parça yerleştirirken parmağını sıkıştırdı. İş ayakkabısı ve eldiveni vardı ancak siper devre dışı bırakılmış."

Beklenen Çıktı (Rapor):

Olay türü: İş kazası

Kök neden: Makine koruyucusunun kasıtlı olarak devre dışı bırakılması, denetim eksikliği

DÖF 1: Tüm makinelerde koruyucu donanımın çalışır durumda olduğunun günlük kontrolü (Sorumlu: Bakım Şefi, Süre: 1 hafta)

DÖF 2: Operatörlere "Kilitleme-Etiketleme" eğitimi verilmesi (Sorumlu: İSG Uzmanı, Süre: 2 hafta)

Resmi rapor başlıkları ve aksiyon planı.

📌 Geliştirme Planı (Yol Haritası)
Ara adımları Streamlit sohbet baloncuklarında canlı gösterme (StepCallback)

Olay veritabanı (SQLite) ile kalıcı kayıt ve geçmiş görüntüleme

E‑posta veya webhook ile gerçek bildirim gönderme

Risk değerlendirme matrisi oluşturan ek ajan

Çok departmanlı genişletme (Üretim, İK, Satın Alma dahil)

Farklı LLM sağlayıcıları için yapılandırma (Azure OpenAI, Gemini, yerel modeller)

🤝 Katkıda Bulunun
Proje fikir aşamasındadır ve katkılara açıktır. Pull request göndermekten çekinmeyin. Büyük değişiklikler için lütfen önce bir issue açarak tartışalım.

📄 Lisans
MIT Lisansı altında sunulmaktadır. İşletmenizin ihtiyaçlarına göre uyarlayabilirsiniz.