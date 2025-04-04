import os
import json
import logging
import opencryptobot.constants as con

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import Any


class ConfigManager:

    _CFG_FILE = os.path.join(con.CFG_DIR, con.CFG_FILE)

    _cfg = dict()

    ignore = False

    def __init__(self, config_file=None):
        if config_file:
            ConfigManager._CFG_FILE = config_file

        ConfigManager._watch_changes()

    # Watch for config file changes
    @staticmethod
    def _watch_changes():
        observer = Observer()

        file = ConfigManager._CFG_FILE
        method = ConfigManager._read_cfg
        change_handler = ChangeHandler(file, method)

        observer.schedule(change_handler, ".", recursive=True)
        observer.start()

    @staticmethod
    def _read_cfg():
        if os.path.isfile(ConfigManager._CFG_FILE):
            with open(ConfigManager._CFG_FILE) as config_file:
                ConfigManager._cfg = json.load(config_file)
        else:
            cfg_file = ConfigManager._CFG_FILE
            exit(f"ERROR: No configuration file '{cfg_file}' found")

    @staticmethod
    def _write_cfg():
        if os.path.isfile(ConfigManager._CFG_FILE):
            with open(ConfigManager._CFG_FILE, "w") as config_file:
                json.dump(ConfigManager._cfg, config_file, indent=4)
        else:
            cfg_file = ConfigManager._CFG_FILE
            exit(f"ERROR: No configuration file '{cfg_file}' found")

    @staticmethod
    def _get_token():
        # First try environment variable
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        logging.debug(f"Token from env: {token}")
        if token:
            return token

        # Fallback to token file
        token_path = os.path.join(con.CFG_DIR, con.TKN_FILE)
        logging.debug(f"Looking for token file at: {token_path}")
        if os.path.isfile(token_path):
            with open(token_path, 'r') as file:
                return file.read().strip()
        return None

    @staticmethod
    def get(*args) -> Any:
        # Special case for bot token
        if args and args[0] == "bot_token":
            return ConfigManager._get_token()

        if not ConfigManager._cfg:
            ConfigManager._read_cfg()

        if not args:
            return ConfigManager._cfg

        value = ConfigManager._cfg
        for arg in args:
            value = value.get(arg, None)
            if value is None:
                return None
        return value

    @staticmethod
    def set(value, *keys):
        tmp_cfg = ConfigManager._cfg

        for key in keys[:-1]:
            tmp_cfg = tmp_cfg.setdefault(key, {})

        tmp_cfg[keys[-1]] = value

        ConfigManager.ignore = True
        ConfigManager._write_cfg()

    @staticmethod
    def remove(*keys):
        for key in keys:
            if key in ConfigManager._cfg:
                del ConfigManager._cfg[key]
                ConfigManager._write_cfg()


class ChangeHandler(FileSystemEventHandler):
    file = None
    method = None
    old = 0

    def __init__(self, file, method):
        type(self).file = file
        type(self).method = method

    @staticmethod
    def on_modified(event):
        cfg_path = os.path.join('.', con.CFG_DIR, con.CFG_FILE)

        if event.src_path == cfg_path:
            statbuf = os.stat(event.src_path)
            new = statbuf.st_mtime

            # Workaround for watchdog bug
            # https://github.com/gorakhargosh/watchdog/issues/93
            if (new - ChangeHandler.old) > 0.5:
                if ConfigManager.ignore:
                    ConfigManager.ignore = False
                else:
                    ChangeHandler.method()

            ChangeHandler.old = new
