# ============================================
# CORE MODULE - DETECTOR
# Detects which platform a given URL belongs to
# ============================================

import re

TIKTOK_PATTERN = re.compile(r"(tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com)", re.IGNORECASE)
INSTAGRAM_PATTERN = re.compile(r"(instagram\.com|instagr\.am)", re.IGNORECASE)
FACEBOOK_PATTERN = re.compile(r"(facebook\.com|fb\.watch|fb\.com|m\.facebook\.com)", re.IGNORECASE)


def detect_platform(url: str) -> str:
    if not url:
        return "unknown"

    if TIKTOK_PATTERN.search(url):
        return "tiktok"

    if INSTAGRAM_PATTERN.search(url):
        return "instagram"

    if FACEBOOK_PATTERN.search(url):
        return "facebook"

    return "unknown"


def is_supported(url: str) -> bool:
    return detect_platform(url) != "unknown"
