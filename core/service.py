# ============================================
# CORE MODULE - SERVICE
# Orchestrates extraction: yt-dlp only, no scraper fallback
# ============================================

from core.downloader import extract_with_ytdlp, download_with_ytdlp, DownloaderError
from core import resolve_cache


class ExtractionFailedError(Exception):
    pass


def resolve_media(url: str, platform: str) -> dict:
    if platform == "tiktok":
        # Handing TikTok's resolved signed CDN url to a different
        # process/server to fetch later gets rejected by TikTok's CDN
        # (confirmed: still 403/502 even with yt-dlp's own resolved
        # headers). So for TikTok we download the actual file here, on
        # the same server that resolves it, in a single yt-dlp pass —
        # and cache the local file path under a token. The proxy
        # endpoint streams that file directly; no CDN url is ever
        # handed to the bot.
        try:
            file_path, result = download_with_ytdlp(url, platform)
        except DownloaderError as error:
            raise ExtractionFailedError(str(error))
        result["proxy_token"] = resolve_cache.put_file(file_path)
        return result

    try:
        return extract_with_ytdlp(url, platform)
    except DownloaderError as error:
        raise ExtractionFailedError(str(error))
