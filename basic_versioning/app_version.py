import os
import json
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    """Root endpoint to show a welcome message."""
    return jsonify({"message": "Welcome to the Basic Versioning API!"})

@app.route("/version")
def get_version():
    """Returns the application version from an environment variable."""
    version = os.getenv("APP_VERSION", "v0.0.1")  # Default version if not set
    return jsonify({"version": version}), 200  # Explicit 200 status code

if __name__ == "__main__":
    # Set debug mode from environment variable (default to False if not set)
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ["true", "1", "t"]
    app.run(host="0.0.0.0", port=5001, debug=debug_mode)
