import unittest
from unittest.mock import patch
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

    @patch("sensor_api.app.requests.get")
    def test_temperature_endpoint(self, mock_get):
        """
        Test if the /temperature endpoint returns an expected status code
        and correct temperature status.
        """

        # Mock successful API response with temp = 15 (Good status)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"main": {"temp": 15}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertIn("temperature_celsius", response.json)
        self.assertEqual(response.json["status"], "Good")

        # Mock successful API response with temp = 5 (Too Cold status)
        mock_get.return_value.json.return_value = {"main": {"temp": 5}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "Too Cold")

        # Mock successful API response with temp = 40 (Too Hot status)
        mock_get.return_value.json.return_value = {"main": {"temp": 40}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "Too Hot")

        # Test for failed API response (e.g., 500)
        mock_get.return_value.status_code = 500
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)

        # Test for missing API key (simulate absence of OPENWEATHER_API_KEY)
        app.config["OPENWEATHER_API_KEY"] = None
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)


if __name__ == "__main__":
    unittest.main()
