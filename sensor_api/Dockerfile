# Use the official Python 3.12.7 slim image for a smaller footprint
FROM python:3.12.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Use bash shell with pipefail to handle errors properly
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies with pinned versions
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-pip="$(apt-cache madison python3-pip | awk '{print $3}' | head -1)" && \
    rm -rf /var/lib/apt/lists/*

# Copy only sensor_api directory
COPY sensor_api /app/sensor_api
COPY basic_versioning /app/basic_versioning 
COPY requirements.txt /app/requirements.txt  

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 5000 for Flask
EXPOSE 5000

# Run the Flask application
CMD ["python", "-m", "sensor_api.app"]
