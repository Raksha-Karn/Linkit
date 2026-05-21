from fastapi import FastAPI
from .routers import users, urls
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="URL Shortener", version="1.0.0")
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
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)