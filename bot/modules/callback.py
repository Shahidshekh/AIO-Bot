from pyrogram.types import CallbackQuery
from bot.modules.logger import LOGGER
from bot.utils.client import app
from bot.modules.dl_progress import Progress
from time import time
from shutil import rmtree
import os
from pyromod import listen
from bot.modules.download_link import aria_start
from bot.modules.utils import files_keyboard
from pyrogram.errors import FloodWait
import asyncio
from bot.utils.ytdl import Youtube_dl
from bot import ytdlurls
from re import split as re_split
import asyncio
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
custom_name = ""
 

@app.on_callback_query()
async def cb(app, update: CallbackQuery):
    cb_data = update.data
    message = update.message
    user_id = update.from_user.id
    directory = f"/usr/src/app/extracted/{user_id}/"
    dl_directory = f"/usr/src/app/Download/{user_id}/"
    thumb_path = f"/usr/src/app/thumb/{user_id}.jpg"
    thumbnail = None
    if os.path.exists(thumb_path):
        thumbnail = thumb_path
    try:
        dir_content = []
        contents = os.listdir(directory)
        for fk in contents:
            if os.path.isfile(f"{directory}{fk}"):
                dir_content.append(fk)

        contents = sorted(dir_content)
    except:
        pass
    if cb_data == "yeah":
        await app.answer_callback_query(update.id, text="omg", show_alert=False)
        msg = await message.edit("**Trying to Upload**")
        if "*" in custom_name:
            for i, file in enumerate(contents, 1):
                new_name = custom_name.replace("*", f"{i:02d}")
                src = f"{directory}{file}"
                dst = f"{directory}{new_name}"
                try:
                    os.rename(src, dst)
                except Exception as e:
                    LOGGER.info(e)
        else:
            await app.answer_callback_query(update.id, text="wrong Format! Uploading without Rename", show_alert=False)
        try:
            await upload_dir(directory, msg, thumbnail)
        except FloodWait as fk:
            await asyncio.sleep(fk.value)
        clean_all(directory)
        await asyncio.sleep(3)
        await message.reply("Uploaded Successfully!", quote=True)

    elif cb_data == "hellno":
        await app.answer_callback_query(update.id, text="alright", show_alert=False)
        await files_keyboard(directory, message)

    elif cb_data == "upload":
        await app.answer_callback_query(update.id, text="alright", show_alert=False)
        msg = await message.edit("Trying To Upload")
        p_msg = await msg.reply("uploading")
        await msg.delete()
        await upload_dir(directory, p_msg, thumbnail)
        await asyncio.sleep(3)
        await message.reply("Uploaded Successfully!")
        try:
            clean_all(directory)
        except Exception:
            pass

    elif cb_data.startswith("rename"):
        await app.answer_callback_query(update.id, text="ok", show_alert=False)
        fi = cb_data.split(" ")
        file_num = fi[1]

        for i, file in enumerate(contents, 1):
            ind = "{:02d}".format(i)
            if ind == file_num:
                msg = await message.reply(f"send me new name for this file:\n\nName : `{file}`")
                na = await app.listen(message.chat.id)
                new_name = na.text
                await na.delete()
                await msg.delete()
                file_path = f"{directory}{file}"
                out = f"{directory}{new_name}"
                try:
                    os.rename(file_path, out)
                except Exception as e:
                    LOGGER.error(e)
            else:
                pass

    elif cb_data.startswith("none"):
        await app.answer_callback_query(update.id, text="click on rename", show_alert=False)

    elif cb_data == "help":
        help_text = "**Bot Commands -\n\nNote** : Bot is still Under Development..\n\n/leech - Reply this command " \
                    "to a Direct Link or Telegram media to download and Upload media from the link to " \
                    "Telegram\n/extract - Reply this command to a Direct Link or Telegram media to extract the file " \
                    "and upload it to Telegram\n/setname [Experimental] - To set a Custom Name to auto rename... similarly /rmname " \
                    "used to remove current Custom Name\n\n**Bot Limitations -\n\nFind it urself**\n\n#TODO - \n**ytdl support\nMulti Rename\nMagnet Support \nGoogle Drive Links Support\nMirror Support**"
        await message.edit(help_text)

    elif cb_data.startswith("cancel"):
        cl = cb_data.split()
        gid = cl[-1]
        LOGGER.info(f"gid is {gid}")
        aria2 = await aria_start()
        file = aria2.get_download(gid)
        aria2.remove(downloads=[file], force=True, files=True, clean=True)
        await message.reply("Download Cancelled 😶‍🌫️️")
        await message.delete()
        remove_user(user_id)
        
    elif cb_data.startswith('yt'):
        LOGGER.info(cb_data)
        await app.answer_callback_query(update.id)
        ms = await update.message.edit("Trying to download")
        d = cb_data.split()
        qual = d[1]
        user_id = d[2]
        dler = Youtube_dl(message)
        url = ytdlurls[user_id]
        if qual.startswith('bv*['):
            height = re_split(r'\[|\]', qual, maxsplit=2)[1]
            qual = qual + f"+ba/b[{height}]"
            LOGGER.info(qual)
        await dler.add_download(url, dl_directory, qual)
        ytdlurls.pop(user_id)
        await asyncio.sleep(5)
        await upload_dir(dl_directory, ms)
        clean_all(dl_directory)


