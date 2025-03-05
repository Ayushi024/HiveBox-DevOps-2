"""Flask application for handling sensor data."""

from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)


@app.route("/version")
def version():
    """Return API version."""
    return jsonify({"version": "1.0.0"})


@app.route("/temperature")
def temperature():
    """Fetch temperature data from OpenWeather API and return temperature status."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return jsonify({"error": "Missing API key"}), 500

    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}&units=metric"
    )
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch temperature"}), 500

    temp = response.json()["main"]["temp"]
    status = "Good" if 10 <= temp <= 30 else "Too Hot" if temp > 30 else "Too Cold"

    return jsonify({"temperature_celsius": temp, "status": status})
