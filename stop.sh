#!/usr/bin/env bash
set -e

echo "Stopping services..."

for dir in */ ; do
  if [ -f "$dir/docker-compose.yaml" ]; then
    echo "→ Stopping $dir"
    (cd "$dir" && docker compose down || true)
  fi
done

echo
echo "Stopping gateway..."
docker compose down || true

echo
echo "All services stopped."
