#!/bin/bash
set -e
echo "Starting IoT Home Energy Management Dashboard..."
uvicorn app:app --host 0.0.0.0 --port 9038 --workers 1
