import os
import pytest
from basic_versioning.app_version import app

@pytest.fixture
def client():
    """Fixture for Flask test client."""
    with app.test_client() as client:
        yield client

def test_version(client):
    """Test that /version endpoint returns the correct version in JSON format."""
    # Set the environment variable for testing
    os.environ["APP_VERSION"] = "v1.2.3"

    # Send a GET request to the /version endpoint
    response = client.get("/version")

    # Check that the response status code is 200
    assert response.status_code == 200

    # Check that the response JSON contains the correct version
    json_data = response.get_json()
    assert "version" in json_data
    assert json_data["version"] == "v1.2.3"
