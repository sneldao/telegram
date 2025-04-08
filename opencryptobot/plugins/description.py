import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Description(OpenCryptoPlugin):

    def get_cmds(self):
        return ["des", "description"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, update, context):
        args = context.args if context.args else []
        keywords = utl.get_kw(args)
        arg_list = utl.del_kw(args)

        if not arg_list:
            update.message.reply_text(
                text=f"Usage:\n{self.get_usage()}",
                parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        coin = arg_list[0].upper()

        # Send loading message
        loading_msg = update.message.reply_text(
            text=f"{emo.WAIT} Fetching description for *{coin}*...",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            # First try common coins mapping
            common_coins = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                "USDT": "tether",
                "USDC": "usd-coin",
                "DAI": "dai",
                "BNB": "binancecoin"
            }
            
            coin_id = common_coins.get(coin)
            
            if not coin_id:
                # If not a common coin, search in full list
                response = APICache.get_cg_coins_list()
                for entry in response:
                    if entry["symbol"].lower() == coin.lower():
                        coin_id = entry["id"]
                        break

            if not coin_id:
                loading_msg.delete()
                update.message.reply_text(
                    text=f"{emo.INFO} No data found for *{coin}*",
                    parse_mode=ParseMode.MARKDOWN)
                return

            # Get coin details
            data = CoinGecko().get_coin_by_id(coin_id)

            if not data or not data.get("description", {}).get("en"):
                loading_msg.delete()
                update.message.reply_text(
                    text=f"{emo.INFO} No description available for *{coin}*",
                    parse_mode=ParseMode.MARKDOWN)
                return

            coin_desc = data["description"]["en"]
            
            # Add coin name and links if available
            header = f"*{data['name']} ({coin})*\n\n"
            
            # Delete loading message before sending description
            loading_msg.delete()

            # Send description in chunks if needed
            first_message = True
            for message in utl.split_msg(coin_desc):
                if first_message:
                    message = header + message
                    first_message = False
                
                update.message.reply_text(
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True)

        except Exception as e:
            loading_msg.delete()
            return self.handle_error(e, update)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "Coin description"

    def get_category(self):
        return Category.GENERAL
