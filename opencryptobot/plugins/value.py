from typing import List, Optional, Dict
import os
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from decimal import Decimal
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Value(OpenCryptoPlugin):
    """Plugin for calculating the value of a cryptocurrency quantity"""

    # Common cryptocurrency mappings
    COMMON_COINS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "USDC": "usd-coin",
        "DAI": "dai",
        "BNB": "binancecoin"
    }

    DEFAULT_VS_CURRENCIES = "btc,eth,usd,eur"

    def get_cmds(self) -> List[str]:
        return ["v", "value"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, update: Update, context: CallbackContext) -> Optional[str]:
        try:
            args = context.args if context.args else []
            keywords = utl.get_kw(args)
            
            if not args:
                msg = f"Usage:\n{self.get_usage()}"
                if keywords.get(Keyword.INLINE):
                    return msg
                update.message.reply_text(text=msg, parse_mode=ParseMode.MARKDOWN)
                return None

            # Parse coin and target currencies
            vs_cur = self.DEFAULT_VS_CURRENCIES
            if "-" in args[0]:
                pair = args[0].split("-", 1)
                vs_cur = pair[1].lower()
                coin = pair[0].upper()
            else:
                coin = args[0].upper()

            # Validate quantity
            if len(args) > 1 and utl.is_number(args[1]):
                qty = args[1]
            else:
                msg = f"Usage:\n{self.get_usage()}"
                if keywords.get(Keyword.INLINE):
                    return msg
                update.message.reply_text(text=msg, parse_mode=ParseMode.MARKDOWN)
                return None

            if RateLimit.limit_reached(update):
                return None

            # Get coin data
            try:
                # Check common coins first
                coin_id = self.COMMON_COINS.get(coin)
                
                if not coin_id:
                    response = APICache.get_cg_coins_list()
                    for entry in response:
                        if entry["symbol"].upper() == coin:
                            coin_id = entry["id"]
                            break
                
                if not coin_id:
                    msg = f"{emo.ERROR} Couldn't find cryptocurrency *{coin}*"
                    if keywords.get(Keyword.INLINE):
                        return msg
                    self.send_msg(msg, update, keywords)
                    return None

                # Get price data
                cg = CoinGecko()
                cg.api_key = os.getenv("COINGECKO_API_KEY")
                data = cg.get_coin_by_id(coin_id)
                prices = data["market_data"]["current_price"]

            except Exception as e:
                return self.handle_error(f"Failed to fetch data: {str(e)}", update)

            # Parse quantity
            try:
                qty_decimal = Decimal(str(qty))
                if qty_decimal <= 0:
                    raise ValueError("Quantity must be positive")
            except Exception as e:
                msg = f"{emo.ERROR} Quantity '{qty}' not valid"
                if keywords.get(Keyword.INLINE):
                    return msg
                self.send_msg(msg, update, keywords)
                return None

            # Calculate values
            msg_lines = []
            for currency in vs_cur.split(","):
                if currency in prices:
                    price = Decimal(str(prices[currency]))
                    value = price * qty_decimal
                    formatted_value = utl.format(float(value))
                    msg_lines.append(f"`{currency.upper()}: {formatted_value}`")

            if msg_lines:
                msg = f"`Value of {qty} {coin}`\n\n" + "\n".join(msg_lines)
            else:
                msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"

            if keywords.get(Keyword.INLINE):
                return msg

            self.send_msg(msg, update, keywords)
            return None

        except Exception as e:
            return self.handle_error(f"Unexpected error: {str(e)}", update)

    def get_usage(self) -> str:
        return f"`/{self.get_cmds()[0]} <symbol>(-<target symbol>,[...]) <quantity>`"

    def get_description(self) -> str:
        return "Value of coin quantity"

    def get_category(self) -> Category:
        return Category.PRICE

    def inline_mode(self) -> bool:
        return True
