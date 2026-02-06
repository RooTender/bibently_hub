#!/bin/bash
set -e

NETWORK_NAME="bibently_web"

if ! docker network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
  echo "Creating docker network: $NETWORK_NAME"
  docker network create "$NETWORK_NAME"
else
  echo "Docker network already exists: $NETWORK_NAME"
fi

echo "Starting Caddy..."
docker compose up -d

echo "Starting Parabol..."
cd ./parabol
docker compose up -d
cd ..

echo "All services started."
