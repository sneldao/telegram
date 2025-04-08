from typing import List, Optional, Dict, Any
import io
import os
import asyncio
import pandas as pd
import plotly.io as pio
import plotly.graph_objs as go
import opencryptobot.emoji as emo
import opencryptobot.utils as utl
import opencryptobot.constants as con

from io import BytesIO
from pandas import DataFrame
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from opencryptobot.ratelimit import RateLimit
from opencryptobot.api.apicache import APICache
from opencryptobot.api.coingecko import CoinGecko
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Chart(OpenCryptoPlugin):
    """Plugin for generating price and volume charts"""

    # Common cryptocurrency mappings
    COMMON_COINS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "USDC": "usd-coin",
        "DAI": "dai",
        "BNB": "binancecoin"
    }

    def __init__(self, telegram_bot):
        super().__init__(telegram_bot)
        self.cg_coin_id: Optional[str] = None
        self.cmc_coin_id: Optional[str] = None

    def get_cmds(self) -> List[str]:
        return ["c", "chart"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, update: Update, context: CallbackContext) -> Optional[str]:
        try:
            args = context.args if context.args else []
            keywords = utl.get_kw(args)
            arg_list = utl.del_kw(args)

            if not arg_list:
                msg = f"Usage:\n{self.get_usage()}"
                if keywords.get(Keyword.INLINE):
                    return msg
                update.message.reply_text(text=msg, parse_mode=ParseMode.MARKDOWN)
                return None

            # Default values
            time_frame = 3  # Days
            base_coin = "BTC"

            # Parse trading pair
            if "-" in arg_list[0]:
                pair = arg_list[0].split("-", 1)
                base_coin = pair[1].upper()
                coin = pair[0].upper()
            else:
                coin = arg_list[0].upper()

            # Use USD as base for BTC
            if coin == "BTC" and base_coin == "BTC":
                base_coin = "USD"

            # Validate trading pair
            if coin == base_coin:
                msg = f"{emo.ERROR} Can't compare *{coin}* to itself"
                if keywords.get(Keyword.INLINE):
                    return msg
                update.message.reply_text(text=msg, parse_mode=ParseMode.MARKDOWN)
                return None

            # Parse time frame
            if len(arg_list) > 1 and arg_list[1].isnumeric():
                time_frame = int(arg_list[1])
                if time_frame <= 0:
                    raise ValueError("Time frame must be positive")

            if RateLimit.limit_reached(update):
                return None

            # Send loading message
            loading_msg = update.message.reply_text(
                text=f"{emo.CHART} Generating chart for *{coin}*-*{base_coin}* ({time_frame}d)...",
                parse_mode=ParseMode.MARKDOWN
            )

            # Get coin IDs
            try:
                # Check common coins first
                self.cg_coin_id = self.COMMON_COINS.get(coin)
                
                if not self.cg_coin_id:
                    response = APICache.get_cg_coins_list()
                    for entry in response:
                        if entry["symbol"].upper() == coin:
                            self.cg_coin_id = entry["id"]
                            break

                if not self.cg_coin_id:
                    msg = f"{emo.ERROR} Can't retrieve data for *{coin}*"
                    if keywords.get(Keyword.INLINE):
                        return msg
                    self.send_msg(msg, update, keywords)
                    return None

                # Get market data
                cg = CoinGecko()
                cg.api_key = os.getenv("COINGECKO_API_KEY")
                market = cg.get_coin_market_chart_by_id(
                    self.cg_coin_id,
                    base_coin.lower(),
                    time_frame)

            except Exception as e:
                return self.handle_error(f"Failed to fetch market data: {str(e)}", update)

            try:
                # Create volume chart
                df_volume = DataFrame(market["total_volumes"], columns=["DateTime", "Volume"])
                df_volume["DateTime"] = pd.to_datetime(df_volume["DateTime"], unit="ms")
                volume = go.Scatter(
                    x=df_volume.get("DateTime"),
                    y=df_volume.get("Volume"),
                    name="Volume"
                )

                # Create price chart
                df_price = DataFrame(market["prices"], columns=["DateTime", "Price"])
                df_price["DateTime"] = pd.to_datetime(df_price["DateTime"], unit="ms")
                price = go.Scatter(
                    x=df_price.get("DateTime"),
                    y=df_price.get("Price"),
                    yaxis="y2",
                    name="Price",
                    line=dict(
                        color=("rgb(22, 96, 167)"),
                        width=2
                    )
                )

                # Configure chart layout
                margin_l = 140
                tickformat = "0.8f"

                max_value = df_price["Price"].max()
                if max_value > 0.9:
                    if max_value > 999:
                        margin_l = 110
                        tickformat = "0,.0f"
                    else:
                        margin_l = 115
                        tickformat = "0.2f"

                layout = go.Layout(
                    paper_bgcolor='rgb(233,233,233)',
                    plot_bgcolor='rgb(233,233,233)',
                    autosize=False,
                    width=800,
                    height=600,
                    margin=go.layout.Margin(
                        l=margin_l,
                        r=50,
                        b=85,
                        t=100,
                        pad=4
                    ),
                    yaxis=dict(
                        domain=[0, 0.20]
                    ),
                    yaxis2=dict(
                        title=dict(
                            text=base_coin,
                            font=dict(
                                size=18
                            )
                        ),
                        domain=[0.25, 1],
                        tickprefix="   ",
                        ticksuffix=f"  "
                    ),
                    title=dict(
                        text=coin,
                        font=dict(
                            size=26
                        )
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        xanchor="center",
                        y=1.05,
                        x=0.45
                    ),
                    shapes=[{
                        "type": "line",
                        "xref": "paper",
                        "yref": "y2",
                        "x0": 0,
                        "x1": 1,
                        "y0": market["prices"][len(market["prices"]) - 1][1],
                        "y1": market["prices"][len(market["prices"]) - 1][1],
                        "line": {
                            "color": "rgb(50, 171, 96)",
                            "width": 1,
                            "dash": "dot"
                        }
                    }]
                )

                # Create figure
                fig = go.Figure(data=[price, volume], layout=layout)
                fig["layout"]["yaxis2"].update(tickformat=tickformat)

                # Send chart
                loading_msg.delete()  # Delete loading message
                return self.send_chart(fig, update, keywords)

            except Exception as e:
                return self.handle_error(f"Failed to create chart: {str(e)}", update)

        except Exception as e:
            return self.handle_error(f"Unexpected error: {str(e)}", update)

    def send_chart(self, fig: go.Figure, update: Update, keywords: Dict[str, Any]) -> Optional[str]:
        """Send the generated chart to the user"""
        try:
            # Convert plot to image
            img_bytes = BytesIO()
            pio.write_image(fig, img_bytes, format="png")
            img_bytes.seek(0)

            if keywords.get(Keyword.INLINE):
                return None  # Charts not supported in inline mode

            # Send image
            self.send_photo(
                photo=img_bytes,
                update=update,
                keywords=keywords)

            return None

        except Exception as e:
            return self.handle_error(f"Failed to send chart: {str(e)}", update)

    def get_usage(self) -> str:
        return (
            f"`/{self.get_cmds()[0]} <symbol>(-<target symbol>) <timeframe>`\n"
            f"Example: `/{self.get_cmds()[0]} BTC-USD 7`"
        )

    def get_description(self) -> str:
        return "Chart with price and volume"

    def get_category(self) -> Category:
        return Category.CHARTS

    def inline_mode(self) -> bool:
        return False  # Charts not supported in inline mode

    def _get_cg_coin_id(self, coin):
        self.cg_coin_id = None

        try:
            response = APICache.get_cg_coins_list()
        except Exception:
            return

        for entry in response:
            if entry["symbol"].upper() == coin:
                self.cg_coin_id = entry["id"]
                return

    def _get_cmc_coin_id(self, coin):
        self.cmc_coin_id = None

        try:
            response = APICache.get_cmc_coin_list()
        except Exception:
            return

        for entry in response["data"]:
            if entry["symbol"].upper() == coin:
                self.cmc_coin_id = entry["id"]
                return
