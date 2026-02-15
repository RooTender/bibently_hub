#!/usr/bin/env bash
set -e

echo
echo "Starting services..."

for dir in */ ; do
  if [ -f "$dir/docker-compose.yaml" ]; then
    echo "→ Starting $dir"
    (cd "$dir" && docker compose up -d)
  fi
done

echo
echo "All services started."
