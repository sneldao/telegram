import logging
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword
from opencryptobot.ratelimit import RateLimit


class Help(OpenCryptoPlugin):

    def get_cmds(self):
        return ["h", "help"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, update, context):
        args = context.args if context.args else []
        keywords = utl.get_kw(args)
        arg_list = utl.del_kw(args)

        if not arg_list:
            if not keywords.get(Keyword.INLINE):
                msg = f"{emo.INFO} *Welcome to SNEL Bot!*\n\n"
                msg += "SNEL helps you learn about stablecoins and navigate Web3.\n\n"
                
                msg += "*📊 Price Information*\n"
                msg += "/price - Check cryptocurrency prices\n"
                msg += "/s - View price, market cap and volume\n"
                msg += "/v - Calculate value of a coin quantity\n\n"
                
                msg += "*📈 Charts & Analysis*\n"
                msg += "/c - View price and volume charts\n"
                msg += "/cs - See candlestick charts\n\n"
                
                msg += "*🧠 Learn About Web3*\n"
                msg += "/i - Get general coin information\n"
                msg += "/des - Read coin descriptions\n"
                msg += "/comp - Compare different coins\n"
                msg += "/top - See top cryptocurrencies\n\n"
                
                msg += "*📰 News & Updates*\n"
                msg += "/n - Get latest crypto news\n\n"
                
                msg += "*🤖 Bot Commands*\n"
                msg += "/about - Learn about SNEL\n"
                msg += "/help - Show this menu\n"
                msg += "/manual - Get help with specific commands\n"
                msg += "/feedback - Share your thoughts\n\n"

                msg += f"*Need help?* Just use /manual followed by any command to learn how it works."

                # Log debugging info
                logging.info(f"Plugins count: {len(self.tgb.plugins)}")
                for i, plugin in enumerate(self.tgb.plugins):
                    logging.info(f"Plugin {i}: {type(plugin).__name__}")

                self.send_msg(msg, update, keywords)
            return

        cmd = arg_list[0].lower()
        cmd = cmd[1:] if cmd.startswith("/") else cmd

        for plugin in self.tgb.plugins:
            try:
                plugin_cmds = plugin.get_cmds()
                if cmd in plugin_cmds:
                    msg = f"{emo.INFO} *{cmd.upper()}*\n\n"
                    msg += f"{plugin.get_description()}\n\n"
                    msg += f"*How to use:*\n{plugin.get_usage()}"

                    if keywords.get(Keyword.INLINE):
                        return msg

                    self.send_msg(msg, update, keywords)
                    return
            except Exception as e:
                logging.error(f"Error getting commands from plugin {type(plugin).__name__}: {e}")
                continue

        msg = f"{emo.ERROR} Command *{cmd}* not found"
        self.send_msg(msg, update, keywords)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]}` or `/{self.get_cmds()[0]} <command>`"

    def get_description(self):
        return "Show available commands"

    def get_category(self):
        return Category.BOT

    def inline_mode(self):
        return True
