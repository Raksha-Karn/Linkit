from fastapi import FastAPI
from .routers import users, urls


app = FastAPI(title="URL Shortener", version="1.0.0")
app.include_router(users.router)
app.include_router(urls.router)

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)