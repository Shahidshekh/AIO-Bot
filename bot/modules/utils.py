import asyncio
import os
from .logger import LOGGER
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import MessageNotModified, MessageIdInvalid, FloodWait
from subprocess import run as srun
from sys import executable
from os import execl
from bot.database.db_client import total_users


class Extract:
    def __init__(self) -> None:
        pass

    async def extract(self, av_path, output_dir, password: str = ""):
        # await self.check(ext_dir)
        if os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                LOGGER.info("created dirs")
            except:
                pass
        command = f"7z e -o\"{output_dir}\" \"{av_path}\" -y"
        final = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        sha, hid = await final.communicate()
        if sha:
            LOGGER.info("Extracted!")


async def files_keyboard(directory, message):
    fcontent = os.listdir(directory)
    fcontents = []
    for fi in content:
        if os.path.isfile(f"{directory}{fi}"):
            contents.append(fi)
    fcontents.sort()
    while True:
        try:
            content = os.listdir(directory)
            contents = []
            for fi in content:
                if os.path.isfile(f"{directory}{fi}"):
                    contents.append(fi)
            contents.sort()
            fi_butt = []
        except FileNotFoundError:
            return

        for i, file in enumerate(contents, 1):
            fi_butt.append(
                [
                    InlineKeyboardButton(text=file, callback_data=f"none{i: 02d}"),
                    InlineKeyboardButton(text="📝️ Rename", callback_data="rename {:02d}".format(i))
                ]
            )
        fi_butt.append([InlineKeyboardButton(text="Upload", callback_data="upload")])
        files = InlineKeyboardMarkup(fi_butt)
        try:
            if contents != fcontents:
                await message.edit("Select and Rename files you want -", reply_markup=files)
        except MessageNotModified:
            await asyncio.sleep(1)
        except MessageIdInvalid:
            return
        except FloodWait as fd:
            await asyncio.sleep(fd.value)

async def log(app, message):
    await message.reply_document(
        document="log.txt",
        thumb=None,
        caption="`logs`",
        disable_notification=False
    )


async def restart(app, message):
  msg = await message.reply("**Restarting.....**", quote=True)
  srun(["python3", "upstream.py"])
  with open("/usr/src/app/.restartmg", "w") as f:
    f.truncate(0)
    f.write(f"{msg.chat.id}\n{msg.id}\n")
  execl(executable, executable, "-m", "bot")

async def db_users_count(app, message):
    t = await total_users()
    await message.reply(f"**Total Users On DB are : {t}**", quote=True)