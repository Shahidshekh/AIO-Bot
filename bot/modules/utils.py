import asyncio
import os
from .logger import LOGGER
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import MessageNotModified, MessageIdInvalid


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
        command = f"7z x -o\"{output_dir}\" \"{av_path}\" -y"
        final = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        sha, hid = await final.communicate()
        if sha:
            LOGGER.info("Extracted!")


async def files_keyboard(directory, message):
    while True:
        try:
            content = os.listdir(directory)
            contents = sorted(content)
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
            await message.edit("Select and Rename files you want -", reply_markup=files)
        except MessageNotModified:
            await asyncio.sleep(1)
        except MessageIdInvalid:
            return
