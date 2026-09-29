# 🤔 Kararsızım

> "Kararsızım, sen karar ver!" — Karar veremediğin anlarda topluluğa 2-5 seçenekli anket açıp herkesin (üye olsun ya da olmasın) oy verebildiği anket platformu.

Tüm proje detayları, kurallar ve faz planı: **[doct/PROJE.md](doct/PROJE.md)**

## Teknoloji

| Katman | Seçim |
|---|---|
| Backend | Python + Django 5 (sunucu tarafı render) |
| Veritabanı | Supabase (PostgreSQL) — yalnızca DB olarak |
| Frontend | Vanilla HTML + CSS + JS (framework yok) |
| Statik | WhiteNoise |
| Deploy | Vercel |

## Yerel Geliştirme (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # .env'i doldur (DATABASE_URL dahil)
python manage.py migrate
python manage.py runserver
```

Ardından <http://127.0.0.1:8000/> adresini aç.

> `DATABASE_URL` tanımlı değilse proje yerelde otomatik olarak `db.sqlite3` kullanır.

## Süper kullanıcı (Django admin)

```
python manage.py createsuperuser
```

Ardından `/admin/` adresinden giriş yap.

## Ortam Değişkenleri

`.env.example` dosyasına bakın. `.env` **asla** git'e commit edilmez.

## Klasör Yapısı

```
kararsizim/      → Django proje paketi (settings, urls, wsgi)
polls/           → tek Django uygulaması (modeller, view'lar, formlar)
templates/       → HTML şablonları
static/          → css / js
doct/            → proje dokümantasyonu (PROJE.md)
```
