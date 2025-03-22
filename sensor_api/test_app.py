import os
import unittest
from unittest.mock import patch
from sensor_api.app import app


class TestSensorAPI(unittest.TestCase):
    """Tests for the Sensor API endpoints."""

    def setUp(self):
        self.client = app.test_client()
        os.environ["OPENWEATHER_API_KEY"] = "test_api_key"

    @patch("sensor_api.app.requests.get")
    def test_temperature_endpoint(self, mock_get):
        """Test different temperature values from OpenWeather API."""
        # Test with temperature 15°C - "Good"
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"main": {"temp": 15}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["status"], "Good")

        # Test with temperature 5°C - "Too Cold"
        mock_get.return_value.json.return_value = {"main": {"temp": 5}}
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["status"], "Too Cold")

        # Test with temperature 40°C - "Too Hot"
        mock_get.return_value.json.return_value = {"main": {"temp": 40}}
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["status"], "Too Hot")

    @patch("sensor_api.app.requests.get")
    def test_temperature_invalid_api_response(self, mock_get):
        """Test handling when OpenWeather API returns unexpected response."""
        # Test with an invalid API response (empty JSON)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}  # Missing "main" key

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Invalid API response")

    @patch("sensor_api.app.os.getenv", return_value=None)  # Mock getenv to return None
    def test_temperature_missing_api_key(self, mock_getenv):
        """Test handling of missing OpenWeather API key."""
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], "API key missing"
        )  # Ensure correct message

    @patch("sensor_api.app.requests.get")
    def test_temperature_api_failure(self, mock_get):
        """Test handling of API failure (non-200 status code)."""
        mock_get.return_value.status_code = 500
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Failed to fetch data")

    @patch("sensor_api.app.requests.get", side_effect=Exception("API Timeout"))
    def test_temperature_api_exception(self, mock_get):
        """Test handling of API exceptions (e.g., timeout)."""
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertTrue("Unexpected error" in response.json["error"])
