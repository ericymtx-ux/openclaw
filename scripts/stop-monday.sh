#!/bin/bash
# Stop Monday Dashboard running on port 18790

# Find the PID of the process listening on 18790
PID=$(lsof -t -i :18790)

if [ -z "$PID" ]; then
  echo "Monday Dashboard is not running on port 18790."
else
  echo "Stopping Monday Dashboard (PID: $PID)..."
  kill -9 $PID
  echo "Monday Dashboard stopped."
fi
