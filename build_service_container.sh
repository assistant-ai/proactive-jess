#!/bin/bash

CONTAINER_TAG="us-west1-docker.pkg.dev/jess-backend/cloud-run-source-deploy/proactive-jess/jess-backend"

docker build . -t "${CONTAINER_TAG}" -f ./Dockerfile.service
docker push "${CONTAINER_TAG}"
gcloud run services update jess-backend --project jess-backend --platform=managed --image=us-west1-docker.pkg.dev/jess-backend/cloud-run-source-deploy/proactive-jess/jess-backend:latest --region=us-west1
