# ============================================
# MAIN FILE
# Application entry point, mounts routes and static files
# ============================================

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)
