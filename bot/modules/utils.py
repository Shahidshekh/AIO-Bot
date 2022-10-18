import asyncio
import os
from .logger import LOGGER
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import MessageNotModified, MessageIdInvalid, FloodWait
from subprocess import run as srun
from sys import executable
from os import execl
from bot.database.db_client import total_users, up_mode, get_up_mode


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
    for fi in fcontent:
        if os.path.isfile(f"{directory}{fi}"):
            fcontents.append(fi)
    fcontents.sort()
    count = 0
    while True:
        count+=1
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
        except Exception as e:
            LOGGER.info(e)

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
            if contents != fcontents or count==1:
                await message.edit("Select and Rename files you want -", reply_markup=files)
        except MessageNotModified:
            await asyncio.sleep(1)
        except MessageIdInvalid:
            return
        except FloodWait as fd:
            await asyncio.sleep(fd.value)
        except Exception as e:
            LOGGER.error(e)

async def log(app, message):
    await message.reply_document(
        document="log.txt",
        thumb=None,
        caption="`logs`",
        disable_notification=False
    )


async def restart(app, message):
    if message.from_user.id != 1485677797:
        await message.reply("Only My Owner Can Use It 😉", quote=True)
        return
    msg = await message.reply("**Restarting.....**", quote=True)
    srun(["python3", "upstream.py"])
    with open("/usr/src/app/.restartmg", "w") as f:
        f.truncate(0)
        f.write(f"{msg.chat.id}\n{msg.id}\n")
    execl(executable, executable, "-m", "bot")

async def db_users_count(app, message):
    if message.from_user.id != 1485677797:
        await message.reply("Only My Owner Can Use It 😉", quote=True)
        return
    t = await total_users()
    await message.reply(f"**Total Users On DB are : {t}**", quote=True)

async def settings(app, message):
    user_id = message.from_user.id
    mode = await get_up_mode(user_id)
    msgt = "**Upload Mode Set To** : `{0}`".format("Document" if mode else "Streamable")
    text = "{0}".format("Document" if not mode else "Streamable")
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=f"{text}", callback_data="mode")]])
    await message.reply(f"{msgt}", quote=True, reply_markup=reply_markup)