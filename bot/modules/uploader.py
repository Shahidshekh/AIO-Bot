from bot.modules.logger import LOGGER
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from bot.database.db_client import get_up_mode
from bot.modules.dl_progress import Progress
from PIL import Image
import asyncio
import os
import time

async def upload_video(message, local_file_name, user_id, yt_thumb = None, thumb = None, mul = False):
    st = time.time()
    prog = Progress(message, local_file_name, st)
    progress = prog.mul_progress if mul else prog.up_progress
    mode = await get_up_mode(user_id)
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
    if local_file_name.upper().endswith(("MKV", "MP4", "WEBM", "FLV", "3GP", "AVI", "MOV", "OGG", "WMV", "M4V", "TS", "MPG", "MTS", "M2TS")):
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


async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = os.path.join(output_directory, str(time.time()) + ".jpg")
    if video_file.upper().endswith(("MKV", "MP4", "WEBM", "AVI", "MOV", "OGG", "WMV", "M4V", "TS", "MPG", "MTS", "M2TS", "3GP")):
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
            clean_all(self.download_location)

        except Exception as e:
            LOGGER.error(e)
        except FloodWait as fd:
            await asyncio.sleep(fd.value)
        return
    else:
        await message.edit(f"Can't Upload :( Due to Telegram Limitation\n\n**Size :** {round(size, 2)}MiB")
        return


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
