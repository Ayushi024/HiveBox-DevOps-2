import unittest
from unittest.mock import patch, Mock
import requests
from sensor_api.app import get_temperature


class TestTemperatureMock(unittest.TestCase):
    """Test temperature endpoint with mocked API response."""

    @patch("requests.get")
    def test_temperature_status_mock(self, mock_get):
        """Mock external temperature API response and check status"""

        # Create a mock Response object
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"main": {"temp": 20}}  # Mock JSON response
        mock_get.return_value = mock_response

        # Call the function
        response, status_code = get_temperature()

        # Verify response
        self.assertEqual(status_code, 200)
        self.assertEqual(response.get_json()["status"], "Good")

        # Mock different temperature values
        for temp, expected_status in [(5, "Too Cold"), (40, "Too Hot")]:
            mock_response.json.return_value = {"main": {"temp": temp}}
            response, status_code = get_temperature()
            self.assertEqual(status_code, 200)
            self.assertEqual(response.get_json()["status"], expected_status)

        # Simulate API failure
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Failed to fetch temperature"}
        response, status_code = get_temperature()
        self.assertEqual(status_code, 500)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
