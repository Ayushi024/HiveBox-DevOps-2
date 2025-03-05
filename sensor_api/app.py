import os
import logging
import requests
from flask import Flask, jsonify
from prometheus_client import Counter  # Import the missing Counter class

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Environment variables and Prometheus metrics
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY", "Delhi")

REQUEST_COUNT = Counter("api_requests_total", "Total API requests")


@app.route("/temperature", methods=["GET"])
def get_temperature():
    """Fetches the latest temperature data from OpenWeather API."""
    REQUEST_COUNT.inc()  # Increment API request counter

    # Check if API key is missing
    if not OPENWEATHER_API_KEY:
        logger.error("API key is missing.")
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
        if temp < 10:
            status = "Too Cold"
        elif temp <= 36:
            status = "Good"
        else:
            status = "Too Hot"

        logger.info(f"Temperature fetched successfully: {temp}°C, Status: {status}")
        return jsonify({"temperature_celsius": temp, "status": status}), 200

    except requests.exceptions.Timeout:
        logger.error("Timeout occurred while fetching temperature data.")
        return jsonify({"error": "Request timed out"}), 504
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching temperature data: {str(e)}")
        return jsonify({"error": "Failed to fetch temperature", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
