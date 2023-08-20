import requests
from pyrogram.errors import FloodWait
from bot.modules.logger import LOGGER
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from bot.database.db_client import get_up_mode
from bot.modules.dl_progress import Progress
from PIL import Image
from pathlib import Path
from hurry.filesize import size
import asyncio
import os
import time
import re
import subprocess


async def upload_video(message, local_file_name, user_id, yt_thumb=None, thumb=None, mul=False):
    st = time.time()
    prog = Progress(message, local_file_name, st)
    progress = prog.mul_progress if mul else prog.up_progress
    mode = await get_up_mode(user_id)
    LOGGER.info(user_id)
    if mode:
        await upload(
            local_file_name=local_file_name,
            message=message,
            thumbnail=thumb,
            progress=progress
        )
        return

    stats = os.stat(local_file_name)
    size = stats.st_size / (1024 * 1024)
    if size > 1950.00:
        await message.edit(f"Can't Upload :( Due to Telegram Limitation\n\n**Size :** {round(size, 2)}MiB")
        return
    caption_str = f"`{os.path.basename(local_file_name)}`"
    thumb = None
    if local_file_name.upper().endswith(
            ("MKV", "MP4", "WEBM", "FLV", "3GP", "AVI", "MOV", "OGG", "WMV", "M4V", "TS", "MPG", "MTS", "M2TS")):
        duration = 0
        try:
            metadata = extractMetadata(createParser(local_file_name))
            if metadata.has("duration"):
                duration = metadata.get("duration").seconds
        except Exception as g_e:
            LOGGER.info(g_e)
        width = 0
        height = 0
        thumb_image_path = None
        if not yt_thumb:
            LOGGER.info("Taking Screenshot..")
            thumb_image_path = await take_screen_shot(
                local_file_name,
                os.path.dirname(os.path.abspath(local_file_name)),
                (duration / 2),
            )

        else:
            req = requests.get(yt_thumb)
            thumb_image_path = os.path.join(
                os.path.dirname(os.path.abspath(local_file_name)),
                str(time.time()) + ".jpg",
            )
            with open(thumb_image_path, "wb") as thum:
                thum.write(req.content)
            img = Image.open(thumb_image_path).convert("RGB")
            img.save(thumb_image_path, format="jpeg")
        # get the correct width, height, and duration for videos greater than 10MB
        if os.path.exists(thumb_image_path):
            metadata = extractMetadata(createParser(thumb_image_path))
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
            # ref: https://t.me/PyrogramChat/44663
            # https://stackoverflow.com/a/21669827/4723940
            Image.open(thumb_image_path).convert("RGB").save(
                thumb_image_path
            )
            img = Image.open(thumb_image_path)
            # https://stackoverflow.com/a/37631799/4723940
            img.resize((320, height))
            img.save(thumb_image_path, "JPEG")
        if thumb_image_path is not None and os.path.isfile(thumb_image_path):
            thumb = thumb_image_path

        sent_message = await message.reply_video(
            video=local_file_name,
            caption=caption_str,
            duration=duration,
            width=width,
            height=height,
            thumb=thumb,
            supports_streaming=True,
            disable_notification=True,
            progress=progress
        )
    else:
        await upload(
            local_file_name=local_file_name,
            message=message,
            thumbnail=thumb,
            progress=progress
        )


async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = os.path.join(output_directory, str(time.time()) + ".jpg")
    if video_file.upper().endswith(
            ("MKV", "MP4", "WEBM", "AVI", "MOV", "OGG", "WMV", "M4V", "TS", "MPG", "MTS", "M2TS", "3GP")):
        file_genertor_command = [
            "ffmpeg",
            "-ss",
            str(ttl),
            "-i",
            video_file,
            "-vframes",
            "1",
            out_put_file_name,
        ]
        # width = "90"
        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            # stdout must a pipe to be accessible as process.stdout
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        # Wait for the subprocess to finish
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
    #
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None


async def upload(local_file_name, message, thumbnail, progress):
    file_name = os.path.basename(local_file_name)
    LOGGER.info(f"uploading : {file_name}")
    LOGGER.info(f"path is : {local_file_name}")
    stats = os.stat(local_file_name)
    size = stats.st_size / (1024 * 1024)
    if size < 1950.00:
        try:
            total = await message.reply_document(
                document=local_file_name,
                thumb=thumbnail,
                caption=f"<code>{file_name}</code>",
                disable_notification=True,
                progress=progress
            )


        except Exception as e:
            LOGGER.error(e)
        except FloodWait as fd:
            await asyncio.sleep(fd.value)
        return
    else:
        await message.edit(f"Can't Upload :( Due to Telegram Limitation\n\n**Size :** {round(size, 2)}MiB")
        return


async def upload_to_gdrive(file_upload, message, g_id):
    await asyncio.sleep(3)
    del_it = await message.edit_text(
        f"<a href='tg://user?id={g_id}'>🔊</a> Now Uploading to ☁️ Cloud!!!"
    )
   # if not os.path.exists("rclone.conf"):
    #    with open("rclone.conf", "w+", newline="\n", encoding="utf-8") as fole:
   #         fole.write(f"{RCLONE_CONFIG}")
    if os.path.exists("rclone.conf"):
        with open("rclone.conf", "r+") as file:
            con = file.read()
            gUP = "Gdrive"
            LOGGER.info(gUP)
    destination = "AIO-Bot"
    file_upload = str(Path(file_upload).resolve())
    LOGGER.info(file_upload)
    if os.path.isfile(file_upload):
        g_au = [
            "rclone",
            "copy",
            "--config=rclone.conf",
            f"{file_upload}",
            f"{gUP}:{destination}",
            "-v",
        ]
        LOGGER.info(g_au)
        tmp = await asyncio.create_subprocess_exec(
            *g_au, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        pro, cess = await tmp.communicate()
        LOGGER.info(pro.decode())
        LOGGER.info(cess.decode())
        gk_file = re.escape(os.path.basename(file_upload))
        LOGGER.info(gk_file)
        with open("filter.txt", "w+", encoding="utf-8") as filter:
            print(f"+ {gk_file}\n- *", file=filter)

        t_a_m = [
            "rclone",
            "lsf",
            "--config=rclone.conf",
            "-F",
            "i",
            "--filter-from=filter.txt",
            "--files-only",
            f"{gUP}:{destination}",
        ]
        gau_tam = await asyncio.create_subprocess_exec(
            *t_a_m, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        # os.remove("filter.txt")
        gau, tam = await gau_tam.communicate()
        gautam = gau.decode().strip()
        LOGGER.info(gau.decode())
        LOGGER.info(tam.decode())
        # os.remove("filter.txt")
        gauti = f"https://drive.google.com/file/d/{gautam}/view?usp=drivesdk"
        gjay = size(os.path.getsize(file_upload))
        button = []
        button.append(
            [pyrogram.InlineKeyboardButton(text="☁️ CloudUrl ☁️", url=f"{gauti}")]
        )
        button_markup = pyrogram.InlineKeyboardMarkup(button)
        await asyncio.sleep(EDIT_SLEEP_TIME_OUT)
        await message.reply_text(
            f"🤖: Uploaded successfully `{os.path.basename(file_upload)}` <a href='tg://user?id={g_id}'>🤒</a>\n📀 Size: {gjay}",
            reply_markup=button_markup,
        )
        os.remove(file_upload)
        await del_it.delete()


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
