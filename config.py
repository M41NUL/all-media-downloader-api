# ============================================
# CONFIG FILE
# Application configuration and developer information
# ============================================

import os
from datetime import datetime

# ------------------------------------------------
# DEVELOPER INFORMATION
# ------------------------------------------------

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

# ------------------------------------------------
# API KEY SETTINGS
# ------------------------------------------------

API_KEY = os.environ.get("API_KEY", "m41nul")

# ------------------------------------------------
# SERVER SETTINGS
# ------------------------------------------------

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# ------------------------------------------------
# FIREBASE SETTINGS
# ------------------------------------------------

FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON", "")
FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL", "")

# ------------------------------------------------
# DOWNLOAD SETTINGS
# ------------------------------------------------

REQUEST_TIMEOUT_SECONDS = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", 60))
MAX_CAPTION_LENGTH = None
PREFERRED_QUALITY = "best"

# ------------------------------------------------
# CORS SETTINGS
# ------------------------------------------------

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
