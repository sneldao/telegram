from typing import List, Optional, Dict, Any
import os
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Stats(OpenCryptoPlugin):
    """Plugin for showing detailed cryptocurrency statistics"""

    # Common cryptocurrency mappings
    COMMON_COINS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "USDC": "usd-coin",
        "DAI": "dai",
        "BNB": "binancecoin"
    }

    def get_cmds(self) -> List[str]:
        return ["s", "stats"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, update: Update, context: CallbackContext) -> Optional[str]:
        try:
            args = context.args if context.args else []
            keywords = utl.get_kw(args)
            arg_list = utl.del_kw(args)

            if not arg_list:
                if not keywords.get(Keyword.INLINE):
                    update.message.reply_text(
                        text=f"Usage:\n{self.get_usage()}",
                        parse_mode=ParseMode.MARKDOWN)
                return None

            if RateLimit.limit_reached(update):
                return None

            coin = arg_list[0].upper()
            
            # Check common coins first
            cgid = self.COMMON_COINS.get(coin)
            
            if not cgid:
                try:
                    response = APICache.get_cg_coins_list()
                    for entry in response:
                        if entry["symbol"].upper() == coin:
                            cgid = entry["id"]
                            break
                except Exception as e:
                    return self.handle_error(f"Failed to fetch coin list: {str(e)}", update)

            if not cgid:
                msg = f"{emo.ERROR} No data found for *{coin}*"
                if keywords.get(Keyword.INLINE):
                    return msg
                self.send_msg(msg, update, keywords)
                return None

            # Get detailed coin data
            try:
                cg = CoinGecko()
                cg.api_key = os.getenv("COINGECKO_API_KEY")
                data = cg.get_coin_by_id(cgid)
            except Exception as e:
                return self.handle_error(f"Failed to fetch coin data: {str(e)}", update)

            # Extract and format data
            name = data["name"]
            symbol = data["symbol"].upper()
            
            # Rankings
            rank_mc = data.get("market_cap_rank", "N/A")
            rank_cg = data.get("coingecko_rank", "N/A")

            # Supply info
            market_data = data.get("market_data", {})
            cs = int(float(market_data.get('circulating_supply', 0)))
            sup_c = f"{utl.format(cs)} {symbol}"
            
            ts = market_data.get("total_supply")
            sup_t = f"{utl.format(int(float(ts)))} {symbol}" if ts else "N/A"

            # Price data
            prices = market_data.get("current_price", {})
            usd = prices.get("usd", 0)
            eur = prices.get("eur", 0)
            btc = prices.get("btc", 0)
            eth = prices.get("eth", 0)

            p_usd = utl.format(usd, force_length=True)
            p_eur = utl.format(eur, force_length=True, template=p_usd)
            p_btc = utl.format(btc, force_length=True, template=p_usd)
            p_eth = utl.format(eth, force_length=True, template=p_usd)

            # Format price strings
            p_usd = "{:>12}".format(p_usd)
            p_eur = "{:>12}".format(p_eur)
            p_btc = "{:>12}".format(p_btc)
            p_eth = "{:>12}".format(p_eth)

            # Skip BTC/ETH prices if coin is BTC/ETH
            btc_str = "" if coin == "BTC" else f"BTC {p_btc}\n"
            eth_str = "" if coin == "ETH" else f"ETH {p_eth}\n"

            # Volume and market cap
            v_24h = utl.format(int(float(market_data.get("total_volume", {}).get("usd", 0))))
            m_cap = utl.format(int(float(market_data.get("market_cap", {}).get("usd", 0))))

            # Price changes
            changes = market_data.get("price_change_percentage_1h_in_currency", {})
            h1 = self._format_change(changes.get("usd"))
            
            changes = market_data.get("price_change_percentage_24h_in_currency", {})
            d1 = self._format_change(changes.get("usd"))
            
            changes = market_data.get("price_change_percentage_7d_in_currency", {})
            w1 = self._format_change(changes.get("usd"))
            
            changes = market_data.get("price_change_percentage_30d_in_currency", {})
            m1 = self._format_change(changes.get("usd"))
            
            changes = market_data.get("price_change_percentage_1y_in_currency", {})
            y1 = self._format_change(changes.get("usd"))

            # Build message
            msg = (
                f"`{name} ({symbol})\n\n"
                f"USD {p_usd}\n"
                f"EUR {p_eur}\n"
                f"{btc_str}"
                f"{eth_str}\n"
                f"Hour  {h1}\n"
                f"Day   {d1}\n"
                f"Week  {w1}\n"
                f"Month {m1}\n"
                f"Year  {y1}\n\n"
                f"Market Cap Rank: {rank_mc}\n"
                f"Coin Gecko Rank: {rank_cg}\n\n"
                f"Volume 24h: {v_24h} USD\n"
                f"Market Cap: {m_cap} USD\n"
                f"Circ. Supp: {sup_c}\n"
                f"Total Supp: {sup_t}\n\n"
                f"`"
                f"Stats on [CoinGecko](https://www.coingecko.com/en/coins/{cgid}) & "
                f"[Coinlib](https://coinlib.io/coin/{coin}/{coin})"
            )

            if keywords.get(Keyword.INLINE):
                return msg

            self.send_msg(msg, update, keywords)
            return None

        except Exception as e:
            return self.handle_error(f"Unexpected error: {str(e)}", update)

    def _format_change(self, value: Optional[float]) -> str:
        """Format price change percentage"""
        if value is not None:
            change = utl.format(float(value), decimals=2, force_length=True)
            return "{:>10}".format(f"{change}%")
        return "{:>10}".format("N/A")

    def get_usage(self) -> str:
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self) -> str:
        return "Price, market cap and volume"

    def get_category(self) -> Category:
        return Category.PRICE

    def inline_mode(self) -> bool:
        return True
