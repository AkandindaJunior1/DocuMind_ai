from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test that the application starts and the health check responds."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "DocuMind API is running"}

def test_unauthorized_dashboard_access():
    """Test that protected routes return 401 without a token."""
    response = client.get("/dashboard/stats")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
