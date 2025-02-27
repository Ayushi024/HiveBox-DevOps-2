"""
Sensor API - Provides temperature data, version info, and metrics.

This Flask application fetches temperature data from the OpenWeather API,
exposes an endpoint to get the current version of the app, and provides
Prometheus metrics for monitoring.
"""

import os
import sys
import json
import logging
from flask import Flask, jsonify
import requests
from dotenv import load_dotenv
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter

# Ensure Python can find `basic_versioning`
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

try:
    from basic_versioning.app_version import get_version
except ModuleNotFoundError:
    raise ImportError(
        "⚠️ Could not import 'basic_versioning'. Check your project structure."
    )

# Load environment variables from .env (for local development)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

# Get API key securely from environment variables
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY", "Delhi")  # Default city

if not os.getenv("CITY"):
    logging.warning("CITY is not set! Using default: 'Delhi'.")

# Prometheus metrics
REQUEST_COUNT = Counter("api_requests_total", "Total API requests")


@app.route("/", methods=["GET"])
def home():
    """Default route to guide users."""
    return (
        jsonify(
            {
                "message": "Welcome to the Sensor API!",
                "instructions": {
                    "Get Version": "Visit /version",
                    "Get Temperature": "Visit /temperature",
                    "Get Metrics": "Visit /metrics",
                },
            }
        ),
        200,
    )


@app.route("/version", methods=["GET"])
def get_version_endpoint():
    """Returns the application version from basic_versioning."""
    try:
        version = json.loads(get_version())  # Convert JSON string to dict
        return jsonify(version)
    except Exception as e:
        logging.error(f"Error fetching version: {str(e)}")
        return jsonify({"error": "Failed to fetch version"}), 500


@app.route("/temperature", methods=["GET"])
def get_temperature():
    """Fetches the latest temperature data from OpenWeather API."""
    REQUEST_COUNT.inc()  # Increment API request counter

    if not OPENWEATHER_API_KEY:
        return jsonify({"error": "API key is missing!"}), 500

    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=5)  # Added timeout to prevent long hangs
        response.raise_for_status()  # Raise error for HTTP issues

        data = response.json()
        temp = data["main"]["temp"]

        # Determine status based on temperature
        status = "Too Cold" if temp < 10 else "Good" if temp <= 36 else "Too Hot"

        return jsonify({"temperature_celsius": temp, "status": status})

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching temperature data: {str(e)}")
        return jsonify({"error": "Failed to fetch temperature", "details": str(e)}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    """Returns Prometheus metrics."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    logging.info("Starting Sensor API on port 5000...")
    app.run(debug=True, host="0.0.0.0", port=5000)
