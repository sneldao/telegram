#!/bin/bash

# Server details
SERVER_IP="157.180.36.156"
SERVER_USER="root"
SERVER_PATH="/opt/snel-telegram"

# Deploy files to server using rsync
echo "Syncing files to server..."
rsync -avz --exclude 'venv' --exclude '.git' --exclude 'logs' ./ $SERVER_USER@$SERVER_IP:$SERVER_PATH/

# SSH into server and restart the Docker container
echo "Restarting Docker container..."
ssh $SERVER_USER@$SERVER_IP "cd $SERVER_PATH && docker-compose -f docker-compose.prod.yml down && docker-compose -f docker-compose.prod.yml up -d"

# Open port 8443 in firewall
echo "Opening port 8443 in firewall..."
ssh $SERVER_USER@$SERVER_IP "iptables -A INPUT -p tcp --dport 8443 -j ACCEPT"

# Setup the webhook on Telegram API
echo "Setting up webhook with Telegram..."
BOT_TOKEN=$(grep "TELEGRAM_BOT_TOKEN" .env.prod | cut -d "=" -f2)
ssh $SERVER_USER@$SERVER_IP "cd $SERVER_PATH && curl -F \"url=https://$SERVER_IP:8443/$BOT_TOKEN\" -F \"certificate=@conf/ssl/webhook.pem\" https://api.telegram.org/bot$BOT_TOKEN/setWebhook"

# Verify webhook is set up correctly
echo -e "\nVerifying webhook info:"
ssh $SERVER_USER@$SERVER_IP "cd $SERVER_PATH && curl https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo"

echo "Deployment complete!"