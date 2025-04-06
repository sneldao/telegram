#!/bin/bash

# Set default configuration file
CONFIG_FILE=${CONFIG_FILE:-"conf/config.json"}

# Load environment variables
set -a
if [ -f ".env" ]; then
    source .env
fi
set +a

# Debug output
echo "Bot token from env: $TELEGRAM_BOT_TOKEN"
echo "Environment: $ENVIRONMENT"
echo "Config file: $CONFIG_FILE"

# Export connection settings to increase timeouts
export TELEGRAM_READ_TIMEOUT=30
export TELEGRAM_CONNECT_TIMEOUT=30

# Activate virtual environment if not in Docker
if [ -d "venv" ]; then
  source venv/bin/activate
fi

# Function to start the bot
start_bot() {
    # Run in polling mode for testing
    python3 -u opencryptobot/start.py -cfg "$CONFIG_FILE" -lvl 10
}

# Retry logic
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "Starting bot (attempt $((RETRY_COUNT + 1)) of $MAX_RETRIES)..."
    start_bot
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Bot stopped gracefully"
        break
    else
        echo "Bot crashed with exit code $EXIT_CODE"
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "Retrying in 5 seconds..."
            sleep 5
        else
            echo "Max retries reached. Exiting..."
            exit 1
        fi
    fi
done