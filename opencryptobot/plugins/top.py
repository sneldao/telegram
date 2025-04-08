import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Top(OpenCryptoPlugin):

    def get_cmds(self):
        return ["top"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, update, context):
        args = context.args if context.args else []
        keywords = utl.get_kw(args)
        arg_list = utl.del_kw(args)

        base_cur = "USD"
        fiat_symbol = "$"

        if arg_list:
            base_cur = arg_list[0].upper()
            if base_cur == "EUR":
                fiat_symbol = "€"
            elif base_cur not in ["USD", "EUR", "BTC", "ETH"]:
                update.message.reply_text(
                    text=f"{emo.ERROR} Unsupported base currency. Use USD, EUR, BTC or ETH",
                    parse_mode=ParseMode.MARKDOWN)
                return

        if RateLimit.limit_reached(update):
            return

        # Send loading message
        loading_msg = update.message.reply_text(
            text=f"{emo.WAIT} Fetching top 30 cryptocurrencies in *{base_cur}*...",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            market = CoinGecko().get_coins_markets(
                    base_cur.lower(),
                    per_page=30,
                    page=1,
                    order="market_cap_desc",
                    sparkline=False,
                    price_change_percentage="24h")  # Added 24h price change
        except Exception as e:
            loading_msg.delete()
            return self.handle_error(e, update)

        msg = str()

        if market:
            for i in range(30):
                try:
                    rank = market[i]['market_cap_rank']
                    symbol = market[i]['symbol'].upper()
                    name = market[i]['name']

                    price = market[i]['current_price']
                    price = utl.format(price, decimals=4, symbol=base_cur)

                    # Get 24h price change
                    price_change = market[i].get('price_change_percentage_24h', 0)
                    change_emoji = "🔴" if price_change and price_change < 0 else "🟢"
                    price_change_str = f"{change_emoji} {abs(price_change):.1f}%" if price_change else ""

                    if base_cur == "EUR":
                        price = f"{price} {fiat_symbol}"
                        mcap = f"{utl.format(market[i]['market_cap'])}{fiat_symbol}"
                        vol = f"{utl.format(market[i]['total_volume'])}{fiat_symbol}"
                    elif base_cur == "USD":
                        price = f"{fiat_symbol}{price}"
                        mcap = f"{fiat_symbol}{utl.format(market[i]['market_cap'])}"
                        vol = f"{fiat_symbol}{utl.format(market[i]['total_volume'])}"
                    else:
                        price = f"{price} {base_cur}"
                        mcap = f"{utl.format(market[i]['market_cap'])} {base_cur}"
                        vol = f"{utl.format(market[i]['total_volume'])} {base_cur}"

                    msg += f"{rank}. *{symbol}* ({name}) - {price} {price_change_str}\n" \
                           f"` M.Cap.: {mcap}`\n" \
                           f"` Volume: {vol}`\n\n"
                except (KeyError, IndexError) as e:
                    continue  # Skip coins with missing data

        if msg:
            msg = f"*Top 30 Coins by Market Cap in {base_cur}*\n\n{msg}"
            msg += f"\nData provided by CoinGecko"
        else:
            msg = f"{emo.ERROR} Can't retrieve toplist"

        # Delete loading message before sending results
        loading_msg.delete()
        update.message.reply_text(
            text=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} (<target symbol>)`\n\nSupported base currencies: USD, EUR, BTC, ETH"

    def get_description(self):
        return "List top 30 coins"

    def get_category(self):
        return Category.GENERAL
