# Snel Telegram Bot

A Python-based Telegram bot for cryptocurrency information and tracking. Built with security and scalability in mind.

## Features

- Real-time cryptocurrency price tracking
- Market data and analysis
- Configurable alerts and notifications
- Admin controls and rate limiting
- Secure environment variable management
- Production-ready Docker deployment

## Architecture

### Local Development

```
├── opencryptobot/     # Core bot logic
├── conf/              # Configuration files
│   ├── config.template.json    # Template configuration
│   └── config.prod.json        # Production configuration
├── docker-compose.yml         # Docker composition
├── Dockerfile                # Container definition
├── requirements.txt          # Python dependencies
└── run.sh                   # Startup script
```

### Production Deployment

- Hosted on dedicated VPS
- Docker containerization
- Environment variable management
- Persistent volume storage
- Health monitoring
- Automatic restarts

## Setup

### Prerequisites

- Python 3.7+
- Docker and Docker Compose
- Telegram Bot Token (from @BotFather)
- API Keys (optional, for enhanced functionality)

### Local Development

1. Clone the repository:

```bash
git clone <repository-url>
cd snel-telegram
```

2. Create environment file:

```bash
cp .env.template .env
# Edit .env with your configuration
```

3. Create configuration:

```bash
cp conf/config.template.json conf/config.json
# Edit conf/config.json with your settings
```

4. Run locally:

```bash
docker-compose up --build
```

### Production Deployment

1. Set up server environment:

```bash
# Copy production environment template
cp .env.prod.template .env.prod

# Copy production config template
cp conf/config.template.json conf/config.prod.json
```

2. Deploy to production:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Security

- **Webhook Mode**: More efficient than polling for production
- **Auto-scaling**: Handled by Kubernetes
- **Persistent Storage**: Data and logs are preserved
- **Health Checks**: Automatic monitoring and restart
- **SSL/TLS**: Secure webhook endpoints
- **Resource Limits**: Controlled CPU and memory usage

### Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `ENVIRONMENT`: Set to "production" for webhook mode
- `TELEGRAM_READ_TIMEOUT`: Connection timeout (default: 30)
- `TELEGRAM_CONNECT_TIMEOUT`: Connection timeout (default: 30)
- Additional API keys for various services (optional)

### Configuration Files

- `.env.prod`: Production environment variables
- `conf/config.prod.json`: Production bot configuration
- `.canine.yml`: Canine deployment configuration

### Monitoring and Maintenance

- View logs through Canine dashboard
- Monitor resource usage
- Set up alerts for errors
- Zero-downtime updates

## Security Notes

- Never commit sensitive data (tokens, keys, etc.)
- Use environment variables for secrets
- Keep SSL certificates secure
- Regularly update dependencies
- Monitor bot usage and rate limits

### General bot features

- Written in Python and fully open source
- Update notifications for new releases on GitHub
- Update your running bot to any release or branch
- Admin specific commands like `restart` and `shutdown`
- Every command is a plugin that can be enabled / disabled
- Custom rate limit per user or per user and command
- Use database to track usage or disable it all together
- Cache functionality (can be disabled)
- Run the bot locally or hosted on a server
- Powerful logging functionality
- Set up the bot by using command line arguments
- Bot can be administered by more then one user
- Data provided by seven different API providers
- BPMN diagrams for commands to understand the data flow
- Users can provide feedback about the bot
- Experimental inline-mode (only `price` command for now)
- Repeatedly send commands at specified time interval

### Command features

- Current price
- Price change over time
- Current and historical volume
- Market capitalization
- Candlestick charts
- Price and volume charts
- All Time High details
- Calculated value of coin quantity
- Find out where to buy a coin
- Sort trading pairs by volume
- Details about the team behind a coin
- Details about the people in a team
- Coin-specific news or filtered by keywords
- Return on Investment for a coin
- Details about ICO if there was one
- Whitepaper download
- Best and worst movers
- Compare different coins
- Google Trends chart for keywords
- Description for a coin
- Details about exchanges and toplist
- Details about coin development
- Social media links and stats
- Get a coin summary
- Global dominance, volume and market cap
- Coin logo and technical coin details
- Search for a coin by name
- Get latest Tweets from Twitter for a coin

## Configuration

### Environment Variables

Required variables (set in .env):

- `TELEGRAM_BOT_TOKEN`: Your bot token
- `ENVIRONMENT`: development/production
- `ADMIN_ID`: Telegram user ID for admin

This file holds the configuration for the bot. You have to at least edit the value for **admin_id**. Every else setting is optional.

