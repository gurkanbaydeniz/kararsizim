# 🤔 Kararsızım — Proje Kılavuzu (Tek Kaynak Dosyası)

> **Bu dosya nedir?** "Kararsızım" web uygulamasının tüm detaylarını barındıran tek kaynak (single source of truth) dosyasıdır. ZCode (veya başka bir yapay zekâ asistanı) ile çalışırken bağlam olarak bu dosya verilir / okutulur. Dosya `doct/PROJE.md` yolunda tutulur ve kararlar değiştikçe güncellenir.

---

## 0. Bu Dosya ZCode ile Nasıl Kullanılır?

1. Bu dosya **`doct/PROJE.md`** yolunda durur. Proje kökündeki `AGENTS.md` dosyası ZCode'a bu dosyayı işaret eder — ZCode oturum başında onu otomatik okur, her seferinde "PROJE.md'yi oku" demek zorunda kalmazsın.
2. Geliştirme **fazlara bölünmüştür** (Bölüm 9 ve 10). Her ZCode oturumunda **tek fazın promptunu** yapıştır; hepsini birden isteme.
3. Faz bitince Bölüm 9'daki **kabul kriterlerini** kendin kontrol et; sonra `git commit` yap ve sonraki faza geç.
4. Bir şey bozulursa hatayı yapıştır ve şöyle de: *"doct/PROJE.md'ye uygun şekilde düzelt."*
5. Kod yazım kuralları: **tanımlayıcılar İngilizce** (`poll`, `choice`, `vote_count`), **yorumlar ve tüm arayüz metinleri Türkçe**.
6. ZCode'da tarayıcı aracı varsa, faz sonlarında sayfaların ekran görüntüsünü alıp görsel kontrol yapmasını isteyebilirsin.

---

## 1. Proje Künyesi

| Alan | Değer |
|---|---|
| Proje adı | **Kararsızım** |
| Tür | Sosyal anket / oylama platformu (web) |
| Slogan | "Kararsızım, sen karar ver!" |
| Hedef kitle | Gençler (16-30) |
| Arayüz dili | Türkçe |
| Aşama | **Prototip** (basit tutulacak, aşırı mühendislik YOK) |
| Domain adı | `kararsizim.vercel.app` (Vercel projesi oluşturulurken proje adı "kararsizim" yapılacak; prototipte subdomain yeterli) |

**Tek cümlelik tanım:** Kararsızım; kullanıcıların karar veremedikleri anlarda ("sinemaya mı gitsem, restorana mı?") topluluğa 2-5 seçenekli anket açıp, herkesin (üye olsun ya da olmasın) oy verdiği basit ve eğlenceli bir anket platformudur.

---

## 2. Kapsam

### 2.1 Prototipte YAPILACAKLAR
- Anket görüntüleme (hepsi herkese açık, akış halinde liste)
- Anket oluşturma (yalnızca üyeler; soru + 2-5 seçenek)
- Oy kullanma (**misafirler dahin** herkes oylayabilir)
- Sonuçları yüzdesel bar grafiklerle görme
- Üyelik: kullanıcı adı + e-posta + parola ile kayıt, giriş, çıkış
- Kullanıcı adının anketlerde görünmesi (e-posta asla görünmez)
- "Anketlerim" sayfası
- Django admin (geliştirici/moderasyon için)
- Vercel'e canlı deploy

