# ============================================
# CORE MODULE - SERVICE
# Orchestrates extraction: yt-dlp only, no scraper fallback
# ============================================

from core.downloader import extract_with_ytdlp, DownloaderError


class ExtractionFailedError(Exception):
    pass


def resolve_media(url: str, platform: str) -> dict:
    try:
        return extract_with_ytdlp(url, platform)
    except DownloaderError as error:
        raise ExtractionFailedError(str(error))
