import os
from datetime import datetime


AUTHOR = "Md. Mainul Islam"
OWNER = "CODEX-M41NUL"
GITHUB = "M41NUL"
GITHUB_URL = "https://github.com/M41NUL"

WHATSAPP = "+8801308850528"

TELEGRAM = "t.me/mdmainulislaminfo"
TELEGRAM_CHANNEL = "https://t.me/codexm41nul"
TELEGRAM_GROUP = "https://t.me/codex_m41nul"

EMAIL = "devmainulislam@gmail.com"

YOUTUBE = "https://youtube.com/@codexm41nul"

YEAR = datetime.now().year
COPYRIGHT = f"Copyright {YEAR} CODEX-M41NUL. All Rights Reserved."


API_KEY = os.environ.get("API_KEY", "m41nul")


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"


FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON", "")
FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL", "")


REQUEST_TIMEOUT_SECONDS = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", 60))
MAX_CAPTION_LENGTH = None
PREFERRED_QUALITY = "best"


FILENAME_BRAND_SUFFIX = os.environ.get("FILENAME_BRAND_SUFFIX", "All Media Downloader")
MAX_FILENAME_LENGTH = int(os.environ.get("MAX_FILENAME_LENGTH", 150))


YTDLP_AUTO_UPDATE = os.environ.get("YTDLP_AUTO_UPDATE", "true").lower() == "true"
YTDLP_UPDATE_CHECK_INTERVAL_SECONDS = int(
    os.environ.get("YTDLP_UPDATE_CHECK_INTERVAL_SECONDS", 6 * 60 * 60)
)


ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
