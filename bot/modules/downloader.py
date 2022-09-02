import asyncio
import os
from time import time
from bot.modules.utils import Extract
from bot.modules.dl_progress import Progress
from bot.modules.download_link import add_url, aria_start, progress_aria
from bot.modules.logger import LOGGER
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import CallbackQuery
from bot.modules.utils import files_keyboard


class Downloader:
    def __init__(self, client, message, custom_name):
        self.name = custom_name
        self.msg = message
        self.client = client
        self.st = time()
        self.user = message.from_user.id
        self.download_location = f"/usr/src/app/Download/{self.user}/"

    async def download_from_link(self):
        url = self.msg.reply_to_message.text
        if url.startswith("http"):
            msg = await self.msg.reply("**Checking...**", quote=True)
            await asyncio.sleep(2)
            aria_i = await aria_start()
            done, gid = add_url(aria_i, url, self.download_location)
            file = await progress_aria(aria_i, gid, msg, self.user)
            if file is None:
                await msg.delete()
                return False
            else:
                file_name = f"{self.download_location}{file}"
                return file_name

    async def download_from_file(self, app):
        mess = self.msg.reply_to_message
        if mess.media:
            message = await self.msg.reply("**Checking...**")
            file = [mess.document, mess.video, mess.audio]
            file_name = [fi for fi in file if fi is not None][0].file_name
            file_loc = f"{self.download_location}{file_name}"
            prog = Progress(message, file_name, self.st)
            file = await app.download_media(
                mess,
                file_loc,
                progress=prog.dl_progress
            )
            return file_loc

    async def extractit(self, file_path, out_path):
        if file_path.endswith('zip'):
            em = await self.msg.reply("Extracting...", quote=True)
            ext = Extract()
            await ext.extract(file_path, out_path)
            await em.edit("Extracted!")
            LOGGER.info(f"file name : {self.name}")
            await em.edit("**Waiting...**")
            butt = [
                [
                    InlineKeyboardButton("Yes", callback_data="yeah"),
                    InlineKeyboardButton("No", callback_data="hellno")
                ]

            ]
            name_but = InlineKeyboardMarkup(butt)
            if self.name != "":
                await em.edit("Found Custom Name! Wanna Use It?", reply_markup=name_but)
                await asyncio.sleep(10)
            else:
                await files_keyboard(out_path, em)
        else:
            await self.msg.reply_text("File Corrupted", quote=True)

    def upload(self, local_file_name, message, progress):
        file_name = os.path.basename(local_file_name)
        stats = os.stat(local_file_name)
        size = stats.st_size / (1024 * 1024)
        if size < 1950.00:
            try:
                total = message.reply_document(
                    document=local_file_name,
                    thumb=None,
                    caption=f"<code>{file_name}</code>",
                    disable_notification=True,
                    progress=progress
                )
                clean_all(self.download_location)

            except Exception as e:
                LOGGER.error(e)
            return
        else:
            message.edit(f"Can't Upload :( Due to Telegram Limitation\n\n**Size :** {round(size, 2)}MiB")
            return

def clean_all(dl_loc):
    LOGGER.info("Cleaning...")
    try:
        rmtree(dl_loc)
    except Exception as e:
        pass
