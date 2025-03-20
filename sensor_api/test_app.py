from sensor_api.app import app
import unittest
from unittest.mock import patch


class TestSensorAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("sensor_api.app.requests.get")
    def test_temperature_endpoint(self, mock_get):
        """Test different temperature values from OpenWeather API."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"main": {"temp": 15}}

        response = self.client.get("/temperature")
        print(response.status_code)
        print(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn("temperature_celsius", response.json)
        self.assertEqual(response.json["status"], "Good")

    @patch("os.getenv", return_value=None)  # Mock getenv to return None
    def test_temperature_missing_api_key(self, mock_getenv):
        """Test handling of missing OpenWeather API key."""
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "API key is missing or not set")
