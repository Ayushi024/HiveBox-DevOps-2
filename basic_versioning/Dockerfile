# Stage 1: Build stage
FROM python:3.12-slim AS build

# Set the working directory for the build stage
WORKDIR /app

# Copy only the requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies (including any build dependencies)
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final runtime image
FROM python:3.12-slim

# Set the working directory for the runtime stage
WORKDIR /app

# Copy the application files and installed dependencies from the build stage
COPY --from=build /app /app

# Expose the port for the Flask application
EXPOSE 5001

# Run the version service
CMD ["python", "app_version.py"]
