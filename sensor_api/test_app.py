import os
import unittest
from unittest.mock import patch
from sensor_api.app import app


class TestSensorAPI(unittest.TestCase):
    """Tests for the Sensor API endpoints."""

    def setUp(self):
        self.client = app.test_client()
        os.environ["OPENWEATHER_API_KEY"] = "test_api_key"

    # ===========================
    # /temperature Endpoint Tests
    # ===========================

    @patch("sensor_api.app.requests.get")
    def test_temperature_endpoint(self, mock_get):
        """Test different temperature values from OpenWeather API."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"main": {"temp": 15}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "Good")

        mock_get.return_value.json.return_value = {"main": {"temp": 5}}
        response = self.client.get("/temperature")
        self.assertEqual(response.json["status"], "Too Cold")

        mock_get.return_value.json.return_value = {"main": {"temp": 40}}
        response = self.client.get("/temperature")
        self.assertEqual(response.json["status"], "Too Hot")

    @patch("sensor_api.app.requests.get")
    def test_temperature_invalid_api_response(self, mock_get):
        """Test handling when OpenWeather API returns unexpected response."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}  # Missing "main" key

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)

    @patch("sensor_api.app.requests.get")
    def test_temperature_invalid_json_response(self, mock_get):
        """Test handling when OpenWeather API returns invalid JSON."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Error parsing API response")

    @patch("sensor_api.app.os.getenv", return_value=None)
    def test_temperature_missing_api_key(self, mock_getenv):
        """Test handling of missing OpenWeather API key."""
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(
            response.json["error"], "API key missing"
        )  # Ensure correct message

    @patch("sensor_api.app.redis_client.get", return_value=None)
    @patch("sensor_api.app.requests.get")
    def test_temperature_no_cache_data(self, mock_get, mock_redis_get):
        """Test fetching temperature when no cache is available."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"main": {"temp": 25}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "Good")
        self.assertEqual(response.json["source"], "api")

    @patch("sensor_api.app.redis_client.get")
    def test_temperature_cached_data(self, mock_redis_get):
        """Test fetching temperature data from cache."""
        mock_redis_get.return_value = b'{"temp": 20, "status": "Good"}'

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["source"], "cache")
        self.assertEqual(response.json["data"]["status"], "Good")

    @patch("sensor_api.app.requests.get")
    def test_temperature_invalid_value(self, mock_get):
        """Test handling of invalid temperature values from OpenWeather API."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"main": {"temp": "invalid"}}

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Invalid temperature value")

    # ===========================
    # /readyz Endpoint Tests
    # ===========================

    def test_readyz_endpoint(self):
        """Test /readyz endpoint to check service readiness."""
        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ready")

    @patch("sensor_api.app.redis_client.ping", side_effect=Exception("Redis error"))
    @patch("sensor_api.app.minio_client.bucket_exists", return_value=True)
    def test_readyz_dependency_failure(self, mock_bucket_exists, mock_redis_ping):
        """Test /readyz endpoint when a dependency check fails."""
        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json["status"], "not ready")

    # ===========================
    # /store Endpoint Tests
    # ===========================

    @patch("sensor_api.app.minio_client.put_object")
    def test_store_manual_trigger(self, mock_put_object):
        """Test /store endpoint to trigger manual storage to MinIO."""
        mock_put_object.return_value = None
        response = self.client.post("/store")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Data stored successfully")

    @patch(
        "sensor_api.app.minio_client.put_object", side_effect=Exception("Storage error")
    )
    def test_store_failure(self, mock_put_object):
        """Test /store endpoint handling storage error."""
        response = self.client.post("/store")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Failed to store data in MinIO")

    # ===========================
    # MinIO Connection Tests
    # ===========================

    @patch("sensor_api.app.minio_client.bucket_exists", return_value=False)
    def test_minio_connection_failure(self, mock_bucket_exists):
        """Test MinIO connection failure."""
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "MinIO connection error")

    @patch("sensor_api.app.minio_client.bucket_exists", return_value=False)
    @patch(
        "sensor_api.app.minio_client.make_bucket",
        side_effect=Exception("Bucket creation failed"),
    )
    def test_minio_bucket_creation_failure(self, mock_make_bucket, mock_bucket_exists):
        """Test failure when MinIO bucket creation fails."""
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "MinIO bucket creation failed")

    # ===========================
    # Cache Tests
    # ===========================

    @patch("sensor_api.app.redis_client.set")
    def test_cache_temperature_data(self, mock_redis_set):
        """Test caching temperature data after API fetch."""
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        mock_redis_set.assert_called_once_with(
            "temperature_data",
            b'{"temp": 15, "status": "Good"}',
            ex=300,
        )


if __name__ == "__main__":
    unittest.main()
