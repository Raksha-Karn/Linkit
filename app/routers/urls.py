from datetime import datetime, timedelta, timezone
import secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app import models, schema, auth
from app.database import get_db

router = APIRouter(tags=["urls"])

@router.post("/shorten", response_model=schema.URLOut)
def shorten_url(data: schema.URLCreate, db: Session = Depends(get_db), email: str = Depends(auth.decode_token)):
    owner = db.query(models.User).filter(models.User.email == email).first()
    short_code = secrets.token_urlsafe(6)
    expire = datetime.now(timezone.utc) + timedelta(data.expires_days)
    url = models.URL(
        original_url=str(data.original_url),
        short_code=short_code,
        owner_id=owner.id,
        expires_at=expire
    )
    db.add(url); db.commit(); db.refresh(url)
    return url

@router.get("/{code}")
def redirect_url(code: str, db: Session = Depends(get_db)):
    url = db.query(models.URL).filter(models.URL.short_code == code).first()
    if not url:
        raise HTTPException(404)
    if url.expires_at and datetime.now(timezone.utc) > url.expires_at:
        raise HTTPException(410, detail="Link expired")
    url.click_count += 1; db.commit()
    return RedirectResponse(url.original_url)

@router.get("/stats/{code}", response_model=schema.URLOut)
def get_stats(code: str, db: Session = Depends(get_db), email: str = Depends(auth.decode_token)):
    url = db.query(models.URL).filter(models.URL.short_code == code).first()
    if not url:
        raise HTTPException(404)
    return url