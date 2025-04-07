# CI/CD Setup Guide

This document outlines how to set up continuous integration and continuous deployment (CI/CD) for the Snel Telegram Bot using different platforms.

## Why Use CI/CD?

Setting up CI/CD provides several key benefits:

1. **Automated Deployments**: When you push to your GitHub repository, the bot is automatically updated
2. **Simplified Infrastructure**: Manage your application through a user-friendly interface
3. **Zero-Downtime Updates**: Updates happen seamlessly without interrupting service
4. **Environment Management**: Easily manage environment variables and configurations
5. **Monitoring and Logging**: Built-in tools for tracking application performance

## Option 1: Dokku

[Dokku](https://dokku.com/) is a lightweight, open-source Platform as a Service (PaaS) that helps you build and manage the lifecycle of applications.

### Setup Steps

1. **Install Dokku on your server**:

   ```bash
   wget https://raw.githubusercontent.com/dokku/dokku/v0.28.4/bootstrap.sh
   sudo DOKKU_TAG=v0.28.4 bash bootstrap.sh
   ```

2. **Create a new Dokku application**:

   ```bash
   dokku apps:create snel-telegram
   ```

3. **Set up Docker options** (to expose port 443):

   ```bash
   dokku docker-options:add snel-telegram deploy,run "-p 443:443"
   ```

4. **Configure environment variables**:

   ```bash
   dokku config:set snel-telegram TELEGRAM_BOT_TOKEN=your_bot_token ENVIRONMENT=production
   ```

5. **Set up SSL certificates**:

   ```bash
   # Create directory for SSL certificates
   mkdir -p /var/lib/dokku/data/storage/snel-telegram/ssl

   # Generate certificates
   openssl req -newkey rsa:2048 -sha256 -nodes \
     -keyout /var/lib/dokku/data/storage/snel-telegram/ssl/webhook.key \
     -x509 -days 365 -out /var/lib/dokku/data/storage/snel-telegram/ssl/webhook.pem \
     -subj '/C=US/ST=State/L=City/O=Organization/CN=your-server-ip'

   # Mount certificates to the container
   dokku storage:mount snel-telegram /var/lib/dokku/data/storage/snel-telegram/ssl:/app/conf/ssl
   ```

6. **Add a remote to your local Git repository**:

   ```bash
   git remote add dokku dokku@your-server-ip:snel-telegram
   ```

7. **Deploy your application**:

   ```bash
   git push dokku main
   ```

8. **Set up webhook with Telegram**:
   ```bash
   curl -F "url=https://your-server-ip/your-bot-token" \
     -F "certificate=@/var/lib/dokku/data/storage/snel-telegram/ssl/webhook.pem" \
     https://api.telegram.org/bot<your-bot-token>/setWebhook
   ```

## Option 2: Coolify

[Coolify](https://coolify.io/) is a self-hostable Heroku/Netlify alternative.

### Setup Steps

1. **Install Coolify on your server**:

   ```bash
   wget -q https://get.coolify.io -O install.sh
   sudo bash ./install.sh
   ```

2. **Access Coolify Dashboard**: Open `http://your-server-ip:3000` in your browser

3. **Add your Git repository**:

   - Go to Sources > Add New Source > GitHub
   - Connect your GitHub account
   - Select your repository

4. **Create a new service**:

   - Click "New Service" > "Application"
   - Select your repository
   - Choose "Docker" as the deployment method
   - Use `docker-compose.prod.yml` as the configuration file

5. **Configure environment variables**:

   - Add `TELEGRAM_BOT_TOKEN` and `ENVIRONMENT=production`

6. **Configure SSL and ports**:

   - Enable "Expose port 443"
   - Enable SSL if using Coolify's built-in SSL

7. **Deploy your application**:

   - Click "Save" and then "Deploy"

8. **Set up webhook with Telegram** (after deployment):
   ```bash
   curl -F "url=https://your-server-ip/your-bot-token" \
     -F "certificate=@path/to/certificate.pem" \
     https://api.telegram.org/bot<your-bot-token>/setWebhook
   ```

## Option 3: Dokploy

[Dokploy](https://dokploy.com/) is a managed Dokku service that simplifies deployment.

### Setup Steps

1. **Sign up for Dokploy**: Create an account at [dokploy.com](https://dokploy.com)

2. **Connect your GitHub repository**:

   - Go to "Apps" > "Create App"
   - Connect to your GitHub account
   - Select your repository

3. **Configure your app**:

   - Select "Docker" as the deployment method
   - Use `docker-compose.prod.yml` as the configuration file
   - Configure environment variables: `TELEGRAM_BOT_TOKEN` and `ENVIRONMENT=production`

4. **Configure networking**:

   - Enable port 443
   - Set up custom domain if needed

5. **Deploy your app**:

   - Click "Deploy"

6. **Set up webhook with Telegram** (after deployment):
   ```bash
   curl -F "url=https://your-app-url/your-bot-token" \
     -F "certificate=@path/to/certificate.pem" \
     https://api.telegram.org/bot<your-bot-token>/setWebhook
   ```

## Notes on Repository Structure

For any of these deployment options, make sure your repository includes:

1. **docker-compose.prod.yml**: Defines your production services
2. **Dockerfile**: Contains instructions to build your container
3. **Configuration Templates**: `conf/config.prod.template.json` and `.env.prod.template`
4. **Documentation**: README.md and this CI/CD guide

## Post-Deployment Verification

After setting up CI/CD with any platform:

1. **Check webhook status**:

   ```bash
   curl https://api.telegram.org/bot<your-bot-token>/getWebhookInfo
   ```

2. **Verify bot functionality**:

   - Send a message to your bot on Telegram
   - Check logs for proper message processing

3. **Test the deployment pipeline**:
   - Make a small change to your code
   - Push to the repository
   - Verify the change is automatically deployed
