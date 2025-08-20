from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test the root endpoint"""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "name" in data
    assert "version" in data
    assert "api_version" in data
    assert "endpoints" in data

def test_healthcheck():
    """Test the health check endpoint"""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "timestamp" in data
    assert "model" in data

def test_api_v1_endpoints():
    """Test that API v1 endpoints are accessible"""
    # Test nikud endpoint
    res = client.post("/api/v1/add_nikud", json={"text": "שלום"})
    # Should either succeed or fail gracefully, but endpoint should exist
    assert res.status_code in [200, 422, 500]  # 422 for validation error, 500 for model loading
    
    # Test normalize endpoint
    res = client.post("/api/v1/normalize", json={"text": "שלום"})
    assert res.status_code in [200, 422, 500]
    
    # Test spellcheck endpoint
    res = client.post("/api/v1/spellcheck", json={"text": "שלום"})
    assert res.status_code in [200, 422, 500]
