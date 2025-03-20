import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/temperature", methods=["GET"])
def temperature():
    """Fetches temperature from OpenWeather API and determines status."""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")

        if not api_key:
            return jsonify({"error": "API key is missing or not set"}), 500

        city = "London"
        url = (
            f"http://api.openweathermap.org/data/2.5/weather?q={city}"
            f"&appid={api_key}&units=metric"
        )

        response = requests.get(url)

        if response.status_code != 200:
            return (
                jsonify(
                    {
                        "error": f"Failed to fetch data, status code: {response.status_code}"
                    }
                ),
                500,
            )

        data = response.json()

        # Validate API response
        if "main" not in data or "temp" not in data["main"]:
            return jsonify({"error": "Invalid API response format"}), 500

        temp = data["main"]["temp"]

        # Determine temperature status
        if temp < 10:
            status = "Too Cold"
        elif temp <= 30:
            status = "Good"
        else:
            status = "Too Hot"

        # Return temperature and status
        return jsonify({"temperature_celsius": temp, "status": status}), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    # Run Flask with debugging enabled for development
    app.run(host="0.0.0.0", port=5000, debug=True)
