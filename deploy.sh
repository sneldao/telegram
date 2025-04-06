#!/bin/bash

# Create necessary directories
mkdir -p data logs conf

# Copy configuration files
cp conf/config.template.json conf/config.prod.json

# Start the bot
docker-compose up -d

# Show logs
docker-compose logs -f 