# Use a lightweight Python image
FROM python:3.12.7-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY sensor_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clean up the requirements.txt to reduce image size
RUN rm requirements.txt

# Create a non-root user to run the application
RUN adduser --disabled-password myuser
USER myuser

# Copy application files (after installing dependencies to leverage Docker cache)
COPY . .

# Expose port 5000 for Flask
EXPOSE 5000

# Run the application
ENTRYPOINT ["python", "sensor_api/app.py"]
