import inspect
import logging
import opencryptobot.emoji as emo
import opencryptobot.utils as utl
import os

from telegram.ext import CommandHandler
from telegram import ChatAction, ParseMode
from opencryptobot.config import ConfigManager as Cfg


class PluginInterface:

    # List of command strings that trigger the plugin
    def get_cmds(self):
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    # Logic that gets executed if command is triggered
    def get_action(self, update, context):
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"Interface method '{method}' not implemented")

    # How to use the command
    def get_usage(self):
        return None

    # Short description what the command does
    def get_description(self):
        return None

    # Category for command
    def get_category(self):
        return None

    # Does this command support inline mode
    def inline_mode(self):
        return False

    # Execute logic after the plugin is loaded
    def after_plugin_loaded(self):
        return None

    # Execute logic after all plugins are loaded
    def after_plugins_loaded(self):
        return None


class OpenCryptoPlugin(PluginInterface):

    def __init__(self, telegram_bot):
        super().__init__()

        self.tgb = telegram_bot
        self.add_plugin()

    @classmethod
    def send_typing(cls, func):
        def _send_typing_action(self, update, context):
            if update.message:
                user_id = update.message.chat_id
            elif update.callback_query:
                user_id = update.callback_query.message.chat_id
            else:
                return func(self, update, context)

            try:
                context.bot.send_chat_action(
                    chat_id=user_id,
                    action=ChatAction.TYPING)
            except Exception as ex:
                logging.error(f"{ex} - {update}")

            return func(self, update, context)
        return _send_typing_action

    @classmethod
    def only_owner(cls, func):
        def _only_owner(self, update, context):
            if update.effective_user.id in Cfg.get("admin_id"):
                return func(self, update, context)

        return _only_owner

    @classmethod
    def save_data(cls, func):
        def _save_data(self, update, context):
            if Cfg.get("database", "use_db"):
                if update.message:
                    usr = update.message.from_user
                    cmd = update.message.text
                    cht = update.message.chat
                elif update.inline_query:
                    usr = update.effective_user
                    cmd = update.inline_query.query[:-1]
                    cht = update.effective_chat
                else:
                    logging.warning(f"Can't save usage - {update}")
                    return func(self, update, context)

                if usr.id in Cfg.get("admin_id"):
                    return func(self, update, context)

                sql = self.get_sql("save_usage")
                self.tgb.db.execute_sql(sql, (usr.id, usr.username, usr.first_name,
                                            usr.last_name, usr.language_code, cmd,
                                            cht.id, cht.type, cht.title))

            return func(self, update, context)
        return _save_data

    def add_plugin(self):
        for cmd in self.get_cmds():
            self.tgb.dispatcher.add_handler(
                CommandHandler(
                    cmd,
                    self.get_action))

    def remove_plugin(self):
        for cmd in self.get_cmds():
            self.tgb.dispatcher.remove_handler(
                CommandHandler(
                    cmd,
                    self.get_action))

    def send_msg(self, msg, update, keywords):
        if not keywords:
            keywords = dict()

        notify = keywords.get(Keyword.NOTIFY, True)
        preview = keywords.get(Keyword.PREVIEW, True)
        quote = keywords.get(Keyword.QUOTE, True)
        parse = keywords.get(Keyword.PARSE, ParseMode.MARKDOWN)

        if update.message:
            update.message.reply_text(
                text=msg,
                parse_mode=parse,
                disable_web_page_preview=not preview,
                quote=quote)
        elif update.callback_query:
            update.callback_query.message.reply_text(
                text=msg,
                parse_mode=parse,
                disable_web_page_preview=not preview)

    def send_photo(self, photo, update, keywords):
        if not keywords:
            keywords = dict()

        notify = keywords.get(Keyword.NOTIFY, True)
        preview = keywords.get(Keyword.PREVIEW, True)
        quote = keywords.get(Keyword.QUOTE, True)
        parse = keywords.get(Keyword.PARSE, ParseMode.MARKDOWN)

        if update.message:
            update.message.reply_photo(
                photo=photo,
                parse_mode=parse,
                disable_notification=not notify,
                quote=quote)
        elif update.callback_query:
            update.callback_query.message.reply_photo(
                photo=photo,
                parse_mode=parse,
                disable_notification=not notify)

    def handle_error(self, error, update, send_error=True):
        logging.error(f"{error} - {update}")

        if send_error:
            msg = f"{emo.ERROR} {error}"
            self.send_msg(msg, update, None)

    @classmethod
    def build_menu(cls, buttons, n_cols=1, header_buttons=None, footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu

    def get_sql(self, filename):
        sql_file = os.path.join(con.SQL_DIR, f"{filename}.sql")
        with open(sql_file, "r", encoding="utf8") as file:
            return file.read()


class Keyword:

    NOTIFY = "notify"
    PREVIEW = "preview"
    QUOTE = "quote"
    PARSE = "parse"
    INLINE = "inline"


class Category:

    CHARTS = "Charts"
    PRICE = "Price"
    GENERAL = "General"
    NEWS = "News & Events"
    UTILS = "Utilities"
    FUN = "Fun"
    BOT = "Bot"

    @classmethod
    def get_categories(cls):
        return [cls.CHARTS, cls.PRICE, cls.GENERAL,
                cls.NEWS, cls.UTILS, cls.FUN, cls.BOT]
