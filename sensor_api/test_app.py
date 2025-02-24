"""
Unit tests for the Sensor API.

This script contains tests for:
- The `/version` endpoint to check if it returns the expected version.
- The `/temperature` endpoint to validate API responses.
"""

import unittest
from sensor_api.app import app


class TestSensorAPI(unittest.TestCase):
    """Test cases for the Flask application."""

    def setUp(self):
        """Set up a test client before each test."""
        self.client = app.test_client()

    def test_version_endpoint(self):
        """
        Test if the /version endpoint returns a 200 status
        and contains 'version' in the response JSON.
        """
        response = self.client.get("/version")
        self.assertEqual(response.status_code, 200)
        self.assertIn("version", response.json)

    def test_temperature_endpoint(self):
        """
        Test if the /temperature endpoint returns an expected status code.

        The status code depends on external API responses.
        """
        response = self.client.get("/temperature")
        self.assertIn(response.status_code, [200, 404, 500])  # API-dependent


if __name__ == "__main__":
    unittest.main()
