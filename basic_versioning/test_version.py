import os
import pytest
from basic_versioning.app_version import app

# Set environment variable before app loads
os.environ["APP_VERSION"] = "v1.2.3"


@pytest.fixture
def client():
    """Fixture for Flask test client with app context."""
    with app.test_client() as client:
        with app.app_context():  # Ensure Flask app context is active
            yield client


def test_version(client):
    """Test that /version endpoint returns the correct version in JSON format."""
    response = client.get("/version")

    # Check that the response status code is 200
    assert response.status_code == 200

    # Check that the response JSON contains the correct version
    json_data = response.get_json()
    assert "version" in json_data
    assert json_data["version"] == "v1.2.3"
