import unittest
from unittest.mock import patch
import requests
from sensor_api.app import get_temperature

class TestTemperatureMock(unittest.TestCase):
    """
    Test case for mocking the temperature status based on environment settings.
    This test ensures that the temperature status is correctly determined
    from the mocked value of the temperature.
    """
    
    @patch("requests.get")
    def test_temperature_status_mock(self, mock_get):
        """Mock external temperature API response and check status"""
        
        # Create a mock Response object
        mock_response = requests.Response()

        # Mock successful response for temperature = 20 (Good status)
        mock_response.status_code = 200
        mock_response.json = lambda: {"main": {"temp": 20}}  # Mock the json() method
        mock_get.return_value = mock_response  # Return the mock response directly

        # Call the actual get_temperature function
        response, status_code = get_temperature()

        # Ensure that the returned status is "Good" for temperature 20
        self.assertEqual(status_code, 200)
        self.assertEqual(response.json["status"], "Good")

        # Mock another response for temperature = 5 (Too Cold status)
        mock_response.json = lambda: {"main": {"temp": 5}}  # Mock the json() method
        mock_get.return_value = mock_response  # Return the updated mock response

        response, status_code = get_temperature()
        self.assertEqual(status_code, 200)
        self.assertEqual(response.json["status"], "Too Cold")

        # Mock response for temperature = 40 (Too Hot status)
        mock_response.json = lambda: {"main": {"temp": 40}}  # Mock the json() method
        mock_get.return_value = mock_response  # Return the updated mock response

        response, status_code = get_temperature()
        self.assertEqual(status_code, 200)
        self.assertEqual(response.json["status"], "Too Hot")

        # Simulate failure response (e.g., 500 error)
        mock_response.status_code = 500
        mock_response.json = lambda: {"error": "Failed to fetch temperature"}  # Mock the json() method
        mock_get.return_value = mock_response  # Return the updated mock response

        response, status_code = get_temperature()
        self.assertEqual(status_code, 500)
        self.assertIn("error", response.json)

if __name__ == "__main__":
    unittest.main()