"""
Kararsızım — Django ayarları.

Tüm hassas değerler ortam değişkenlerinden okunur (yerelde .env dosyasından,
canlıda Vercel ortam değişkenlerinden). Ayrıntılar: doct/PROJE.md Bölüm 7.3
"""

import os
from pathlib import Path

import dj_database_url
import dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Yerel geliştirmede .env dosyasını yükle (canlıda ortam değişkenleri zaten tanımlı).
dotenv.load_dotenv(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-yalnizca-gelistirme-anahtari")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "1") == "1"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Vercel (https) gibi ters vekil kaynakları için CSRF güvenilir origin listesi
CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # runserver'da Django'nun statik bulma uygulamasını devre dışı bırak;
    # geliştirmede de WhiteNoise statikleri servis etsin.
    "whitenoise.runserver_nostatic",
    "polls",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "kararsizim.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "kararsizim.wsgi.application"


# Database
# Supabase PostgreSQL bağlantısı DATABASE_URL ortam değişkeninden gelir
# (dj-database-url ile çözümlenir). Tanımlı değilse yerel SQLite'a düşer.

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=0,  # serverless + connection pooler için her istekte yeni bağlantı
        # SSL, DATABASE_URL içindeki "?sslmode=require" ile gelir;
        # ssl_require=True burada kullanılamaz çünkü sqlite düşüşünde hata verir.
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Kimlik doğrulama yönlendirmeleri (Faz 1)
LOGIN_URL = "polls:login"
LOGIN_REDIRECT_URL = "polls:index"
LOGOUT_REDIRECT_URL = "polls:index"


# Internationalization

LANGUAGE_CODE = "tr"

TIME_ZONE = "Europe/Istanbul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# Kaynaklar static/ altında; collectstatic çıktısı staticfiles/ altında toplanır
# ve WhiteNoise servis eder.

STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Manifest yerine basit sıkıştırma: serverless build'de manifest eksikse
        # 500 alma riskine karşı prototipte güvenli seçenek.
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
