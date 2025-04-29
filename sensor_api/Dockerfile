# Use a lightweight Python image
FROM python:3.12.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clean up the requirements.txt to reduce image size
RUN rm requirements.txt

# Install Redis CLI for Valkey (optional, useful for debugging)
RUN apt-get update && apt-get install -y redis-tools

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" myuser
USER myuser

# Copy application files (after installing dependencies to leverage Docker cache)
COPY . .

# Expose port 5000 for Flask API
EXPOSE 5000

# Run the application with Valkey (Redis-compatible) as the caching layer
ENTRYPOINT ["python", "sensor_api/app.py"]
