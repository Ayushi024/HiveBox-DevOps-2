import os
import requests

# Define separate base URLs for version and temperature endpoints
VERSION_BASE_URL = "http://localhost:5001"
TEMPERATURE_BASE_URL = "http://localhost:5000"


def test_version_endpoint():
    """Integration test for /version endpoint"""
    os.environ["APP_VERSION"] = "2.0.0"  # Simulate a version change
    response = requests.get(f"{VERSION_BASE_URL}/version")
    assert response.status_code == 200
    assert response.json()["version"] == "2.0.0"


def test_temperature_endpoint():
    """Integration test for /temperature endpoint"""
    response = requests.get(f"{TEMPERATURE_BASE_URL}/temperature")
    assert response.status_code == 200
    assert "status" in response.json()  # Ensure status is returned
