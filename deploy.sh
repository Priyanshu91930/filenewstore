#!/bin/bash

# Stop and remove existing container if running
echo "Stopping existing filenewstore container..."
docker stop filenewstore || true
docker rm filenewstore || true

# Pull latest code
echo "Pulling latest code..."
git pull

# Build Docker image without caching
echo "Building Docker image..."
docker build --no-cache -t filenewstore .

# Run the container
echo "Running Docker container..."
docker run -d -p 8080:8080 --name filenewstore filenewstore

# Show logs
echo "Showing logs (Ctrl+C to exit)..."
docker logs -f filenewstore
