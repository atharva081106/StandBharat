import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "StandBharat API running"}

import uuid

def test_signup():
    email = f"test_{uuid.uuid4()}@example.com"
    # Create user
    response = client.post("/api/auth/signup", json={"email": email, "password": "password123", "name": "test"})
    assert response.status_code == 200
    assert response.json()["email"] == email
    
    # Login with same user
    response = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.cookies

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_health_db():
    response = client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "PostgreSQL" in data["version"]

def test_health_redis():
    response = client.get("/health/redis")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
