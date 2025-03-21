import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/temperature", methods=["GET"])
def get_temperature():
    """Fetches temperature from OpenWeather API and determines status."""
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return jsonify({"error": "API key missing"}), 500  # Return 500 if no API key

    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}&units=metric",
            timeout=5,
        )

        if response.status_code != 200:
            return (
                jsonify({"error": "Failed to fetch data"}),
                500,
            )  # Handle API failures

        data = response.json()

        if "main" not in data or "temp" not in data["main"]:
            return (
                jsonify({"error": "Invalid API response"}),
                500,
            )  # Handle invalid response

        temp = data["main"]["temp"]
        status = "Good" if 10 <= temp <= 30 else "Too Cold" if temp < 10 else "Too Hot"

        return jsonify({"temperature_celsius": temp, "status": status})

    except Exception as e:
        app.logger.error(f"Error fetching data: {e}")
        return (
            jsonify({"error": f"Unexpected error: {str(e)}"}),
            500,
        )  # Catch unexpected errors


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
