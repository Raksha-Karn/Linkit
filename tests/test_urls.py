from sqlalchemy import create_engine
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
import pytest
from app.main import app
from app.database import Base, get_db

TEST_DB = "sqlite:///./test.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    def override():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=engine)

def get_token(client):
    client.post("/auth/register", json={"email": "abc@mail.com", "password": "abc"})
    r = client.post("/auth/login", data={"username": "abc@mail.com", "password": "abc"})
    return r.json()["access_token"]

def test_register(client):
    r = client.post("/auth/register", json={"email": "test@yahoo.com", "password": "test123"})
    assert r.status_code == 200

def test_duplicate_register(client):
    client.post("/auth/register", json={"email": "test@yahoo.com", "password": "test123"})
    r = client.post("/auth/register", json={"email": "test@yahoo.com", "password": "test123"})
    assert r.status_code == 400

def test_shorten_url(client):
    token = get_token(client)
    r = client.post("/shorten", json={"original_url": "https://google.com"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "short_code" in r.json()

def test_redirect(client):
    token = get_token(client)
    r = client.post("/shorten", json={"original_url": "https://github.com"}, headers={"Authorization": f"Bearer {token}"})
    code = r.json()["short_code"]
    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.status_code == 307

def test_shorten_requires_auth(client):
    r = client.post("/shorten", json={"original_url": "https://google.com"})
    assert r.status_code == 401