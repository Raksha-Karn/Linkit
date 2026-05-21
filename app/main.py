from fastapi import FastAPI
from .database import Base, engine
from .routers import users, urls

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener", version="1.0.0")
app.include_router(users.router)
app.include_router(urls.router)

@app.get("/")
def health_check():
    return {"status": "ok"}