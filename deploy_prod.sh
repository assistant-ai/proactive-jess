#!/bin/bash

rm .env
ln -s .env.prod .env 

# Define variables
CONTAINER_NAME="jess_telegram_bot"
IMAGE_NAME="jess_telegram_bot_image"

# Step 1: Stop and Remove the existing container (if it exists)
echo "Stopping existing container..."
docker stop "${CONTAINER_NAME}"
docker rm "${CONTAINER_NAME}"

# Step 2: Build the new image
echo "Building new Docker image..."
docker build -t "${IMAGE_NAME}" .

# Step 3: Run the new container
echo "Running new container..."
docker run -d --name "${CONTAINER_NAME}" "${IMAGE_NAME}"

echo "Deployment complete!"