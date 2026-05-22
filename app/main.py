from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from .routers import users, urls
import os
from threading import Thread
from app.worker import sync_clicks

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")  

app = FastAPI(title="URL Shortener", version="1.0.0")

@app.on_event("startup")
def start_worker():
    thread = Thread(target=sync_clicks, daemon=True)
    thread.start()
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(urls.router)

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)

@app.get("/health")
def health():
    return {"status": "ok"}

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)