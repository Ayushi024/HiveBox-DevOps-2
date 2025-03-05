import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/version")
def version():
    """Returns the application version."""
    return jsonify({"version": "1.0.0"})


@app.route("/temperature")
def temperature():
    """Fetches temperature from OpenWeather API and determines status."""
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return jsonify({"error": "API key missing"}), 500  # ✅ Ensures API key is required

    try:
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={api_key}&units=metric"
        )
        data = response.json()

        if response.status_code != 200 or "main" not in data or "temp" not in data["main"]:
            return jsonify({"error": "Invalid API response"}), 500  # ✅ Handles bad responses

        temp = data["main"]["temp"]
        status = "Good" if 10 <= temp <= 30 else "Too Cold" if temp < 10 else "Too Hot"

        return jsonify({"temperature_celsius": temp, "status": status})

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500  # ✅ Catch unexpected errors


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
