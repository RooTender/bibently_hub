#!/bin/bash
set -e

echo "Stopping Parabol..."
cd ./parabol
docker compose down
cd ..

echo "All services stopped."
