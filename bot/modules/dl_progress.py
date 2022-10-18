import math
import os
import time

from pyrogram.errors import MessageNotModified
from pyrogram.errors.exceptions import FloodWait
from pyrogram.types import Message


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


class Progress:
    def __init__(self, mess: Message, filename, start):
        self.mess = mess
        self.file = filename
        self.start = start

    def dl_progress(self, current, total):
        percentage = current * 100 / total
        now = time.time()
        start = self.start
        message = self.mess
        name = self.file
        diff = now - start
        speed = current / diff
        elapsed = round(diff) * 1000
        eta = round((total - current) / speed) * 1000
        elapsed = TimeFormatter(elapsed)
        eta = TimeFormatter(eta)
        unfinished = "".join('◉' for i in range(math.floor(percentage / 5)))
        finished = "".join('◌' for i in range(20 - math.floor(percentage / 5)))
        progress = f"[{unfinished}{finished}]"
        if round(diff % 5.00) == 0 or current == total:
            try:
                message.edit(
                    f"**Downloading 📥️**\n\n**Name :** <code>{name}</code>\n\n{progress} {percentage : .2f}%\n\n**Done :** `{humanbytes(current)} of {humanbytes(total)}`\n**Speed :** `{humanbytes(speed)}`"
                    + f"\n**Elapsed :** `{elapsed}`\n**ETA :** `{eta}`")
            except FloodWait as fd:
                time.sleep(fd.value)
            except Exception as e:
                print(e)
        if percentage == 100:
            time.sleep(3)
            message.delete()

    def up_progress(self, current, total):
        percentage = current * 100 / total
        now = time.time()
        start = self.start
        message = self.mess
        name = os.path.basename(self.file)
        diff = now - start
        speed = current / diff
        elapsed = round(diff) * 1000
        eta = round((total - current) / speed) * 1000
        elapsed = TimeFormatter(elapsed)
        eta = TimeFormatter(eta)
        unfinished = "".join('◉' for i in range(math.floor(percentage / 5)))
        finished = "".join('◌' for i in range(20 - math.floor(percentage / 5)))
        progress = f"[{unfinished}{finished}]"
        if round(diff % 3.00) == 0 or current == total:
            try:
                message.edit(
                    f"**Uploading 📤️**\n\n**Name :** <code>{name}</code>\n\n{progress} {percentage : .2f}%\n\n**Done :** `{humanbytes(current)} of {humanbytes(total)}`\n**Speed :** `{humanbytes(speed)}/s`"
                    + f"\n**Elapsed :** `{elapsed}`\n**ETA :** `{eta}`")
            except MessageNotModified:
                time.sleep(3.0)
            except FloodWait as fd:
                time.sleep(fd.value)
        if percentage == 100:
            time.sleep(3)
            message.delete()
        return

    def mul_progress(self, current, total):
        percentage = current * 100 / total
        now = time.time()
        start = self.start
        message = self.mess
        name = os.path.basename(self.file)
        diff = now - start
        speed = current / diff
        elapsed = round(diff) * 1000
        eta = round((total - current) / speed) * 1000
        elapsed = TimeFormatter(elapsed)
        eta = TimeFormatter(eta)
        unfinished = "".join('◉' for i in range(math.floor(percentage / 5)))
        finished = "".join('◌' for i in range(20 - math.floor(percentage / 5)))
        progress = f"[{unfinished}{finished}]"
        if round(diff % 3.00) == 0 or current == total:
            try:
                message.edit(
                    f"**Uploading 📤️**\n\n**Name :** <code>{name}</code>\n\n{progress} {percentage : .2f}%\n\n**Done :** `{humanbytes(current)} of {humanbytes(total)}`\n**Speed :** `{humanbytes(speed)}/s`"
                    + f"\n**Elapsed :** `{elapsed}`\n**ETA :** `{eta}`")
            except MessageNotModified:
                time.sleep(3.0)
            except FloodWait as fd:
                time.sleep(fd.value)
        if percentage == 100:
            time.sleep(3)
            message.edit(f"Uploaded {name}✔")
        return


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
        + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2]