#!/bin/bash
set -e

echo "Stopping Parabol..."
cd ./parabol
docker compose down
cd ..

echo "Stopping Caddy..."
docker compose down

echo "All services stopped."
