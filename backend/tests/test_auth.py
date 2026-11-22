import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "0912345678", "password": "Password123@"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["user"]["phone"] == "0912345678"

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "0912345678", "password": "WrongPassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"

def test_register_and_login_flow():
    new_phone = "0987654321"
    reg_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Trần Thị B",
            "phone": new_phone,
            "password": "SecurePassword123",
            "role": "guardian"
        }
    )
    assert reg_response.status_code == 201
    assert reg_response.json()["data"]["phone"] == new_phone

    # Duplicate register rejected
    dup_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Trần Thị B",
            "phone": new_phone,
            "password": "SecurePassword123"
        }
    )
    assert dup_response.status_code == 400

    # Login with new account
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"phone": new_phone, "password": "SecurePassword123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]

    # Verify /me with token
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["full_name"] == "Trần Thị B"

def test_me_unauthorized():
    # Without header
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401

    # With garbage token
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer fake.token.here"})
    assert resp.status_code == 401
