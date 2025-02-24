import os
import json
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()

def get_version():
    """Returns the application version from an environment variable."""
    version = os.getenv("APP_VERSION", "v0.0.1")  # Default version if not set
    # print(f"DEBUG: Retrieved Version = {version}")  # Debug print
    return json.dumps({"version": version})

if __name__ == "__main__":
    print(get_version())  # Prints JSON format
