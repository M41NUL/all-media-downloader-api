from core.downloader import extract_with_ytdlp, download_with_ytdlp, DownloaderError
from core import resolve_cache


class ExtractionFailedError(Exception):
    pass


def resolve_media(url: str, platform: str) -> dict:
    if platform == "tiktok":
        try:
            file_path, result = download_with_ytdlp(url, platform)
        except DownloaderError as error:
            raise ExtractionFailedError(str(error))
        result["proxy_token"] = resolve_cache.put_file(file_path, filename=result.get("filename"))
        return result

    try:
        return extract_with_ytdlp(url, platform)
    except DownloaderError as error:
        raise ExtractionFailedError(str(error))