### 2.2 Prototipte YAPILMAYACAKLAR (kasıtlı olarak — istenirse bile ekleme!)
- ❌ Takip / arkadaş mekanizması (herkes her anketi görür ve oylar)
- ❌ Yorumlar
- ❌ Bildirimler, e-posta doğrulama, şifre sıfırlama (unutulursa admin'den manuel sıfırlanır)
- ❌ Kategori/etiket, arama, popülerlik sıralaması
- ❌ Seçeneklere görsel ekleme
- ❌ Oy değiştirme, anket düzenleme, anket kapatma süresi
- ❌ REST API, Docker, test süiti, CI/CD
- ❌ Frontend framework (React/Vue/Tailwind vb. YOK — vanilla HTML/CSS/JS)
- ❌ Karanlık mod

> Bu listedekiler **v2 fikirleri** olarak Bölüm 12'de durur. ZCode bunları teklif ederse: "Prototip kapsamı dışı, doct/PROJE.md 2.2'ye bak" denir.

---

## 3. Roller ve Yetkiler

| Eylem | Misafir (üye olmayan) | Üye |
|---|---|---|
| Anketleri listeleme ve görüntüleme | ✅ | ✅ |
| Oy kullanma | ✅ | ✅ |
| Anket oluşturma | ❌ → giriş sayfasına yönlenir (`?next=...`) | ✅ |
| Kendi anketini görüntüleme ("Anketlerim") | ❌ | ✅ |
| Kendi anketini silme | ❌ | ✅ (Faz 4, opsiyonel) |
| Kayıt / giriş / çıkış | ✅ | ✅ |
| Django admin (`/admin/`) | ❌ | Yalnızca staff (geliştirici) |

**Kimlik kuralları:**
- Kamuya açık tek kimlik **kullanıcı adıdır**; e-posta hiçbir şablonda, listede, API yanıtında gösterilmez/sızdırılmaz.
- Misafirler siteye "anonim" girer; isim/kimlik gerekmez.

---

## 4. Veri Modeli

Django ORM ile PostgreSQL (Supabase) üzerinde. Tek uygulama: `polls`. Kullanıcı modeli: Django'nun yerleşik `User`'ı (ekstra profil tablosu YOK; kullanıcı adı ve e-posta `User` üzerinde zaten var).

```python
# polls/models.py
from django.conf import settings
from django.db import models

class Poll(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="polls")
    question = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=80)
    position = models.PositiveSmallIntegerField(default=0)  # seçenek sırası

    class Meta:
        ordering = ["position", "id"]

class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="votes")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             null=True, blank=True)  # kullanıcı silinse de oy sayısı korunur
    voter_key = models.CharField(max_length=64)  # bkz. aşağıdaki açıklama
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["poll", "voter_key"], name="unique_vote_per_poll"),
        ]
```

### `voter_key` mantığı (çift oy önleme, tek mekanizma)
Hem üyelerin hem misafirlerin "anket başına bir oy" kuralı **tek unique constraint** ile zorlanır:

```python
# polls/utils.py
import uuid

def get_voter_key(request):
    """Üyeler için 'user:<id>', misafirler için session'da saklanan 'guest:<uuid>'."""
    if request.user.is_authenticated:
        return f"user:{request.user.id}"
    if not request.session.get("guest_key"):
        request.session["guest_key"] = uuid.uuid4().hex
    return f"guest:{request.session['guest_key']}"
```

- Misafir ilk oyladığında Django session'una (`guest_key`) UUID yazılır → tarayıcı çereziyle aynı misafir tanınır.
- "Bu ankete zaten oy vermiş mi?" kontrolü view'da `Vote.objects.filter(poll=..., voter_key=...)` ile yapılır; yarış durumuna karşı unique constraint de vardır (`IntegrityError` yakalanıp uygun mesaj verilir).

### Sorgu notları
- Feed sorgusunda N+1'den kaçın: `Poll.objects.select_related("creator").annotate(total_votes=Count("votes", distinct=True))`.
- Detay sayfasında her seçenek için oy sayısı: `Choice.objects.filter(poll=...).annotate(vote_count=Count("votes"))`.
- Yüzde: `choice.vote_count / poll.toplam_oy * 100` (tam sayıya yuvarla, 0 oy varsa "Henüz oy yok" durumu).

---

## 5. Sayfalar ve URL Şeması

| URL | View | Şablon | Giriş gerekli mi |
|---|---|---|---|
| `/` | `poll_list` (feed) | `polls/poll_list.html` | Hayır |
| `/anket/olustur/` | `poll_create` | `polls/poll_form.html` | **Evet** |
| `/anket/<int:pk>/` | `poll_detail` | `polls/poll_detail.html` | Hayır |
| `/anket/<int:pk>/oy/` | `vote` (yalnızca POST) | — (detail'e yönlendirir) | Hayır |
| `/anketlerim/` | `my_polls` | `polls/my_polls.html` | Evet |
| `/kayit/` | `register` | `registration/register.html` | Hayır |
| `/giris/` | `login` (kullanıcı adı **veya** e-posta ile) | `registration/login.html` | Hayır |
| `/cikis/` | Django `LogoutView` (yalnızca POST) | — | Hayır |
| `/admin/` | Django admin | — | Staff |

> URL sırası önemli: `/anket/olustur/`, `/anket/<int:pk>/`'den **önce** tanımlanır.

### Sayfa davranışları
- **Feed (`/`):** Anket kartları en yeniden eskiye, sayfa başına 12 (`Paginator`). Kartta: soru, `@kullanıcıadı · 5 dk önce · 12 oy`. `timesince` filtresi kullanılır.
- **Detay:** Seçenekler oylanabilir buton/pill olarak listelenir.
  - Henüz oy vermediyse → oylama butonları + altında küçük "Sonuçları gör (oy vermeden)" linki.
  - Oy verdiyse **veya** "Sonuçları gör"e tıkladıysa → sonuç ekranı (bar grafikleri, yüzdeler, toplam oy, kendi oyunuz ✔ işaretli). "Oylamaya dön" linkiyle geri dönebilir (oy vermediyse).
- **Oylama (`POST /anket/<pk>/oy/`):** `choice_id` alınır; seçeneğin gerçekten bu ankete ait olduğu, kullanıcının daha önce oy vermediği kontrol edilir; oy kaydedilir; mesaj ("Oyun kaydedildi 🎉") ile detail'e yönlendirilir.
- **Oluşturma:** Dinamik seçenek alanları (JS ile ekle/çıkar, 2-5 arası), sunucu tarafı doğrulama, başarıdan sonra yeni anketin detay sayfasına yönlendirme.
- **Header (tüm sayfalarda):** Sol: logo `🤔 Kararsızım`. Sağ: üyeyse `@kullanıcıadı`, `Anketlerim`, `Çıkış`; misafirse `Giriş`, `Kayıt`. `Anket Oluştur` herkese görünür (CTA) ama misafir tıklayınca girişe yönlenir.

---

## 6. İş Kuralları ve Doğrulama

1. **Soru:** zorunlu, 10–200 karakter.
2. **Seçenekler:** en az **2**, en fazla **5**; her biri 1–80 karakter; boş seçenek satırları reddedilir; baş/son boşluklar atılıp (trim, küçük harf duarsız) **birebir aynı** seçenekler reddedilir. Doğrulama hem tarayıcıda (JS) hem sunucuda yapılır.
3. **Bir ankete bir oy:** üye de misafir de ankete yalnızca 1 kez oy verir; oy değiştirilemez. Tekrar denemede "Bu ankete zaten oy verdin" mesajı + sonuç ekranı gösterilir.
4. **Anket sahibi kendi anketine oy verebilir.** (Eğlenceli, serbest.)
5. Anket yayımlandıktan sonra **düzenlenemez**; sahibi silebilir (Faz 4, opsiyonel; silme oylarla birlikte cascade olur).
6. **Kayıt:** kullanıcı adı + e-posta + parola. E-posta sistemde **tektir (unique)**. Doğrulama postası YOK. Parolada Django'nun yerleşik doğrulayıcıları.
7. **Kullanıcı adı:** Django kuralları (harf/rakaz/`./+/-/_`, maks. 150, tek). Kayıt sırasında "bu kullanıcı adı alınmış" kontrolü.
8. **Giriş:** kullanıcı adı **veya** e-posta + parola.
9. Tüm hata/bilgi mesajları **Türkçe**, Django `messages` framework'ü ile; mesajlar sayfa üstünde toast olarak yüzer, JS ile ~3 sn sonra kaybolur.
10. Feed'de her anket herkese görünür — gizlilik/filtre YOK (tasarım gereği).
11. Kullanıcı girişi `?next=` ile korunur: misafir "Anket Oluştur"a basarsa → `/giris/?next=/anket/olustur/` → giriş sonrası direkt oluşturma sayfası.

---

## 7. Teknoloji ve Mimari

### 7.1 Stack
| Katman | Seçim | Not |
|---|---|---|
| Backend | **Python + Django 5** | Sunucu tarafı render (template'ler), API YOK |
| Veritabanı | **Supabase (PostgreSQL)** | Yalnızca DB olarak; Supabase Auth/Storage kullanılmıyor |
| Frontend | **Vanilla HTML + CSS + JS** | Aynı repo, framework yok; JS sadece ince katman |
| Statik dosyalar | **WhiteNoise** | Vercel serverless ortamında statikleri Django servis eder |
| Deploy | **Vercel** | GitHub reposundan, `@vercel/python` runtime |
| Bağlantı çözümleme | `dj-database-url` + `psycopg2-binary` | |

### 7.2 Ortam değişkenleri
| Değişken | Açıklama |
|---|---|
| `SECRET_KEY` | Gizli anahtar; yerelde `.env`, prod'da Vercel env |
| `DEBUG` | Yerelde `1`, canlıda `0` |
| `DATABASE_URL` | Supabase PostgreSQL URI'si (`postgres://...`), gizli tutulur |
| `ALLOWED_HOSTS` | Örn. `localhost,127.0.0.1,.vercel.app` (virgülle ayrılmış) |
| `CSRF_TRUSTED_ORIGINS` | Canlıda `https://*.vercel.app` |

Yerelde `.env` dosyasından okuma için basit bir `os.environ` + `python-dotenv` kullanımı yeterli (aşırı ayar YOK). `.env` **asla** git'e girmez; `.env.example` şablon olarak commit edilir.

### 7.3 `settings.py` özeti (Faz 0'da tam yazılacak)
```python
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY", "yalnizca-gelistirme-anahtari")
DEBUG = os.environ.get("DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",   # DATABASE_URL yoksa yerel düşüş
        conn_max_age=0,                    # serverless + pooler için uygun
        # SSL, DATABASE_URL içindeki "?sslmode=require" ile gelir;
        # ssl_require=True kullanılmaz çünkü sqlite düşüşünde hata verir.
    )
}

INSTALLED_APPS = [..., "whitenoise.runserver_nostatic", "polls"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # SecurityMiddleware'in hemen altında
    ...
]
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]
LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_TZ = True
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
```

### 7.4 Repo/dizin yapısı (hedef)
```
kararsizim/
├── manage.py
├── requirements.txt
├── vercel.json
├── .env                 # yerelde; git'e girmez
├── .env.example
├── .gitignore
├── README.md            # kurulum + çalıştırma adımları
├── AGENTS.md            # ZCode'a doct/PROJE.md'yi işaret eder
├── doct/
│   └── PROJE.md         # BU DOSYA
├── kararsizim/          # Django proje paketi
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py          # sonuna: app = application  (Vercel için)
├── polls/               # TEK Django uygulaması (her şey burada)
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── utils.py
├── templates/
│   ├── base.html
│   ├── polls/
│   │   ├── poll_list.html
│   │   ├── poll_detail.html
│   │   ├── poll_form.html
│   │   └── my_polls.html
│   └── registration/
│       ├── login.html
│       └── register.html
└── static/
    ├── css/style.css
    └── js/main.js
```

### 7.5 Supabase notları
1. supabase.com → New project (bölge olarak **Frankfurt / EU Central** yakın olur) → veritabanı parolası belirle.
2. Project Settings → Database → **Connection string (URI)** kopyala.
3. Vercel (serverless) için **Connection Pooler** URI'sini kullan (port 6543 olan); sonuna `?sslmode=require` ekle. `conn_max_age=0` bırakılır (yukarıdaki ayar bunu yapar).
4. **Migration'lar hep yerel makineden çalıştırılır** (DB uzak olduğundan doğrudan canlıyı etkiler): `python manage.py migrate`. Vercel üzerinde migration çalıştırılmaz.
5. Supabase paneli sadece DB yönetimi için kullanılır; Auth/Storage/RLS özelliklerine dokunulmaz.

### 7.6 Vercel notları
- `requirements.txt`:
  ```
  Django>=5.0,<5.3
  dj-database-url
  psycopg2-binary
  whitenoise
  python-dotenv
  ```
- `vercel.json` (taslak, Faz 0'da oluşur):
  ```json
  {
    "builds": [{ "src": "kararsizim/wsgi.py", "use": "@vercel/python" }],
    "routes": [{ "src": "/(.*)", "dest": "kararsizim/wsgi.py" }],
    "buildCommand": "python -m pip install -r requirements.txt && python manage.py collectstatic --noinput"
  }
  ```
  (`buildCommand` çalışmazsa aynı komut Vercel dashboard'dan Build Command olarak girilir.)
- `kararsizim/wsgi.py` sonuna `app = application` eklenir.
- Vercel projeye env değişkenleri girilir: `SECRET_KEY`, `DEBUG=0`, `DATABASE_URL` (pooler URI), `ALLOWED_HOSTS=localhost,127.0.0.1,.vercel.app`, `CSRF_TRUSTED_ORIGINS=https://*.vercel.app`.
- Deploy akışı: GitHub'a push → Vercel Import (Framework: Other) → Deploy. İlk deploy'dan **önce** migration'lar yerelden çalıştırılmış olmalı.

### 7.7 Yerel geliştirme (Windows)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # .env'i doldur (DATABASE_URL dahil)
python manage.py migrate
python manage.py runserver
```

### 7.8 JS'in görevi (ince katman, hepsi `static/js/main.js` içinde)
- Oluşturma formunda seçenek satırı ekle/çıkar (2-5 sınırı, buton disable/enable)
- Toast mesajlarının ~3 sn sonra kaybolması
- Detay sayfasında "Anketi paylaş" butonu: anket URL'sini panoya kopyalar
- Başka hiçbir şey. Oylama ve formlar normal Django POST'u ile çalışır (JS'siz de çalışmalı).

---

## 8. Tasarım Sistemi

**Ruh:** Açık/zemin açık tonlu, üzerine canlı (vivid) renkler, temiz ve genç. Kart tabanlı, yuvarlak köşeli, oynak ama düzenli. "Pastel değil — canlı". Ölçülü emoji kullanımı serbest.

### 8.1 Renk token'ları (`static/css/style.css` başında `:root` değişkenleri)
```css
:root {
  --bg:        #FAFAFF;   /* açık zemin (hafif lila-beyaz) */
  --surface:   #FFFFFF;   /* kart yüzeyi */
  --ink:       #232135;   /* ana metin */
  --ink-soft:  #7A7B99;   /* ikincil metin */
  --primary:   #6C5CE7;   /* canlı mor — ana marka rengi */
  --primary-2: #A29BFE;   /* açık mor — hover/gradient eşi */
  --accent:    #FF6B6B;   /* mercan — vurgu/hata eşliği */
  --teal:      #00C9A7;   /* nane yeşili — başarı */
  --blue:      #4D96FF;
  --sun:       #FFC93C;   /* sarı */
  --danger:    #E63946;
  --border:    #E9E8F8;
  --ring:      rgba(108, 92, 231, .25);

  --shadow-sm: 0 2px 8px rgba(35, 33, 53, .06);
  --shadow-md: 0 8px 24px rgba(108, 92, 231, .12);
  --r-md: 16px; --r-lg: 24px; --r-pill: 999px;

  /* Oy butonu / sonuç barı renk döngüsü (seçenek sırasına göre) */
  --opt-1: var(--primary); --opt-2: var(--accent); --opt-3: var(--teal);
  --opt-4: var(--blue);    --opt-5: var(--sun);
}
```

### 8.2 Tipografi ve yerleşim
- Font: **Nunito** (Google Fonts; 400/600/700/800). Başlıklar 800, gövde 400/600.
- Taban boyut 16px; soru başlığı `clamp(1.25rem, 4vw, 1.6rem)`.
- Mobil öncelikli; feed konteyneri `max-width: 640px` ortalanmış; formlar `max-width: 480px`.
- Dokunma hedefleri min. 44px.

### 8.3 Bileşenler
- **Header:** sticky, yarı saydam beyaz + hafif blur; sol logo `🤔 Kararsızım` (ağır font, primary renk vurgusu); sağ nav linkleri.
- **Anket kartı (feed):** beyaz yüzey, `--r-lg` köşe, `--shadow-sm`; içinde soru (700-800), meta satırı `@kullanıcıadı · 5 dk önce · 12 oy` (`--ink-soft`); hover'da `translateY(-2px)` + `--shadow-md`. Tıklayınca detaya.
- **Oy butonu (detay):** tam genişlik pill (`--r-pill`), renk döngüsü `--opt-1..5`, solda renkli nokta; hover'da hafif `scale(1.01)`; aktif basılı efekti.
- **Sonuç barı:** üstte satır "seçenek metni — %62" (+ kendi oyunuzsa ✔), altında 10px yüksekliğinde yuvarlak bar; genişlik yüzdeye göre `transition: width .4s ease` ile animasyonlu dolar. En çok oylu seçenek dolgun renk + 👑.
- **Butonlar:** primary (dolu `--primary`, beyaz metin), ghost (şeffaf, mor kenarlık), danger (`--accent`/`--danger`).
- **Formlar:** etiketli input'lar, `border: 1px solid var(--border)`, `--r-md` köşe; odakta `box-shadow: 0 0 0 4px var(--ring)`; hata mesajları küçük, `--danger`.
- **Toast (messages):** sayfa üstünde yüzen pill; başarı `--teal` tonu, hata `--accent` tonu.
- **Boş durumlar:** emoji + tek cümle + CTA. Örn: "Şu an anket yok — ilk anketi sen aç! 🎉"
- **404:** "Bu karara varılamadı 🤷" + ana sayfa linki.

---

## 9. Yol Haritası — Fazlar ve Kabul Kriterleri

> Fazlar sırayla yapılır. Her faz kendi içinde çalışır durumda olmalı; sonraki faz öncekini bozmamalı.
> **Karar (29.09.2026):** Fazlar tek tek, her faz sonunda kullanıcı onayıyla ilerler.

### FAZ 0 — Temel Kurulum ve İskelet
**Amaç:** Proje ayağa kalksın, Supabase bağlantısı çalışsın, tasarım iskeleti görünsün.
**İşler:** git init + .gitignore; venv + requirements.txt; `startproject kararsizim .` (kökte manage.py) + `startapp polls`; 7.3'teki settings; `base.html` (header/nav iskeleti) + `style.css` (token'lar + temel bileşenler) + boş `main.js`; boş anasayfa view'ı; `.env.example`, `README.md`, `vercel.json` taslağı; Supabase'e ilk `migrate`.
**Kabul kriterleri:**
- [ ] `python manage.py runserver` → `http://127.0.0.1:8000/` açılıyor, style.css yükleniyor (konsolda 404 yok)
- [ ] `migrate` Supabase'e hatasız uygulanıyor (Supabase → Table Editor'da `auth_user` tablosu görünüyor)
- [ ] Header'da logo ve nav iskeleti görünüyor; DEBUG hataları Türkçe

### FAZ 1 — Üyelik (Kayıt / Giriş / Çıkış)
**Amaç:** Kullanıcı hesabı açıp girebilsin; header durum göre değişsin.
**İşler:** Kayıt formu (kullanıcı adı, e-posta(unique), parola x2; Türkçe hatalar) + kayıt sonrası otomatik giriş; giriş sayfası (kullanıcı adı **veya** e-posta + parola); çıkış (POST, Django LogoutView); header'da üye/misafir durumları; `@login_required` ile korunmuş boş `/anket/olustur/` placeholder'ı (`?next=` çalışsın).
**Kabul kriterleri:**
- [ ] Kayıt → otomatik giriş → header'da `@kullanıcıadı` görünüyor
- [ ] Aynı e-posta / aynı kullanıcı adıyla ikinci kayıt Türkçe hata veriyor
- [ ] Yanlış parola giriş ekranında Türkçe hata veriyor; çıkış sonrası header misafir haline dönüyor
- [ ] Misafir `/anket/olustur/` adresine girerse `/giris/?next=/anket/olustur/`'a gidiyor; giriş sonrası oluşturma sayfası açılıyor

### FAZ 2 — Anket Oluşturma, Listeleme, Detay
**Amaç:** Üye anket açabilsin; herkes listeleyip detay görebilsin.
**İşler:** Bölüm 4'teki modeller + migration'lar + admin kayıtları; oluşturma formu (soru + JS ile dinamik 2-5 seçenek; sunucu doğrulaması Bölüm 6); feed (Paginator 12, `select_related` + `annotate`); detay sayfası (oy butonları henüz pasif — Faz 3'te bağlanacak; toplam oy, seçenekler, sahibin adı); "Anketlerim" sayfası.
**Kabul kriterleri:**
- [ ] Üye 3 seçenekli anket oluşturuyor → yeni anketin detay sayfasına yönleniyor
- [ ] 1 seçenekle veya 6 seçenekle gönderim Türkçe hata veriyor; boş/birebir aynı seçenek reddediliyor
- [ ] Feed en yeni en üstte; kartta soru + `@kullanıcıadı` + süre + toplam oy; 2. sayfa (`?page=2`) çalışıyor
- [ ] "Anketlerim" yalnızca kullanıcının kendi anketlerini listeliyor

### FAZ 3 — Oylama ve Sonuçlar
**Amaç:** Misafir dahil herkes oy verebilsin; sonuçlar yüzdesel barlarla görünsün.
**İşler:** `POST /anket/<pk>/oy/` view'ı (Bölüm 5 + 6 kuralları: seçenek-anket eşleşmesi, `voter_key`, `IntegrityError` güvenliği); detayda oy-verildi/seçenekleri göster durumları; sonuç ekranı (animasyonlu barlar, yüzdeler, toplam oy, kendi oy ✔, kazanan 👑); "Sonuçları gör (oy vermeden)" / "Oylamaya dön" geçişleri.
**Kabul kriterleri:**
- [ ] Misafir oy verebiliyor; aynı ankete ikinci oy denemesi "Bu ankete zaten oy verdin" gösteriyor ve sonuçlar görünüyor
- [ ] Üye için de aynı; üye çıkış yapıp girse bile oyu hatırlanıyor (tekrar oy veremiyor)
- [ ] Yüzdelerin toplamı ~100; her seçeneğin oyu ve toplam oy doğru sayılıyor
- [ ] Başka bir tarayıcı sekmesinden (yeni misafir) aynı ankete oy verilebiliyor (misafir başına 1 oy kuralı)

### FAZ 4 — Cila ve Vercel Deploy
**Amaç:** Prototip canlıya çıksın.
**İşler:** Boş durumlar + 404 sayfası; favicon ve logo (emoji tabanlı basit SVG); mikro animasyon tutarlılığı; mobil responsive turu; "Anketi paylaş" (panoya kopyala) butonu; opsiyonel: kendi anketini silme (onaylı); güvenlik kontrol listesi (aşağıda); Vercel deploy (7.6) + env değişkenleri + yerelden migration + canlı smoke test.
**Güvenlik kontrol listesi:** `DEBUG=0` canlıda; `SECRET_KEY` env'den; `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` ayarlı; e-posta hiçbir şablonda görünmüyor; Django admin yalnızca staff; CSRF açık (varsayılan); kullanıcı girdisi `|safe` ile render edilmiyor.
**Kabul kriterleri:**
- [ ] Canlı URL'de uçtan uca akış çalışıyor: kayıt → anket oluştur → başka tarayıcıdan (misafir) oy → sonuçlar
- [ ] Statik dosyalar canlıda yükleniyor (CSS uygulanıyor)
- [ ] Mobil ekranda (375px genişlik) düzen bozulmuyor
- [ ] Olmayan anket URL'i Türkçe 404 veriyor

---

## 10. Faz Promptları (ZCode'a sırayla yapıştır)

> Her oturumda bir tanesi. ZCode dosyayı okumamışsa başına "Önce doct/PROJE.md dosyasını oku." ekle.

### Prompt — FAZ 0
```
doct/PROJE.md dosyasını oku; "Kararsızım" projesine başlıyoruz.
Şimdi SADECE Faz 0'ı (Bölüm 9) uygula; model, form, üyelik gibi şeylere girme.

Yapılacaklar:
1) git init + .gitignore (.venv/, .env, __pycache__/, staticfiles/, *.pyc)
2) Sanal ortam + requirements.txt (Bölüm 7.6'daki paketler)
3) Django projesi: "django-admin startproject kararsizim ." (manage.py kökte)
   ve "python manage.py startapp polls"
4) settings.py'i doct/PROJE.md Bölüm 7.3'teki gibi env-tabanlı yapılandır
   (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL/dj-database-url, WhiteNoise,
   STATIC/TEMPLATES dizinleri, LANGUAGE_CODE=tr, TIME_ZONE=Europe/Istanbul)
5) templates/base.html (header/nav iskeleti: logo + Giriş/Kayıt placeholder'ları),
   static/css/style.css (Bölüm 8.1'deki tasarım token'ları + kart/buton/form/toast
   temel stilleri), boş static/js/main.js
6) polls/views.py'de basit anasayfa view'ı + polls/urls.py + kararsizim/urls.py include
7) .env.example, README.md (Bölüm 7.7'deki kurulum adımlarıyla), vercel.json (Bölüm 7.6)
8) Supabase bağlantı URI'sini benden isteyerek .env'e yaz; sonra
   "python manage.py migrate" ile Supabase'e ilk migration'ları uygula

Bitince: runserver ile anasayfanın açıldığını doğrula, yapılanları ve Faz 0 kabul
kriterlerini özetle. Migration'lar dahil her şey tamam ise commit önerisi ver.
```

### Prompt — FAZ 1
```
doct/PROJE.md'yi oku ve SADECE Faz 1'i (Üyelik) uygula; anket işlevlerine girme.

Yapılacaklar:
1) Kayıt sayfası (/kayit/): kullanıcı adı + e-posta (unique) + parola x2.
   Özel UserCreationForm; tüm hatalar Türkçe. Kayit sonrası otomatik giriş.
2) Giriş sayfası (/giris/): kullanıcı adı VEYA e-posta + parola (Bölüm 6, kural 8).
3) Çıkış (/cikis/): yalnızca POST ile, Django LogoutView; sonrası anasayfa.
4) base.html header'ını durumlu yap: üyeyse @kullanıcıadı + Anketlerim + Çıkış;
   misafirse Giriş + Kayıt. "Anket Oluştur" CTA'sı herkese görünür.
5) /anket/olustur/ için @login_required placeholder view; ?next= yönlendirmesi
   çalışsın (giriş sonrası geri dönsün).
6) Mesajlar Django messages + toast bileşeniyle (JS ile ~3 sn sonra kaybolur).

Bitince: Faz 1 kabul kriterlerini (doct/PROJE.md Bölüm 9) tek tek kendin test et,
sonucu ve yaptıklarını özetle, commit öner.
```

### Prompt — FAZ 2
```
doct/PROJE.md'yi oku ve SADECE Faz 2'yi (Anket Oluşturma, Listeleme, Detay) uygula.

Yapılacaklar:
1) Modeller (doct/PROJE.md Bölüm 4'teki Poll, Choice, Vote birebir) + migration'lar
   (yerelden Supabase'e uygula) + admin.py kayıtları.
   NOT: Vote modelini oluştur ama oylama mantığı Faz 3'te; şimdi sadece tablo.
2) /anket/olustur/ : soru (10-200 krk) + dinamik seçenek alanları (JS: ekle/çıkar,
   2-5 arası). Sunucu tarafı doğrulama Bölüm 6 kural 2 (trim, aynı seçenek reddi).
   Başarıda yeni anketin detayına yönlendir.
3) / : feed — en yeni önce, sayfa başına 12 (Paginator), select_related("creator")
   + annotate(total_votes=...). Kart tasarımı Bölüm 8.3.
4) /anket/<int:pk>/ : detay — soru, @kullanıcıadı, süre (timesince), toplam oy,
   seçenekler pill olarak (tıklama Faz 3'te aktifleşecek, şimdi pasif görünsün).
5) /anketlerim/ : yalnızca kendi anketleri.

Bitince: Faz 2 kabul kriterlerini tek tek test et, özetle, commit öner.
```

### Prompt — FAZ 3
```
doct/PROJE.md'yi oku ve SADECE Faz 3'ü (Oylama ve Sonuçlar) uygula.

Yapılacaklar:
1) polls/utils.py -> get_voter_key (doct/PROJE.md Bölüm 4'teki gibi).
2) POST /anket/<int:pk>/oy/ : choice_id doğrula (seçenek bu ankete ait mi?),
   voter_key ile çift oy kontrolü, IntegrityError güvenliği; oy kaydet,
   "Oyun kaydedildi 🎉" mesajıyla detaya yönlendir.
3) Detay sayfası durumları:
   - Oy vermediyse: oy butonları (renk döngüsü --opt-1..5) + "Sonuçları gör
     (oy vermeden)" linki
   - Oy verdiyse veya sonucları açtıysa: animasyonlu sonuç barları, yüzdeler,
     toplam oy, kendi seçeneğinde ✔, en çok oyluda 👑; oy vermediyse
     "Oylamaya dön" linki
4) Oy butonları form POST ile çalışsın (JS'siz de çalışmalı).

Bitince: Faz 3 kabul kriterlerini (misafir + üye + iki tarayıcı senaryosu dahil)
tek tek test et, özetle, commit öner.
```

### Prompt — FAZ 4
```
doct/PROJE.md'yi oku ve SADECE Faz 4'ü (Cila ve Vercel Deploy) uygula.

Yapılacaklar:
1) Boş durumlar (feed boşken, Anketlerim boşken), Türkçe 404 sayfası,
   favicon + logo (emoji tabanlı minik SVG).
2) Mobil responsive turu (375px), animasyon tutarlılığı, "Anketi paylaş"
   (panoya kopyala) butonu detay sayfasında.
3) Opsiyonel (sor önce bana): kendi anketini onaylı silme.
4) doct/PROJE.md Faz 4 güvenlik kontrol listesini uygula (DEBUG=0 prod,
   CSRF_TRUSTED_ORIGINS vb.).
5) Vercel deploy: Bölüm 7.6'yi uygula (vercel.json, wsgi.py app değişkeni,
   collectstatic). Migration'ların yerelden Supabase'e uygulandığından emin ol.
   Deploy adımlarında bana GitHub push / Vercel ayarları için ne yapmam
   gerektiğini sırayla anlat; env değişkenlerini girmemi hatırlat.
6) Deploy sonrası canlı smoke test listesi: kayıt → giriş → anket oluştur →
   misafir oy → sonuçlar → statik CSS → 404.

Bitince: kabul kriterlerini canlı ortamda doğrula (tarayıcı aracın varsa ekran
görüntüleriyle) ve özetle.
```

---

## 11. Terminoloji (kod ve konuşmada ortak dil)

| Terim | Kod karşılığı |
|---|---|
| Anket | `Poll` |
| Seçenek | `Choice` |
| Oy | `Vote` |
| Misafir | guest (kimliği doğrulanmamış ziyaretçi) |
| Üye | authenticated user |
| Akış/Feed | `poll_list` |

---

## 12. v2 Fikirleri (prototip kapsamı DIŞINDA — şimdi yok)

Yorumlar · Kategori/etiketler · Popüler/trend sıralama · Arama · Anket kapatma süresi · Seçeneklere görsel · Oy değiştirme · E-posta doğrulama ve şifre sıfırlama · Hız limitleme (rate limit) · Paylaşım için OG görseli · Karanlık mod · Anket sonucu grafiği/kazanan rozeti geliştirme · Kullanıcı profili sayfası (kişinin tüm anketleri).

---

*Bu doküman projenin tek doğruluk kaynağıdır; yapılan kararlar buraya işlenir, ZCode oturumlarında bağlam olarak verilir.*
