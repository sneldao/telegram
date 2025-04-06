import opencryptobot.emoji as emo
import opencryptobot.utils as utl

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Manual(OpenCryptoPlugin):

    def get_cmds(self):
        return ["man", "manual"]

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

        msg = None
        cmd = arg_list[0].lower()
        cmd = cmd[1:] if cmd.startswith("/") else cmd

        for p in self.tgb.plugins:
            try:
                if cmd.lower() in p.get_cmds():
                    msg = p.get_usage() if p.get_usage() else None
                    break
            except Exception as e:
                continue

        if not msg:
            update.message.reply_text(
                text=f"{emo.INFO} No details for command `{cmd}` available",
                parse_mode=ParseMode.MARKDOWN)
            return

        if keywords.get(Keyword.INLINE):
            return msg

        self.send_msg(msg, update, keywords)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <command>`"

    def get_description(self):
        return "Show how to use a command"

    def get_category(self):
        return Category.BOT
        
    def inline_mode(self):
        return True
