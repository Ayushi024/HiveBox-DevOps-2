import os
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

# Prometheus Metrics
REQUEST_COUNT = Counter("request_count", "Number of requests served")
ERROR_COUNT = Counter("error_count", "Number of errors encountered")

# Valkey (Redis) Configuration
redis_host = os.getenv("VALKEY_HOST", "localhost")
redis_port = int(os.getenv("VALKEY_PORT", 6379))
redis_client = redis.Redis(
    host=redis_host, port=redis_port, db=0, decode_responses=True
)

# MinIO Configuration
minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
    secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
    secure=False,
)

BUCKET_NAME = "sensor-data"

# Ensure MinIO bucket exists
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)

    # /temperature Endpoint


@app.route("/temperature", methods=["GET"])
def get_temperature():
    """Fetches temperature from OpenWeather API and determines status."""
    REQUEST_COUNT.inc()  # Increment request count

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        ERROR_COUNT.inc()
        return jsonify({"error": "API key missing"}), 500

    try:
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

        return jsonify({"temperature_celsius": temp, "status": status})

    except Exception as e:
        app.logger.error("Error fetching data: %s", e)
        ERROR_COUNT.inc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


@app.route("/store", methods=["POST"])
def store_data():
    """Stores sensor data to MinIO bucket manually."""
    try:
        # Get cached temperature data
        redis_data = redis_client.get("temperature_data")
        if not redis_data:
            return jsonify({"error": "No data available to store"}), 500

        # Prepare file name and content
        file_name = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        content = str(redis_data).encode("utf-8")

        # Upload data to MinIO
        minio_client.put_object(
            BUCKET_NAME, file_name, data=content, length=len(content)
        )

        return jsonify({"message": "Data stored successfully", "file": file_name})

    except Exception as e:
        app.logger.error("Error storing data: %s", e)
        return (
            jsonify({"error": f"Failed to store data: {str(e)}"}),
            500,
        )  # Use f-string here


@app.route("/readyz", methods=["GET"])
def readiness_check():
    """Returns 200 OK if system is healthy."""
    try:
        # Check if cache has fresh data
        cached_data = redis_client.get("temperature_data")
        if not cached_data:
            return jsonify({"status": "Failure", "reason": "Cache is empty"}), 500

        # Check API Health
        if check_senseboxes_health():
            return jsonify({"status": "OK"}), 200
        else:
            return (
                jsonify({"status": "Failure", "reason": "SenseBox Health Failing"}),
                500,
            )
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


def check_senseboxes_health():
    """Dummy function to simulate senseBox health check."""
    return True


def store_data_periodically():
    """Stores data to MinIO every 5 minutes."""
    while True:
        try:
            redis_data = redis_client.get("temperature_data")
            if redis_data:
                file_name = f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
                content = str(redis_data).encode("utf-8")
                minio_client.put_object(
                    BUCKET_NAME, file_name, data=content, length=len(content)
                )
                app.logger.info("Stored data periodically: %s", file_name)
        except Exception as e:
            app.logger.error("Error in periodic data storage: %s", e)

        time.sleep(300)


Thread(target=store_data_periodically, daemon=True).start()

if __name__ == "__main__":

    start_http_server(8000)

    app.run(host="0.0.0.0", port=5000)
