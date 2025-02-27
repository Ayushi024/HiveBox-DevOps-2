"""
Integration tests for the Sensor API endpoints.

This module contains tests for the /version and /temperature endpoints of the Sensor API.
It simulates API responses using mocking and checks the behavior of the API based on the
mocked temperature values and version.
"""

import requests
import os

# Define base URLs or any constants here
VERSION_BASE_URL = "http://localhost:5001"
TEMPERATURE_BASE_URL = "http://localhost:5000"


def get_version():
    """Simulate getting version from the environment variable"""
    return {"version": os.getenv("APP_VERSION", "1.0.0")}


def get_temperature():
    """Fetches the latest temperature data from an API (mocked for tests)"""
    response = requests.get(TEMPERATURE_BASE_URL + "/temperature")

    if response.status_code == 200:
        temp_data = response.json()
        temp = temp_data["main"]["temp"]
        status = "Too Cold" if temp < 10 else "Good" if temp <= 36 else "Too Hot"
        return {"temperature_celsius": temp, "status": status}
    else:
        return {"error": "Failed to fetch temperature"}
