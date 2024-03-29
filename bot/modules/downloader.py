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
from shutil import rmtree
from bot import filenames
from pyrogram.errors import FloodWait
from bot.modules.uploader import upload_video
from threading import Thread


class Downloader:
    def __init__(self, client, message, custom_name):
        self.name = custom_name
        self.msg = message
        self.client = client
        self.st = time()
        self.user = message.from_user.id
        self.download_location = f"/usr/src/app/Download/{self.user}/"

    async def download_from_link(self, url):

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
                Thread(target=key_loop, args=([out_path, em])).start()
        else:
            await self.msg.reply_text("File Corrupted", quote=True)


def clean_all(dl_loc):
    LOGGER.info("Cleaning...")
    try:
        rmtree(dl_loc)
    except Exception as e:
        pass


async def compress(local_file, out, message, user):
    filename = os.path.basename(local_file)
    filenames.update({f"{user}" : f"{filename}"})
    cmd = f"ffmpeg -i '{local_file}' -preset slow -vcodec libx265 -crf 28 '{out}'"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Stats", callback_data=f"c |{user}")
            ]        
        ]
    )
    mess = await message.reply(
        f"**Compressing...**\n\n**Name** : `{filename}`", 
        reply_markup=reply_markup
        )
    
    proc = await asyncio.create_subprocess_shell(cmd, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    err = stderr.decode()
    u = stdout.decode()
    #LOGGER.info(u)
    #if err:
        #await mess.edit("**Error 🤷‍♂️**")
    await mess.edit(f"**Compressed Successfully!**")
    await upload_video(local_file_name=out,message=mess,thumb=None, user_id=user)


def humanbytes(size: int):
    if not size:
        return "N/A"
    power = 2 ** 10
    n = 0
    dic_powern = {0: " ", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {dic_powern[n]}B"


def key_loop(out, msg):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(files_keyboard(out, msg))
        loop.close()
