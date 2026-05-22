from fastapi import FastAPI
from .routers import users, urls
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
import socket
from fastapi.staticfiles import StaticFiles
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_PATH = BASE_DIR / "frontend" / "index.html"


app = FastAPI(title="URL Shortener", version="1.0.0")
# app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204) 

app.include_router(users.router)
app.include_router(urls.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return FileResponse(FRONTEND_PATH)

@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)