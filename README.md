# 🦺 Sanal İSG Ofisi — Dijital İkiz Prototip

**İş Sağlığı ve Güvenliği süreçlerini otonom yapay zeka ajanlarıyla simüle eden, Streamlit tabanlı çok-ajanlı sistem.**

Kullanıcı bir iş kazası veya ramak kala bildirimi yapar; üç otonom ajan sırayla devreye girerek analiz, karar ve resmi raporlama görevlerini tamamlar.

---

## 📐 Mimari

```
Olay Bildirimi (Kullanıcı)
        │
        ▼
┌───────────────────┐
│   İSG Uzmanı      │  Olay sınıflandırma · 5 Neden analizi · Aciliyet kararı
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   İSG Müdürü      │  Analiz onayı · DÖF tanımlama · Sorumlu atama · Yasal uygunluk
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Raporlama Ajani  │  İş Kazası Raporu + Düzeltici Faaliyet Formu (Türkçe, resmi format)
└───────────────────┘
```

**Teknoloji Yığını:**

| Katman | Teknoloji |
|---|---|
| Çok-ajanlı orkestrasyon | CrewAI 1.14.5 |
| LLM | Groq API — `llama-3.3-70b-versatile` |
| LLM yönlendirme | LiteLLM (CrewAI dahili) |
| Web arayüzü | Streamlit |
| Dil | Python 3.11 |

---

## 🤖 Ajanlar

| Ajan | Rolü | Sorumlulukları |
|---|---|---|
| **İSG Uzmanı** | Saha inceleme | Olay tipi tespiti, 5 Neden kök neden analizi, 6331 sayılı kanun referansı |
| **İSG Müdürü** | Yönetim ve onay | Analiz denetimi, DÖF (Düzeltici Önleyici Faaliyet) tanımlama, bütçe ve sorumlu atama |
| **Raporlama Sorumlusu** | Dokümantasyon | İş Kazası Bildirim Formu ve Düzeltici Faaliyet Talimatı hazırlama |

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.11+
- [Groq API anahtarı](https://console.groq.com/keys) (ücretsiz tier mevcut)

### 1. Repoyu klonla

```bash
git clone https://github.com/ugeyik83/isg-dijital-ofis.git
cd isg-dijital-ofis
```

### 2. Sanal ortam oluştur

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. API anahtarını tanımla

```bash
cp .env.example .env
```

`.env` dosyasını düzenle:

```
GROQ_API_KEY=gsk_...
LLM_MODEL_NAME=llama-3.3-70b-versatile
```

### 4. Uygulamayı başlat

```bash
streamlit run app.py
```

---

## ☁️ Streamlit Cloud Deploy

1. Bu repoyu GitHub'a push et.
2. [share.streamlit.io](https://share.streamlit.io) → **New app** → repoyu seç, `app.py` belirt.
3. **Settings → Secrets** bölümüne ekle:

```toml
GROQ_API_KEY = "gsk_..."
LLM_MODEL_NAME = "llama-3.3-70b-versatile"
```

4. **Deploy** — başka yapılandırma gerekmez.

---

## 🧪 Örnek Kullanım

**Girdi:**
```
Pazartesi sabahı üretim hattında bir operatör, koruyucu siperi kaldırılmış makineye 
parça yerleştirirken parmağını sıkıştırdı. İş ayakkabısı ve eldiveni vardı ancak 
siper kasıtlı olarak devre dışı bırakılmıştı.
```

**Çıktı (özet):**

```
OLAY TİPİ         : İş Kazası (6331 sk. Md. 3/1-g)
ACİLİYET          : Yüksek — Makine derhal durdurulmalı

KÖK NEDEN ANALİZİ (5 Neden)
  Neden 1 : Operatör siperi devre dışı bıraktı
  Neden 2 : Siper üretim hızını yavaşlatıyor
  Neden 3 : Bakım-tasarım uyumsuzluğu — ergonomi sorunu
  Neden 4 : Periyodik denetim yapılmamış
  Neden 5 : Denetim prosedürü tanımlı değil

DÖF 1 : Tüm makinelerde koruyucu kontrolü — Sorumlu: Bakım Şefi — Süre: 1 hafta
DÖF 2 : LOTO (Kilitleme-Etiketleme) eğitimi — Sorumlu: İSG Uzmanı — Süre: 2 hafta
DÖF 3 : Siper bypass alarmı kurulumu — Sorumlu: Üretim Md. — Süre: 3 hafta
```

---

## 📁 Proje Yapısı

```
isg-dijital-ofis/
├── agents.py          # Ajan tanımları — rol, hedef, backstory, LLM bağlantısı
├── tasks.py           # Görev zinciri — analiz → onay → rapor
├── crew_setup.py      # Crew ve süreç konfigürasyonu (sequential)
├── app.py             # Streamlit arayüzü
├── requirements.txt   # Python bağımlılıkları (sürüm sabitli)
├── packages.txt       # Sistem bağımlılıkları (Streamlit Cloud için)
├── .env.example       # API anahtarı şablonu
└── README.md
```

---

## 🔑 Desteklenen LLM Modeller

`LLM_MODEL_NAME` değişkeniyle model değiştirilebilir. Groq üzerinde önerilen modeller:

| Model | Hız | Kapasite |
|---|---|---|
| `llama-3.3-70b-versatile` | Yüksek | **Önerilen** |
| `llama-3.1-8b-instant` | Çok yüksek | Hızlı prototipleme |
| `mixtral-8x7b-32768` | Orta | Uzun bağlam |

> OpenAI veya Gemini kullanmak istersen `agents.py`'de `LLM(model="gpt-4o", ...)` veya `LLM(model="gemini/gemini-1.5-pro", ...)` olarak değiştir; `crewai.LLM` LiteLLM üzerinden her sağlayıcıyı destekler.

---

## 🗺️ Geliştirme Yol Haritası

- [ ] CrewAI `StepCallback` ile ajan adımlarını canlı sohbet baloncuklarında gösterme
- [ ] SQLite olay veritabanı — kalıcı kayıt ve geçmiş görüntüleme
- [ ] PDF rapor çıktısı (ReportLab ile)
- [ ] Risk değerlendirme matrisi oluşturan 4. ajan
- [ ] E-posta / webhook bildirim entegrasyonu
- [ ] Çok departmanlı genişletme (Üretim, İK, Satın Alma)

---

## 📄 Lisans

MIT — işletme ihtiyaçlarına göre uyarlayabilirsiniz.
