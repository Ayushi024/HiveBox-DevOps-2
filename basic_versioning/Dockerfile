# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy files
COPY app_version.py .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5001 for this service
EXPOSE 5001

# Run the version service
CMD ["python", "app_version.py"]
