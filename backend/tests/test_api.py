from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "antiscam-backend"

def test_mock_verify_demo_endpoint():
    response = client.get("/api/v1/mock/verify-demo?account_number=1029384756")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["entity_value"] == "1029384756"
    assert data["data"]["risk_level"] == "CRITICAL"
    assert len(data["data"]["what_if_scenarios"]) >= 3

def test_verify_entity_api_fast_path():
    payload = {
        "entity_type": "phone_number",
        "value": "0987654321"
    }
    response = client.post("/api/v1/verify/entity", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["risk_level"] == "CRITICAL"
    assert res["data"]["trigger_sos"] is True

def test_verify_vietqr_api():
    payload = {
        "qr_payload": "https://img.vietqr.io/image/970422-1029384756-compact2.png"
    }
    response = client.post("/api/v1/verify/vietqr", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["bank_bin"] == "970422"
    assert res["data"]["bank_name"] == "MBBank"
    assert res["data"]["account_number"] == "1029384756"

def test_verify_image_phash_api():
    payload = {
        "phash": "a1b2c3d4e5f60718"
    }
    response = client.post("/api/v1/verify/image-phash", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["is_duplicate_scam_image"] is True
    assert res["data"]["min_hamming_distance"] == 0
