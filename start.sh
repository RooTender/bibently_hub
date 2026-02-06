#!/bin/bash
set -e

echo "Starting Parabol..."
cd ./parabol
docker compose up -d
cd ..

echo "All services started."
