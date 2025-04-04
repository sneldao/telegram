#!/bin/bash

# Load environment variables
set -a
source .env
set +a

# Debug output
echo "Bot token from env: $TELEGRAM_BOT_TOKEN"

# Export connection settings to increase timeouts
export TELEGRAM_READ_TIMEOUT=30
export TELEGRAM_CONNECT_TIMEOUT=30

# Activate virtual environment if not in Docker
if [ -d "venv" ]; then
  source venv/bin/activate
fi

# Run with retry logic
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  echo "Starting bot (attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
  python -m opencryptobot -lvl 20
  
  EXIT_CODE=$?
  if [ $EXIT_CODE -eq 0 ]; then
    break
  fi
  
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
    echo "Bot exited with error, retrying in 10 seconds..."
    sleep 10
  else
    echo "Maximum retry attempts reached."
  fi
done