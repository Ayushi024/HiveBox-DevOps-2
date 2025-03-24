import os
import unittest
from unittest.mock import patch, MagicMock
from sensor_api.app import app


class TestSensorAPI(unittest.TestCase):
    """Tests for the Sensor API endpoints."""

    def setUp(self):
        """Set up test client and mock external dependencies."""
        self.client = app.test_client()
        os.environ["OPENWEATHER_API_KEY"] = "test_api_key"

        # Patch and
        # mock REDIS_CLIENT and MINIO_CLIENT
        self.redis_patch = patch("sensor_api.app.REDIS_CLIENT", new_callable=MagicMock)
        self.minio_patch = patch("sensor_api.app.MINIO_CLIENT", new_callable=MagicMock)

        # Start patches and assign to attributes
        self.mock_redis = self.redis_patch.start()
        self.mock_minio = self.minio_patch.start()

        # Add cleanup to stop patching after tests
        self.addCleanup(self.redis_patch.stop)
        self.addCleanup(self.minio_patch.stop)

        # Mock MinIO methods
        self.mock_minio.bucket_exists.return_value = True
        self.mock_minio.put_object.return_value = None
        self.mock_minio.make_bucket.return_value = None

        # Mock Redis methods
        self.mock_redis.get.return_value = None
        self.mock_redis.setex.return_value = True
        self.mock_redis.ping.return_value = True

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
        self.assertEqual(response.json["data"]["status"], "Good")

        mock_get.return_value.json.return_value = {"main": {"temp": 5}}
        response = self.client.get("/temperature")
        self.assertEqual(response.json["data"]["status"], "Too Cold")

        mock_get.return_value.json.return_value = {"main": {"temp": 40}}
        response = self.client.get("/temperature")
        self.assertEqual(response.json["data"]["status"], "Too Hot")

    @patch("sensor_api.app.requests.get")
    def test_temperature_invalid_api_response(self, mock_get):
        """Test handling when OpenWeather API returns unexpected response."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {}  # Missing "main" key

        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)

    # ===========================
    # /readyz Endpoint Tests
    # ===========================

    def test_readyz_endpoint(self):
        """Test /readyz endpoint to check service readiness."""
        self.mock_redis.ping.return_value = True
        self.mock_minio.bucket_exists.return_value = True

        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ready")

    def test_readyz_dependency_failure(self):
        """Test /readyz endpoint when a dependency check fails."""
        self.mock_redis.ping.side_effect = Exception("Redis error")
        self.mock_minio.bucket_exists.return_value = True

        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 500)
        self.assertIn("status", response.json)
        self.assertEqual(response.json["status"], "Failure")

    # ===========================
    # /store Endpoint Tests
    # ===========================

    def test_store_manual_trigger(self):
        """Test /store endpoint to trigger manual storage to MinIO."""
        self.mock_redis.get.return_value = (
            '{"temperature_celsius": 20, "status": "Good"}'
        )
        self.mock_minio.put_object.return_value = None

        response = self.client.post("/store")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "Data stored successfully")

    def test_store_failure(self):
        """Test /store endpoint handling storage error."""
        self.mock_redis.get.return_value = (
            '{"temperature_celsius": 20, "status": "Good"}'
        )
        self.mock_minio.put_object.side_effect = Exception("Storage error")

        response = self.client.post("/store")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertIn("Failed to store data", response.json["error"])

    def test_store_no_data_available(self):
        """Test /store endpoint when no data is available to store."""
        self.mock_redis.get.return_value = None

        response = self.client.post("/store")
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "No data available to store")

    # ===========================
    # MinIO Connection Tests
    # ===========================

    def test_minio_bucket_creation_failure(self):
        """Test failure when MinIO bucket creation fails."""
        self.mock_minio.bucket_exists.return_value = False
        self.mock_minio.make_bucket.side_effect = Exception("Bucket creation failed")

        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 500)
        self.assertIn("status", response.json)
        self.assertEqual(response.json["status"], "Failure")

    def test_minio_bucket_not_exists(self):
        """Test MinIO bucket existence failure."""
        self.mock_minio.bucket_exists.return_value = False

        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 500)
        self.assertIn("status", response.json)
        self.assertEqual(response.json["status"], "Failure")

    # ===========================
    # Cache Tests
    # ===========================

    # def test_cache_temperature_data(self):
    #     """Test caching temperature data after API fetch."""
    #     self.mock_redis.setex.return_value = True
    #     response = self.client.get("/temperature")
    #     self.assertEqual(response.status_code, 200)
    #     self.mock_redis.setex.assert_called()


if __name__ == "__main__":
    unittest.main()
