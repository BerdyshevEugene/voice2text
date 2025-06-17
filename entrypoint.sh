#!/bin/sh
set -e

cd /app/src
uv run uvicorn main:app --host 0.0.0.0 --port 8000

exec "$@"
