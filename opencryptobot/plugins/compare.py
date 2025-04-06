import time
import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Compare(OpenCryptoPlugin):

    BASE_URL = "https://coinlib.io/compare/"

    def get_cmds(self):
        return ["comp", "compare"]

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

        if len(arg_list) == 1:
            msg = f"{emo.ERROR} Enter at least 2 coins to compare them"
            self.send_msg(msg, update, keywords)
            return

        if len(arg_list) > 8:
            msg = f"{emo.ERROR} Not possible to compare more then 8 coins"
            self.send_msg(msg, update, keywords)
            return

        y, m, d = time.strftime("%Y-%m-%d").split("-")

        if int(m) - 1 < 1:
            y = str(int(y) - 1)
            m = "12"
        else:
            m = str(int(m) - 1)
        if len(m) == 1:
            m = f"0{m}"
        if len(d) == 1:
            d = f"0{d}"

        url = f"{self.BASE_URL}{y}-{m}-{d}/"

        for symbol in arg_list:
            url += f"{symbol.upper()}/"

        title = f"Compare {' & '.join(arg_list).upper()}"
        msg = f"[{title}]({url})"

        if keywords.get(Keyword.INLINE):
            return msg

        self.send_msg(msg, update, keywords)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <symbol> <symbol> ...`"

    def get_description(self):
        return "Compare coins"

    def get_category(self):
        return Category.GENERAL
        
    def inline_mode(self):
        return True
