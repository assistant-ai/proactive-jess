#!/bin/bash

# Define variables
CONTAINER_NAME="jess_telegram_bot_dev"
IMAGE_NAME="jess_telegram_bot_image_dev"

echo "Stopping existing container..."
docker stop "${CONTAINER_NAME}"
docker rm "${CONTAINER_NAME}"

echo "Stopped and removed existing container."