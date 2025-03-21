import os
import requests
from flask import Flask, jsonify, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, start_http_server

app = Flask(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter("request_count", "Number of requests served")
ERROR_COUNT = Counter("error_count", "Number of errors encountered")


@app.route("/temperature", methods=["GET"])
def get_temperature():
    """Fetches temperature from OpenWeather API and determines status."""
    REQUEST_COUNT.inc()  # Increment request count

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        ERROR_COUNT.inc()  # Increment error count for missing API key
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
        app.logger.error(f"Error fetching data: {e}")
        ERROR_COUNT.inc()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    # Start Prometheus metrics server in the background
    start_http_server(8000)
    app.run(host="0.0.0.0", port=5000)
