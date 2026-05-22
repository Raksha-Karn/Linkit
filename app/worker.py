import time
from app.database import SessionLocal
from app import models
import redis
import os
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

def sync_clicks():
    while True:
        print("Syncing clicks...")
        db = SessionLocal()

        try:
            keys = r.keys("clicks:*")

            for key in keys:
                code = key.split(":")[1]
                count = int(r.get(key) or 0)

                if count > 0:
                    url = db.query(models.URL).filter(models.URL.short_code == code).first()
                    if url:
                        url.click_count += count
                        db.commit()

                    r.set(key, 0)  

        except Exception as e:
            print("Sync error:", e)

        finally:
            db.close()

        time.sleep(30)  