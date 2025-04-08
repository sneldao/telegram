from telegram import ParseMode
import opencryptobot.emoji as emo
import opencryptobot.utils as utl
from opencryptobot.config import ConfigManager as Cfg
from opencryptobot.plugin import OpenCryptoPlugin, Category, Keyword


class Feedback(OpenCryptoPlugin):

    def get_cmds(self):
        return ["feedback"]

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

        user = update.message.from_user
        if user.username:
            name = f"@{user.username}"
        else:
            name = user.first_name

        feedback = " ".join(arg_list)

        try:
            # Send feedback to all admins
            for admin in Cfg.get("admin_id"):
                context.bot.send_message(
                    chat_id=admin,
                    text=f"💬 Feedback from {name}:\n\n{feedback}",
                    parse_mode=ParseMode.MARKDOWN)

            update.message.reply_text(
                text=f"Thanks for your feedback! {emo.TOP}",
                parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            return self.handle_error(f"Failed to send feedback: {str(e)}", update)

    def get_usage(self):
        return f"`/{self.get_cmds()[0]} <your feedback>`"

    def get_description(self):
        return "Share your thoughts about the bot"

    def get_category(self):
        return Category.BOT
