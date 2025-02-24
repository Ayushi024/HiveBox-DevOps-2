# Use the official Python 3.12.7 slim image for a smaller footprint
FROM python:3.12.7-slim

# Set working directory inside the container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Copy dependencies file and install dependencies
COPY basic_versioning/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY basic_versioning/app.py .

# Create a non-root user for security and switch to it
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 5000 for Flask
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
