#!/bin/bash
set -e

echo "Starting Caddy..."
docker compose up -d

echo "Starting Parabol..."
cd ./parabol
docker compose up -d
cd ..

echo "All services started."
