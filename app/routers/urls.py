from datetime import datetime, timedelta, timezone
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app import models, schema, auth
from app.database import get_db
import redis
import time
import os
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=int(os.getenv("REDIS_PORT", 6379)), decode_responses=True)

WINDOW_SIZE = 60   
LIMIT = 10   

def rate_limit(ip: str):
    key = f"rate:{ip}"
    now = time.time()

    pipeline = r.pipeline()
    pipeline.zremrangebyscore(key, 0, now - WINDOW_SIZE)
    pipeline.zadd(key, {str(now): now})
    pipeline.zcard(key)
    pipeline.expire(key, WINDOW_SIZE)

    _, _, count, _ = pipeline.execute()
    if count > LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests (sliding window limit exceeded)"
        )

router = APIRouter(tags=["urls"])

@router.post("/shorten", response_model=schema.URLOut)
def shorten_url(data: schema.URLCreate, request: Request, db: Session = Depends(get_db), email: str = Depends(auth.decode_token)):
    rate_limit(request.client.host)
    owner = db.query(models.User).filter(models.User.email == email).first()
    short_code = secrets.token_urlsafe(6)
    expire = datetime.utcnow() + timedelta(data.expires_days)
    url = models.URL(
        original_url=str(data.original_url),
        short_code=short_code,
        owner_id=owner.id,
        expires_at=expire
    )
    db.add(url); db.commit(); db.refresh(url)
    return url

@router.get("/r/{code}")
def redirect_url(code: str, request: Request, db: Session = Depends(get_db)):
    rate_limit(request.client.host)
    cache_key = f"url:{code}"
    cached_url = r.get(cache_key)
    if cached_url:
        print("Cache hit")
        return RedirectResponse(str(cached_url))
    print("Cache miss")
    url = db.query(models.URL).filter(models.URL.short_code == code).first()
    if not url:
        raise HTTPException(404)
    if url.expires_at and datetime.utcnow() > url.expires_at:
        raise HTTPException(410, detail="Link expired")
    r.setex(name=cache_key, value=url.original_url, time=3600)
    url.click_count += 1; db.commit()
    return RedirectResponse(url.original_url)

@router.get("/stats/{code}", response_model=schema.URLOut)
def get_stats(code: str, db: Session = Depends(get_db), email: str = Depends(auth.decode_token)):
    url = db.query(models.URL).filter(models.URL.short_code == code).first()
    if not url:
        raise HTTPException(404)
    return url