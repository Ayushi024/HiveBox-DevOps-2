"""
This module contains the routes for the Sensor API, including:
- /version: Returns the version of the application.
- /temperature: Fetches temperature data from the OpenWeather API.
- /metrics: Exposes Prometheus metrics for monitoring.
"""

import os
import logging
import requests 
from flask import Flask, jsonify
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter

app = Flask(__name__)

# Environment variables and Prometheus metrics
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY", "Delhi")

REQUEST_COUNT = Counter("api_requests_total", "Total API requests")

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
        response = requests.get(url, timeout=5)  # Timeout to avoid long hanging
        response.raise_for_status()  # Raises HTTPError for bad responses

        data = response.json()
        temp = data["main"]["temp"]

        # Determine status based on temperature
        status = "Too Cold" if temp < 10 else "Good" if temp <= 36 else "Too Hot"

        return jsonify({"temperature_celsius": temp, "status": status}), 200

    except requests.exceptions.Timeout:
        logging.error(f"Timeout occurred while fetching temperature data.")
        return jsonify({"error": "Request timed out"}), 504
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching temperature data: {str(e)}")
        return jsonify({"error": "Failed to fetch temperature", "details": str(e)}), 500