async def upload_dir(directory, message, thumbnail=None):
    directory_contents = os.listdir(directory)
    directory_contents.sort()
    LOGGER.info(directory_contents)
    start = time()
    msg = await message.edit("**Uploading...**")

    for file in directory_contents:
        basename = os.path.basename(file)
        file_loc = f"{directory}{basename}"
        prog = Progress(message, basename, start)
        try:
            await upload(
                local_file_name=file_loc,
                message=msg,
                thumb = thumbnail,
                progress=prog.up_progress
            )
            await asyncio.sleep(3)
        except FloodWait as fd:
            await asyncio.sleep(fd.value)
    LOGGER.info("DOne")
    await msg.delete()



async def upload(local_file_name, message,thumb, progress):
    chat = message.chat.id
    file_name = os.path.basename(local_file_name)
    stats = os.stat(local_file_name)
    size = round((stats.st_size / (1024 * 1024)), 2)
    LOGGER.info("yeah")
    if not size < 1950.00:
        LOGGER.info("here")
        await message.edit(f"Can't Upload :( Due to Telegram Limitation\n\n**Size :** {size}MiB")
        return
    else:
        LOGGER.info("here maybe")
        try:
            if local_file_name.upper().endswith(("MKV", "MP4", "WEBM", "FLV", "3GP", "AVI", "MOV", "OGG", "WMV", "M4V", "TS", "MPG", "MTS", "M2TS")):
                LOGGER.info("may work now")
                await upload_video(message, progress, local_file_name)

            else:
                await message.reply_document(document=local_file_name, thumb=thumb, caption=f"<code>{file_name}</code>", disable_notification=True, progress=progress)

        except FloodWait as fk:
            await asyncio.sleep(fk.value)
        except Exception as e:
            LOGGER.info(e)
        return



def name(name):
    global custom_name
    custom_name = name


def remove_user(user_id):
    # removing proces data
    with open("./process/users.txt", "r") as f:
        lines = f.readlines()
    with open("./process/users.txt", "w") as fd:
        for line in lines:
            if line.strip("\n") != f"{user_id}":
                fd.write(line)
        fd.close()
        LOGGER.info(f"removed {user_id}")
        

def clean_all(dl_loc):
    LOGGER.info("Cleaning...")
    try:
        rmtree(dl_loc)
    except Exception as e:
        pass


async def upload_video(message, progress, local_file_name, yt_thumb = None):
    LOGGER.info("yo baby")
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
                parse_mode="html",
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