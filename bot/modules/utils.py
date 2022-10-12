import asyncio
import os
from .logger import LOGGER
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import MessageNotModified, MessageIdInvalid, FloodWait


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


async def compress(local_file, out, message):
    filename = os.path.basename(local_file)
    cmd = f'ffmpeg -i "{local_file}" -preset ultrafast -c:v libx265 -crf 27 -map 0:v -c:a aac -map 0:a -c:s copy -map 0:s? "{out}" -y'
    mess = await message.edit("**Compressing...**")
    proc = asyncio.create_subprocess_shell(cmd, stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    err = stderr.decode()
    if err:
        await mess.edit("**Error 🤷‍♂️")