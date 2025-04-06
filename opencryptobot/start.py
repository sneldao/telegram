import os
import json
import logging
import opencryptobot.constants as con

from argparse import ArgumentParser
from opencryptobot.database import Database
from opencryptobot.telegrambot import TelegramBot
from opencryptobot.config import ConfigManager as Cfg
from logging.handlers import TimedRotatingFileHandler


class OpenCryptoBot:

    def __init__(self):
        # Parse command line arguments
        self.args = self._parse_args()

        # Load config file
        Cfg(self.args.config)

        # Set up logging
        log_path = self.args.logfile
        log_level = self.args.loglevel
        self._init_logger(log_path, log_level)

        # Create database
        db_path = self.args.database
        self.db = Database(db_path)

        # Create bot
        bot_token = self._get_bot_token()
        self.tg = TelegramBot(bot_token, self.db)

    # Parse arguments
    def _parse_args(self):
        desc = "Telegram bot for crypto currency info"
        parser = ArgumentParser(description=desc)

        # Config file path
        parser.add_argument(
            "-cfg",
            dest="config",
            help="path to conf file",
            default=os.path.join(con.CFG_DIR, con.CFG_FILE),
            required=False,
            metavar="FILE")

        # Save logfile
        parser.add_argument(
            "-log",
            dest="logfile",
            help="path to log file",
            default=os.path.join(con.LOG_DIR, con.LOG_FILE),
            required=False,
            metavar="FILE")

        # Logging level
        parser.add_argument(
            "-lvl",
            dest="loglevel",
            help="logging level",
            type=int,
            default=20,
            required=False)

        # Module logging level
        parser.add_argument(
            "-mlvl",
            dest="mloglevel",
            help="module logging level",
            required=False)

        # Bot token
        parser.add_argument(
            "-tkn",
            dest="token",
            help="bot token",
            required=False)

        # Database path
        parser.add_argument(
            "-db",
            dest="database",
            help="path to database file",
            default=os.path.join(con.DAT_DIR, con.DAT_FILE),
            required=False,
            metavar="FILE")

        # Use webhook
        parser.add_argument(
            "--webhook",
            dest="webhook",
            help="use webhook",
            action="store_true",
            required=False)

        return parser.parse_args()

    # Configure logging
    def _init_logger(self, log_path, log_level):
        logger = logging.getLogger()
        logger.setLevel(log_level)

        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)

        if log_path:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            file_log = TimedRotatingFileHandler(log_path, when="midnight", interval=1)
            file_log.setFormatter(formatter)
            logger.addHandler(file_log)

        console_log = logging.StreamHandler()
        console_log.setFormatter(formatter)
        logger.addHandler(console_log)

        # Set log level for specified modules
        if self.args.mloglevel:
            for modlvl in self.args.mloglevel.split(","):
                module, loglvl = modlvl.split("=")
                logr = logging.getLogger(module)
                logr.setLevel(int(loglvl))

    # Read bot token from environment or file
    def _get_bot_token(self):
        # First check command line argument
        if self.args.token:
            return self.args.token

        # Then check environment variable
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token:
            logging.info("Using bot token from environment variable")
            return token

        # Finally check token file
        token_path = os.path.join(con.CFG_DIR, con.TKN_FILE)

        try:
            if os.path.isfile(token_path):
                with open(token_path, 'r') as file:
                    return json.load(file)["telegram"]
            else:
                exit(f"ERROR: No token file '{con.TKN_FILE}' found at '{token_path}'")
        except KeyError as e:
            cls_name = f"Class: {type(self).__name__}"
            logging.error(f"{repr(e)} - {cls_name}")
            exit("ERROR: Can't read bot token")

    def start(self):
        if self.args.webhook:
            logging.info("Starting bot in webhook mode")
            if self.tg.bot_start_webhook():
                logging.info("Webhook started successfully")
            else:
                logging.error("Failed to start webhook")
                return
        else:
            logging.info("Starting bot in polling mode")
            if self.tg.bot_start_polling():
                logging.info("Polling started successfully")
            else:
                logging.error("Failed to start polling")
                return

        self.tg.bot_idle()


if __name__ == '__main__':
    OpenCryptoBot().start()
