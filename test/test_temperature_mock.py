import unittest
from unittest.mock import patch
from sensor_api.app import get_temperature

class TestTemperatureMock(unittest.TestCase):
    @patch("os.getenv", return_value="15")
    def test_temperature_status_mock(self, mock_env):
        """Mock environment variable for temperature"""
        response = get_temperature()
        self.assertEqual(response.json["status"], "Good")

if __name__ == "__main__":
    unittest.main()
