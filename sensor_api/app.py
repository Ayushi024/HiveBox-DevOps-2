import os
import json
import time
from threading import Thread
from datetime import datetime
import requests
import redis
from flask import Flask, jsonify, Response
from prometheus_client import (
    Counter,
    generate_latest,
    CONTENT_TYPE_LATEST,
    start_http_server,
)
from minio import Minio

app = Flask(__name__)

# ------------------------
# Prometheus Metrics
# ------------------------
REQUEST_COUNT = Counter("request_count", "Number of requests served")
ERROR_COUNT = Counter("error_count", "Number of errors encountered")

# ------------------------
# Valkey (Redis) Configuration
# ------------------------
redis_host = os.getenv("VALKEY_HOST", "localhost")
redis_port = int(os.getenv("VALKEY_PORT", 6379))
CACHE_TTL = 300  # Cache expiry in 5 minutes

# Initialize Redis/Valkey client
try:
    REDIS_CLIENT = redis.Redis(
        host=redis_host, port=redis_port, db=0, decode_responses=True
    )
    REDIS_CLIENT.ping()  # Check if Redis is running
    app.logger.info("✅ Redis connection successful")
except redis.ConnectionError as e:
    app.logger.error("❌ Redis connection failed: %s", str(e))
    REDIS_CLIENT = None

# ------------------------
# MinIO Configuration
# ------------------------
minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")

minio_host = minio_endpoint.replace("http://", "").replace("https://", "")

try:
    MINIO_CLIENT = Minio(
        minio_host,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )

    BUCKET_NAME = "sensor-data"

    # Ensure MinIO bucket exists
    if not MINIO_CLIENT.bucket_exists(BUCKET_NAME):
        MINIO_CLIENT.make_bucket(BUCKET_NAME)
        app.logger.info("✅ MinIO bucket '%s' created", BUCKET_NAME)
    else:
        app.logger.info("✅ MinIO bucket '%s' already exists", BUCKET_NAME)

except Exception as e:
    app.logger.error("❌ MinIO connection failed: %s", str(e))
    MINIO_CLIENT = None


# ------------------------
# /temperature Endpoint
# ------------------------
@app.route("/temperature", methods=["GET"])
def get_temperature():
    """Fetches temperature from OpenWeather API and determines status."""
    REQUEST_COUNT.inc()  # Increment request count

    # Check if cached data is available
    cached_data = REDIS_CLIENT.get("temperature_data") if REDIS_CLIENT else None
    if cached_data:
        return jsonify({"source": "cache", "data": json.loads(cached_data)})

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        ERROR_COUNT.inc()
        return jsonify({"error": "API key missing"}), 500

    try:
        # Get temperature data from OpenWeather API
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}&units=metric",
            timeout=5,
        )

        if response.status_code != 200:
            ERROR_COUNT.inc()
            return jsonify({"error": "Failed to fetch data"}), 500

        data = response.json()

        if "main" not in data or "temp" not in data["main"]:
            ERROR_COUNT.inc()
            return jsonify({"error": "Invalid API response"}), 500

        temp = data["main"]["temp"]
        status = "Good" if 10 <= temp <= 30 else "Too Cold" if temp < 10 else "Too Hot"

        temperature_data = {"temperature_celsius": temp, "status": status}

        # Cache the data in Redis/Valkey
        if REDIS_CLIENT:
            REDIS_CLIENT.setex(
                "temperature_data", CACHE_TTL, json.dumps(temperature_data)
            )

        return jsonify({"source": "API", "data": temperature_data})

    except Exception as e:
        app.logger.error("Error fetching data: %s", e)
        ERROR_COUNT.inc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


# ------------------------
# /store Endpoint
# ------------------------
@app.route("/store", methods=["POST"])
def store_data():
    """Stores sensor data to MinIO bucket manually."""
    try:
        if not MINIO_CLIENT:
            return jsonify({"error": "MinIO is not configured correctly"}), 500

        # Get cached temperature data
        redis_data = REDIS_CLIENT.get("temperature_data") if REDIS_CLIENT else None
        if not redis_data:
            return jsonify({"error": "No data available to store"}), 500

        # Prepare file name and content
        file_name = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        content = redis_data.encode("utf-8")

        # Upload data to MinIO
        MINIO_CLIENT.put_object(
            BUCKET_NAME, file_name, data=content, length=len(content)
        )

        return jsonify({"message": "Data stored successfully", "file": file_name})

    except Exception as e:
        app.logger.error("Error storing data: %s", e)
        return jsonify({"error": f"Failed to store data: {str(e)}"}), 500


# ------------------------
# /metrics Endpoint
# ------------------------
@app.route("/metrics", methods=["GET"])
def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


# ------------------------
# /readyz Endpoint
# ------------------------
@app.route("/readyz", methods=["GET"])
def readiness_check():
    """Returns 200 ready if system is healthy."""
    try:
        # Check Redis connection
        if REDIS_CLIENT and REDIS_CLIENT.ping():
            redis_status = "ready"
        else:
            redis_status = "Failure"

        # Check MinIO bucket
        if MINIO_CLIENT and MINIO_CLIENT.bucket_exists(BUCKET_NAME):
            minio_status = "ready"
        else:
            minio_status = "Failure"

        # Return combined status
        if redis_status == "ready" and minio_status == "ready":
            return jsonify({"status": "ready"}), 200
        else:
            return (
                jsonify(
                    {
                        "status": "Failure",
                        "reason": f"Redis: {redis_status}, MinIO: {minio_status}",
                    }
                ),
                500,
            )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "Failure",
                    "reason": f"Unexpected error: {str(e)}",
                }
            ),
            500,
        )


# ------------------------
# Periodic Data Storage to MinIO
# ------------------------
def store_data_periodically():
    """Stores data to MinIO every 5 minutes."""
    while True:
        try:
            if not MINIO_CLIENT:
                app.logger.warning("MinIO not configured, skipping periodic storage")
                time.sleep(300)
                continue

            redis_data = REDIS_CLIENT.get("temperature_data") if REDIS_CLIENT else None
            if redis_data:
                file_name = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
                content = redis_data.encode("utf-8")
                MINIO_CLIENT.put_object(
                    BUCKET_NAME, file_name, data=content, length=len(content)
                )
                app.logger.info("Stored data periodically: %s", file_name)
        except Exception as e:
            app.logger.error("Error in periodic data storage: %s", e)

        time.sleep(300)  # Sleep for 5 minutes


# ------------------------
# Start Background Thread for Periodic Data Storage
# ------------------------
Thread(target=store_data_periodically, daemon=True).start()

if __name__ == "__main__":
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)

    app.run(host="0.0.0.0", port=5000)
