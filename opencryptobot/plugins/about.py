import os
import opencryptobot.emoji as emo
import opencryptobot.constants as con

from telegram import ParseMode
from opencryptobot.plugin import OpenCryptoPlugin, Category


class About(OpenCryptoPlugin):

    ABOUT_FILENAME = "about.md"

    def get_cmds(self):
        return ["about"]

    @OpenCryptoPlugin.save_data
    @OpenCryptoPlugin.send_typing
    def get_action(self, update, context):
        about_file = os.path.join(con.RES_DIR, self.ABOUT_FILENAME)
        
        try:
            if not os.path.isfile(about_file):
                update.message.reply_text(
                    text=f"{emo.ERROR} About information not available",
                    parse_mode=ParseMode.MARKDOWN)
                return

            with open(about_file, "r", encoding="utf8") as file:
                content = file.readlines()

            if not content:
                update.message.reply_text(
                    text=f"{emo.ERROR} About information is empty",
                    parse_mode=ParseMode.MARKDOWN)
                return

            update.message.reply_text(
                text="".join(content),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True)

        except Exception as e:
            return self.handle_error(f"Failed to read about info: {str(e)}", update)

    def get_usage(self):
        return None

    def get_description(self):
        return "Information about bot"

    def get_category(self):
        return Category.BOT
