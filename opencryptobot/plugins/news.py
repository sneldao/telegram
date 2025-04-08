import os
import json
import logging
import opencryptobot.emoji as emo
import opencryptobot.constants as con
import opencryptobot.utils as utl

from datetime import datetime
from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.cryptopanic import CryptoPanic
from opencryptobot.plugin import OpenCryptoPlugin, Category


class News(OpenCryptoPlugin):

    _token = None

    filters = ["rising", "hot", "bullish", "bearish", "important", "saved", "lol"]

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)
        self._token = os.getenv("CRYPTOPANIC_API_TOKEN")
        if not self._token:
            logging.error("CRYPTOPANIC_API_TOKEN not found in environment variables")

    def get_cmds(self):
        return ["n", "news"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, update, context):
        args = context.args if context.args else []
        keywords = utl.get_kw(args)
        arg_list = utl.del_kw(args)

        symbol = str()
        filter = str()
        msg = str()

        cp = CryptoPanic(token=self._token)
        data = None

        if not args:
            if RateLimit.limit_reached(update):
                return

            # Send loading message
            loading_msg = update.message.reply_text(
                text=f"{emo.WAIT} Fetching latest crypto news...",
                parse_mode=ParseMode.MARKDOWN
            )

            try:
                data = cp.get_posts()
            except Exception as e:
                loading_msg.delete()
                return self.handle_error(e, update)

            msg = f"<b>Current news</b>\n\n"
        else:
            for arg in args:
                if arg.lower().startswith("filter="):
                    filter = arg[7:]
                else:
                    symbol = arg

            if len(args) > 2:
                update.message.reply_text(
                    text=f"{emo.ERROR} Only two arguments allowed",
                    parse_mode=ParseMode.MARKDOWN)
                return
            if len(args) == 2 and (not symbol or not filter):
                update.message.reply_text(
                    text=f"{emo.ERROR} Wrong arguments",
                    parse_mode=ParseMode.MARKDOWN)
                return
            if filter and filter.lower() not in self.filters:
                update.message.reply_text(
                    text=f"{emo.ERROR} Wrong filter. Choose from: "
                         f"{', '.join(self.filters)}",
                    parse_mode=ParseMode.MARKDOWN)
                return

            if RateLimit.limit_reached(update):
                return

            # Send loading message
            loading_text = f"{emo.WAIT} Fetching news"
            if symbol:
                loading_text += f" for *{symbol}*"
            if filter:
                loading_text += f" with filter '*{filter}*'"
            loading_text += "..."
            
            loading_msg = update.message.reply_text(
                text=loading_text,
                parse_mode=ParseMode.MARKDOWN
            )

            try:
                if symbol and filter:
                    data = cp.get_multiple_filters(symbol, filter)
                    msg = f"<b>News for {symbol} and filter '{filter}'</b>\n\n"
                elif symbol:
                    data = cp.get_currency_news(symbol)
                    msg = f"<b>News for {symbol}</b>\n\n"
                elif filter:
                    data = cp.get_filtered_news(filter)
                    msg = f"<b>News for filter '{filter}</b>'\n\n"
            except Exception as e:
                loading_msg.delete()
                return self.handle_error(e, update)

        if not data or not data["results"]:
            loading_msg.delete()
            update.message.reply_text(
                text=f"{emo.ERROR} Couldn't retrieve news",
                parse_mode=ParseMode.MARKDOWN)
            return

        for news in reversed(data["results"]):
            if news["kind"] == "news":
                published = news["published_at"]
                domain = news["domain"]
                title = news["title"]
                url = news["url"]

                t = datetime.fromisoformat(published.replace("Z", "+00:00"))
                month = f"0{t.month}" if len(str(t.month)) == 1 else t.month
                day = f"0{t.day}" if len(str(t.day)) == 1 else t.day
                hour = f"0{t.hour}" if len(str(t.hour)) == 1 else t.hour
                minute = f"0{t.minute}" if len(str(t.minute)) == 1 else t.minute

                msg += f'{t.year}-{month}-{day} {hour}:{minute} - {domain}\n' \
                       f'<a href="{url}">{title.strip()}</a>\n\n'

        # Delete loading message before sending news
        loading_msg.delete()
        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol> (filter=<filter>)`"

    def get_description(self):
        return "News about a coin"

    def get_category(self):
        return Category.NEWS
