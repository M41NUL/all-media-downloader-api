from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import HOST, PORT, ALLOWED_ORIGINS
from version import VERSION

from routes import home
from routes import tiktok
from routes import instagram
from routes import facebook
from routes import auto
from routes import proxy

app = FastAPI(
    title="All Media Downloader API",
    version=VERSION,
    docs_url=None,
    redoc_url=None,
)

_origins_env = ALLOWED_ORIGINS
_is_wildcard = _origins_env == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins_env,
    allow_credentials=not _is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home.router)
app.include_router(tiktok.router)
app.include_router(instagram.router)
app.include_router(facebook.router)
app.include_router(auto.router)
app.include_router(proxy.router)

app.mount("/public", StaticFiles(directory="public"), name="public")


@app.on_event("startup")
def on_startup():
    import database
    database.increment_restart_count()
    _start_daily_restart_timer()

    from core.ytdlp_updater import start_background_updater
    start_background_updater()


def _start_daily_restart_timer():
    import os
    import threading

    RESTART_AFTER_SECONDS = 24 * 60 * 60

    def _restart():
        print(f"[auto-restart] {RESTART_AFTER_SECONDS}s elapsed, restarting process now.")
        os._exit(0)

    timer = threading.Timer(RESTART_AFTER_SECONDS, _restart)
    timer.daemon = True
    timer.start()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
