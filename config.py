from pathlib import Path


# ============================================================
# PROJECT BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# MYSQL DATABASE CONFIGURATION
# ============================================================

MYSQL_HOST = "localhost"
MYSQL_PORT = 3306

MYSQL_USER = "root"

# IMPORTANT:
# Replace YOUR_MYSQL_PASSWORD with your MySQL root password.
MYSQL_PASSWORD = "rifoo-1120"

MYSQL_DATABASE = "lost_found_db"


# ============================================================
# FILE UPLOAD CONFIGURATION
# ============================================================

# Folder where lost/found item images are stored.
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads" / "item_images"


# Allowed image file extensions.
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}


# Maximum uploaded request size:
# 5 MB
MAX_CONTENT_LENGTH = 5 * 1024 * 1024


# ============================================================
# FLASK SECURITY
# ============================================================

SECRET_KEY = "digital-lost-found-secret-key"


# ============================================================
# LANGUAGE CONFIGURATION
# ============================================================

DEFAULT_LANGUAGE = "en"

LANGUAGES = {
    "en": "English",
    "ta": "தமிழ்",
    "hi": "हिन्दी",
    "te": "తెలుగు",
    "ml": "മലയാളം",
    "kn": "ಕನ್ನಡ",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "ar": "العربية",
    "ja": "日本語",
    "zh": "中文",
    "ko": "한국어"
}


# Right-to-left languages.
RTL_LANGUAGES = {
    "ar"
}


# ============================================================
# SMART MATCHING CONFIGURATION
# ============================================================

# Minimum similarity percentage required
# for an item to be considered a match.
MATCH_THRESHOLD = 40


# Maximum number of matches displayed.
MAX_MATCHES = 10