- **admin_id**: This is a list of Telegram user IDs that will control the bot. You can just add your own user or multiple users if you want. If you don't know your Telegram user ID, get in a conversation with Telegram bot [@userinfobot](https://telegram.me/userinfobot) and if you write him he will return you your user ID.
- **telegram - read_timeout**: Read timeout in seconds as integer. Default Telegram value is about 5 seconds. Usually this value doesn't have to be changed.
- **telegram - connect_timeout**: Connect timeout in seconds as integer. Default Telegram value is about 5 seconds. Usually this value doesn't have to be changed.
- **webhook - listen**: Required for webhook mode. IP to listen to.
- **webhook - port**: Required for webhook mode. Port to listen on.
- **webhook - privkey_path**: Required for webhook mode. Path to private key (.pem file).
- **webhook - cert_path**: Required for webhook mode. Path to certificate (.pem file).
- **webhook - url**: Required for webhook mode. URL where the bot is hosted.
- **use_db**: If `true` then a new database file (SQLite) will be generated on first start and every usage of the bot will be recorded in this database. If `false`, no database will be used.
- **rate_limit - enabled**: If `true` then a rate limit for users will be activated so that only a specific number of requests in a specific timeframe are possible. If `false` then rate limit functionality will be disabled.
- **rate_limit - requests**: Number (integer) of API requests that are allowed for a specific timeframe (see _rate_limit - timespan_).
- **rate_limit - timespan**: Number (integer) of seconds for which the issued API requests will be counted. If the count exceeds the value in _rate_limit - requests_, the user will be informed and can not issue new requests until the timeframe is reached.
- **rate_limit - incl_cmd**: If `true` then the rate limit will be per command. If `false` then it doesn't matter which command you used. If you exceed the limit you can't issue any API calls anymore until the timeframe is over.
- **refresh_cache**: If `null` then caching is disabled and every API call will reach the API provider. It's highly recommanded to enabled caching. The timeframe to refresh the cache can be specified in seconds `s` or minutes `m` or hours `h` or days `d`. Example: `6h`.
- **update - github_user**: Only relevant if you want to provide your own updates. The GitHub username.
- **update - github_repo**: Only relevant if you want to provide your own updates. The GitHub repository that you want to do the updates from.
- **update - update_hash**: _This should not be changed_. The bot saves here the hash of the currently running bot (only if an update happened).
- **update - update_hash**: How ofter should the bot automatically check for updates? The timeframe can be specified in seconds `s` or minutes `m` or hours `h` or days `d`. Example: `1d`. To disable update checks, enter `null`.

### bot.token

Edit `conf/config.json` or `conf/config.prod.json`:

- Admin settings
- Rate limiting
- Database configuration
- Webhook settings (production)
- Cache refresh intervals

## Monitoring

- Docker container health checks
- Application logs
- Error reporting
- Performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

##### Charts

```
/c - Chart with price and volume
/cs - Candlestick chart for coin
```

##### Price

```
/51 - PoW 51% attack cost
/ath - All time high price for coin
/best - Best movers for hour or day
/ch - Price change over time
/ico - ICO info for coin
/p - Coin price
/roi - Return on Investment for a coin
/s - Price, market cap and volume
/v - Value of coin quantity
/worst - Worst movers for hour or day
```

##### General

```
/comp - Compare coins
/de - Show decentralization info
/des - Coin description
/dev - Development information
/ex - Exchange details and toplist
/g - Global crypto data
/i - General coin information
/m - Find exchanges to trade a coin
/pe - Info about person from a team
/re - Repeat any command periodically
/se - Search for symbol by coin name
/t - Info about team behind a coin
/top - List top 30 coins
/tr - Google Trends - Interest Over Time
/wp - Find whitepaper for a coin
```

##### News & Events

```
/ev - Show crypto events
/n - News about a coin
/soc - Social media details
/tw - Latest Tweets from Twitter
```

##### Utilities

```
/po - Info about mining pools
/wa - Details about wallets
```

##### Bot

```
/about - Information about bot
/bpmn - BPMN diagram for a command
/feedback - Send us your feedback
/man - Show how to use a command
/re - Repeat any command periodically
```

If you want to show a list of available commands as you type, open a chat with Telegram user [@BotFather](https://telegram.me/BotFather) and send the command `/setcommands`. Then choose the bot you want to activate the list for and after that send the list of commands with description. Something like this:

```
51 - PoW 51% attack cost
about - Information about bot
ath - All time high price for coin
best - Best movers for hour or day
bpmn - BPMN diagram for a command
c - Chart with price and volume
ch - Price change over time
comp - Compare coins
cs - Candlestick chart for coin
de - Show decentralization info
des - Coin description
dev - Development information
ev - Show crypto events
ex - Exchange details and toplist
feedback - Send us your feedback
g - Global crypto data
h - Show overview of all commands
i - General coin information
ico - ICO info for coin
m - Find exchanges to trade a coin
man - Show how to use a command
mc - Market capitalization
n - News about a coin
p - Coin price
pe - Info about person from a team
po - Info about mining pools
re - Repeat any command periodically
roi - Return on Investment for a coin
s - Price, market cap and volume
se - Search for symbol by coin name
soc - Social media details
t - Info about team behind a coin
top - List top 30 coins
tr - Google Trends - Interest Over Time
tw - Get newest tweets for coin
v - Value of coin quantity
vol - Volume for a coin
wa - Details about wallets
worst - Worst movers for hour or day
wp - Find whitepaper for a coin
```

## Disclaimer

I use this bot personally to check the current state of some coins but since all the data is relying on external APIs, i can't guarantee that all informations are correct. Please use with caution. **I can't be held responsible for anything!**

## Donating

Forked from **OpenCryptoBot**, please consider donating whatever amount you like to:

#### Bitcoin

```
1EoBYmfdJznJ21v8Uiiv44iJ2sDb6Bsqc1
```

#### Bitcoin Cash

```
qzken7mgslv0w9t4ycj4uganv66ljccsq5ngcepp6h
```

#### Ethereum (ETH)

```
0x15c3dB6f0f3cC3A187Cfa4b20605293a08b9Be46
```

#### Monero (XMR)

```
42eSjjHF63P3LtxcdeC71TT3ZCcGbTtk1aESTvfrz4VqYeKMFP9tbWhjmcUJZE3yVrgDjH8uZhnob9czCtm764cFDWYPe7c
```

#### How else can you support me?

If you can't or don't want to donate, please consider signing up on listed exchanges below. They are really good and by using these links to register an account they get a share of the trading-fee that you pay to the exchange if you execute a trade.

- [Binance](https://www.binance.com/?ref=16770868)
- [KuCoin](https://www.kucoin.com/#/?r=H3QdJJ)
