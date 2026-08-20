# All Media Downloader API

A Python FastAPI service that extracts direct video links, captions and metadata
from TikTok, Instagram and Facebook. The service is used both as a public web tool
and as a backend that any Telegram bot or other client can call.

## Features

- Separate API route for each platform
- Combined auto detect route that identifies the platform from the url
- Primary extraction engine using yt-dlp
- Automatic fallback scraper per platform when yt-dlp fails
- Full length Instagram captions with no truncation
- Firebase used only for stats and logs, not for full download history
- Live status page with uptime, CPU, RAM and download stats

## Project structure

```
main.py                 application entry point
config.py                environment configuration and developer info
database.py               firebase connection and stats logging
version.py                 version information

routes/
  home.py                   serves the status page and /api/stats
  tiktok.py                  /api/tiktok endpoint
  instagram.py                /api/instagram endpoint
  facebook.py                  /api/facebook endpoint
  auto.py                       /api/download endpoint, auto detects platform

core/
  detector.py                  detects platform from a url
  downloader.py                  primary yt-dlp extraction engine
  service.py                      orchestrates yt-dlp then fallback scraper
  system_stats.py                  cpu, ram and uptime monitoring
  models.py                         shared response models
  utils.py                           formatting helpers
  scrapers/
    tiktok_scraper.py                  fallback extractor for tiktok
    instagram_scraper.py                fallback extractor for instagram
    facebook_scraper.py                  fallback extractor for facebook

public/
  index.html                           status page
```

## Setup

1. Create a virtual environment and install dependencies

```
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your Firebase credentials

3. Run the server locally

```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Authentication

All `/api/*` download endpoints require an api key sent in the request header.

```
x-api-key: m41nul
```

Requests without a valid key return a 401 response. The key value is controlled
by the `API_KEY` environment variable.

## API endpoints

### GET /api/tiktok?url=

### GET /api/instagram?url=

### GET /api/facebook?url=

### GET /api/download?url=

Example request:

```
curl -H "x-api-key: m41nul" "https://your-server.com/api/tiktok?url=https://www.tiktok.com/@user/video/12345"
```

All endpoints return the same response shape:

```json
{
  "success": true,
  "caption": "full caption text",
  "title": "video title",
  "filename": "video title - All Media Downloader.mp4",
  "platform": "tiktok",
  "format": "mp4",
  "size": "12.30 MB",
  "duration": "00:45",
  "video_url": "https://direct-video-link",
  "thumbnail_url": "https://thumbnail-link",
  "quality": "hd",
  "proxy_token": "e262ea1e389042c7bd58e561381c2e09"
}
```

`filename` is the ready-to-use output filename (`<title/caption> - All Media Downloader.mp4`),
truncated automatically if the title is long, with unsafe filesystem characters stripped.

`proxy_token` is only present for TikTok, where the file is downloaded on the server first
(TikTok's CDN rejects direct fetches from a different server/process). For Facebook and
Instagram, `proxy_token` is `null` and `video_url` can be fetched directly or passed to
`/api/proxy-video`.

### GET /api/proxy-video

Streams the video back with a proper `Content-Disposition` header, so clients that save the
response directly to disk (browsers, Telegram bots, etc.) get the clean filename instead of a
raw video id.

```
GET /api/proxy-video?proxy_token=<token>&api_key=m41nul
GET /api/proxy-video?video_url=<url>&platform=facebook&filename=<name>&api_key=m41nul
```

- `proxy_token` — required for TikTok, returned by the download endpoints
- `video_url` + `platform` — for Facebook/Instagram, used instead of `proxy_token`
- `filename` — optional override; falls back to the resolved title-based filename

### GET /api/stats

Returns live server stats used by the status page, including uptime, cpu percent,
memory usage, download counters and recent activity.

### GET /api/ytdlp-status

Returns the currently installed yt-dlp version, the latest version known from PyPI, whether
auto-update is enabled, and the result of the last update check.

```json
{
  "installedVersion": "2026.07.04",
  "latestKnownVersion": "2026.07.04",
  "autoUpdateEnabled": true,
  "lastStatus": "up_to_date"
}
```

yt-dlp is kept current automatically: `requirements.txt` uses `yt-dlp>=...` so every Render
build pulls the latest release, and a background checker (interval controlled by
`YTDLP_UPDATE_CHECK_INTERVAL_SECONDS`, default 6 hours) also checks PyPI at runtime and
upgrades in place if a newer version is available. Disable with `YTDLP_AUTO_UPDATE=false`.

## Deployment on Render

1. Push this repository to GitHub
2. Create a new Web Service on Render and connect the repository
3. Render will detect `render.yaml` automatically, or set manually:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables `FIREBASE_CREDENTIALS_JSON` and `FIREBASE_DATABASE_URL`
   in the Render dashboard

## Firebase setup

1. Create a Firebase project and enable Realtime Database
2. Generate a service account key from Firebase project settings
3. Paste the full JSON content as the value of `FIREBASE_CREDENTIALS_JSON`
4. Set `FIREBASE_DATABASE_URL` to your database url, for example
   `https://your-project-id-default-rtdb.firebaseio.com`

## Developer

Md. Mainul Islam
CODEX-M41NUL

GitHub: https://github.com/M41NUL
Telegram: t.me/mdmainulislaminfo
Email: devmainulislam@gmail.com
