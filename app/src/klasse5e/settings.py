import os
import sys
from pathlib import Path

BASE_DIR = Path(os.environ.get("APP_ROOT", Path.cwd())).resolve()
APP_VERSION = "0.3.0-beta.4"
APP_RELEASE_CHANNEL = "beta"
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "unsafe-test-only-4f8d2a6c9e1b7d3f5a8c2e6b9d1f4a7c0e3b6d9f"
)
# Tests must never inherit production-only HTTPS redirects from a developer's
# shell. Production still requires DJANGO_DEBUG=0 explicitly.
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1" or "pytest" in sys.modules
ALLOWED_HOSTS = [
    item for item in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost").split(",") if item
]
CSRF_TRUSTED_ORIGINS = [
    item for item in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") if item
]

INSTALLED_APPS = [
    "klasse5e.core",
    "klasse5e.content",
    "klasse5e.events",
    "klasse5e.mobility",
    "klasse5e.media",
    "klasse5e.meals",
    "klasse5e.biometrics",
    "klasse5e.chat",
    "klasse5e.schedule",
    "klasse5e.webuntis",
    "klasse5e.itslearning",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.mfa",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "klasse5e.core.middleware.ActiveAccessMiddleware",
    "klasse5e.core.module_flags.ModuleGateMiddleware",
    "klasse5e.core.middleware.OnboardingRequiredMiddleware",
    "klasse5e.core.middleware.LoginRateLimitMiddleware",
    "klasse5e.core.middleware.PrivilegedMfaMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]
ROOT_URLCONF = "klasse5e.urls"
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
                "klasse5e.core.module_flags.module_context",
            ]
        },
    }
]
WSGI_APPLICATION = "klasse5e.wsgi.application"

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    from urllib.parse import urlparse

    parsed = urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed.path.lstrip("/"),
            "USER": parsed.username,
            "PASSWORD": parsed.password,
            "HOST": parsed.hostname,
            "PORT": parsed.port or 5432,
        }
    }
else:
    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test.sqlite3"}
    }

AUTH_USER_MODEL = "core.UserAccount"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_SIGNUP_ENABLED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_ADAPTER = "klasse5e.core.adapters.ClosedAccountAdapter"
ACCOUNT_SESSION_REMEMBER = False
MFA_SUPPORTED_TYPES = ["totp", "recovery_codes"]
MFA_PASSKEY_LOGIN_ENABLED = False
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

LANGUAGE_CODE = "de"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "runtime-media"))
MEDIA_URL = None
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "klasse-5e-security",
    }
}
WAGTAIL_SITE_NAME = "Klasse 5e"
WAGTAILADMIN_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:8080")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "KlassID <noreply@klassid.de>")
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
SECURE_REDIRECT_EXEMPT = [r"^health/$"]
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
X_FRAME_OPTIONS = "DENY"
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
GALLERY_MAX_UPLOAD_BYTES = 20 * 1024 * 1024
GALLERY_MAX_PIXELS = 40_000_000
GALLERY_MAX_BATCH = 25
GALLERY_MAX_TOTAL_BYTES = 5 * 1024 * 1024 * 1024
GALLERY_RETENTION_GRACE_DAYS = 30
MEAL_PLAN_SOURCE_URL = os.environ.get(
    "MEAL_PLAN_SOURCE_URL", "https://www.wollino.de/newpagefa4f13d4"
)
MEAL_PLAN_SYNC_ENABLED = os.environ.get("MEAL_PLAN_SYNC_ENABLED", "1") == "1"
BIOMETRIC_SEARCH_ENABLED = os.environ.get("BIOMETRIC_SEARCH_ENABLED", "0") == "1"
VISION_BASE_URL = os.environ.get("VISION_BASE_URL", "http://klasse-5e-vision:8000").rstrip("/")
VISION_SERVICE_TOKEN = os.environ.get("VISION_SERVICE_TOKEN", "")
BIOMETRIC_PIPELINE_ID = os.environ.get("BIOMETRIC_PIPELINE_ID", "yunet-sface-2023mar-2021dec")
BIOMETRIC_ORIGINAL_RETENTION_HOURS = 24
BIOMETRIC_MANUAL_REVIEW_MAX_DAYS = 7
BIOMETRIC_PROTOCOL_RETENTION_DAYS = 30
BIOMETRIC_SECURITY_AUDIT_RETENTION_DAYS = 90
CHAT_RETENTION_DAYS = int(os.environ.get("CHAT_RETENTION_DAYS", "90"))
WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY = os.environ.get("WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY", "")
WEBUNTIS_SERVER = os.environ.get("WEBUNTIS_SERVER", "thgwob.webuntis.com")
WEBUNTIS_SCHOOL = os.environ.get("WEBUNTIS_SCHOOL", "thgwob")
ITSLEARNING_CREDENTIAL_ENCRYPTION_KEY = os.environ.get(
    "ITSLEARNING_CREDENTIAL_ENCRYPTION_KEY", ""
)
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_SUBJECT = os.environ.get("VAPID_SUBJECT", "mailto:kontakt@klassid.de")
WEBDAV_ROOT = Path(os.environ.get("WEBDAV_ROOT", MEDIA_ROOT / "webdav"))
SPOONACULAR_API_KEY = os.environ.get("SPOONACULAR_API_KEY", "")
SPOONACULAR_API_BASE_URL = os.environ.get(
    "SPOONACULAR_API_BASE_URL", "https://api.apilayer.com/spoonacular"
)
SPOONACULAR_API_TIMEOUT_SECONDS = 5
SPOONACULAR_MAX_RESULTS = 12
MOBILITY_RETENTION_DAYS = 90
MOBILITY_DATA_ENCRYPTION_KEY = os.environ.get(
    "MOBILITY_DATA_ENCRYPTION_KEY",
    "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=" if DEBUG else "",
)
DATA_UPLOAD_MAX_MEMORY_SIZE = max(DATA_UPLOAD_MAX_MEMORY_SIZE, 100 * 1024 * 1024)
