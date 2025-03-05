"""Unit tests for the Sensor API Flask application."""

import unittest
from unittest.mock import patch
from sensor_api.app import app  # ✅ Correct import


class TestSensorAPI(unittest.TestCase):
    """Test cases for the Flask application."""

    def setUp(self):
        """Set up a test client for the Flask application."""
        self.client = app.test_client()

    @patch("sensor_api.app.requests.get")
    def test_temperature_endpoint_good_status(self, mock_get):
        """Test the /temperature endpoint returns 'Good' for normal temperatures."""

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"main": {"temp": 15}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "Good")

    @patch("sensor_api.app.requests.get")
    def test_temperature_endpoint_too_cold(self, mock_get):
        """Test the /temperature endpoint returns 'Too Cold' for low temperatures."""

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"main": {"temp": 5}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "Too Cold")

    @patch("sensor_api.app.requests.get")
    def test_temperature_endpoint_too_hot(self, mock_get):
        """Test the /temperature endpoint returns 'Too Hot' for high temperatures."""

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"main": {"temp": 40}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "Too Hot")

    @patch("sensor_api.app.requests.get")
    def test_temperature_api_failure(self, mock_get):
        """Test handling when the OpenWeather API fails (returns a 500 error)."""

        mock_get.return_value.status_code = 500

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)

    def test_temperature_missing_api_key(self):
        """Test handling of missing OpenWeather API key."""

        with patch.dict(app.config, {"OPENWEATHER_API_KEY": None}):
            response = self.client.get("/temperature")
            self.assertEqual(response.status_code, 500)
            self.assertIn("error", response.json)

    @patch("sensor_api.app.requests.get")
    def test_temperature_invalid_api_response(self, mock_get):
        """Test handling when the OpenWeather API returns an unexpected response."""

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}  # Missing "main" key

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
