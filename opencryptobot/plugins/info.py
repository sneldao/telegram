import threading
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.tokenstats import TokenStats
from opencryptobot.api.cryptocompare import CryptoCompare
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Info(OpenCryptoPlugin):

    LOGO_URL_PARTIAL = "https://www.cryptocompare.com"
    TOKEN = "Token"
    COIN = "Coin"

    # Common cryptocurrency mappings
    COMMON_COINS = {
        "BTC": "BTC",
        "ETH": "ETH",
        "USDT": "USDT",
        "USDC": "USDC",
        "DAI": "DAI",
        "BNB": "BNB"
    }

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)
        self.coin_type = None
        self.based_on = None

    def get_cmds(self):
        return ["i", "info"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, update, context):
        args = context.args if context.args else []
        keywords = utl.get_kw(args)
        arg_list = utl.del_kw(args)

        if not arg_list:
            if not keywords.get(Keyword.INLINE):
                update.message.reply_text(
                    text=f"Usage:\n{self.get_usage()}",
                    parse_mode=ParseMode.MARKDOWN)
            return

        if RateLimit.limit_reached(update):
            return

        coin = arg_list[0].upper()
        
        # Check common coins mapping
        if coin in self.COMMON_COINS:
            coin = self.COMMON_COINS[coin]

        try:
            # Reset class variables for new request
            self.coin_type = None
            self.based_on = None
            
            type_thread = threading.Thread(target=self._get_coin_type, args=[coin])
            type_thread.start()

            coin_info = CryptoCompare().get_coin_general_info(coin, "USD")
        except Exception as e:
            return self.handle_error(e, update)

        if coin_info["Message"] != "Success" or not coin_info["Data"]:
            msg = f"{emo.ERROR} No data for *{coin}*"
            self.send_msg(msg, update, keywords)
            return

        name = coin_info["Data"][0]["CoinInfo"]["FullName"]
        image = f"{self.LOGO_URL_PARTIAL}{coin_info['Data'][0]['CoinInfo']['ImageUrl']}"
        algo = coin_info["Data"][0]["CoinInfo"]["Algorithm"]
        proof = coin_info["Data"][0]["CoinInfo"]["ProofType"]
        h_per_s = coin_info["Data"][0]["CoinInfo"]["NetHashesPerSecond"]
        block = coin_info["Data"][0]["CoinInfo"]["BlockNumber"]
        block_time = coin_info["Data"][0]["CoinInfo"]["BlockTime"]
        block_reward = coin_info["Data"][0]["CoinInfo"]["BlockReward"]

        type_thread.join()

        if self.coin_type:
            type = f"{self.coin_type}"

            if self.based_on:
                type += f" ({self.based_on})"
        else:
            type = str("-")

        if self.coin_type == self.TOKEN:
            msg = f"`" \
                  f"Name:         {name}\n" \
                  f"Ticker:       {coin}\n" \
                  f"Type:         {type}\n" \
                  f"`"
        else:
            msg = f"`" \
                  f"Name:         {name}\n" \
                  f"Ticker:       {coin}\n" \
                  f"Type:         {type}\n" \
                  f"Algorithm:    {algo}\n" \
                  f"Proof type:   {proof}\n" \
                  f"Hashes (sec): {utl.format(int(h_per_s))}\n" \
                  f"Block:        {block}\n" \
                  f"Block time:   {block_time} seconds\n" \
                  f"Block reward: {block_reward}" \
                  f"`"

        if keywords.get(Keyword.INLINE):
            return f"[{name}]({image})\n\n{msg}"

        update.message.reply_photo(
            photo=image,
            caption=msg,
            parse_mode=ParseMode.MARKDOWN)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol>`"

    def get_description(self):
        return "General coin information"

    def get_category(self):
        return Category.GENERAL
        
    def inline_mode(self):
        return True

    def _get_coin_type(self, coin):
        res = TokenStats().get_roi_for_symbol(coin)
        if res:
            if res["type"]:
                if res["type"] == "coin":
                    self.coin_type = self.COIN
                    self.based_on = None
                elif res["type"] == "none":
                    self.coin_type = self.TOKEN
                    self.based_on = None
                else:
                    self.coin_type = self.TOKEN
                    self.based_on = res["type"].capitalize()
