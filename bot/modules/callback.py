from pyrogram.types import CallbackQuery
from bot.modules.logger import LOGGER
from bot.utils.client import app
from bot.database.db_client import up_mode, get_up_mode
from bot.modules.dl_progress import Progress
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from shutil import rmtree
import os
from pyromod import listen
from bot.modules.download_link import aria_start
from bot.modules.utils import files_keyboard
from pyrogram.errors import FloodWait
import asyncio
from bot.utils.ytdl import Youtube_dl
from bot import ytdlurls, filenames
from re import split as re_split
from bot.modules.uploader import upload_video

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
        if user_id != update.message.reply_to_message.from_user.id:
            await app.answer_callback_query(update.id, text="Not Urs 😑", show_alert=True)
            return
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
        if user_id != update.message.reply_to_message.from_user.id:
            await app.answer_callback_query(update.id, text="Not Urs 😑", show_alert=True)
            return
        await app.answer_callback_query(update.id, text="alright", show_alert=False)
        await files_keyboard(directory, message)

    elif cb_data == "upload":
        if user_id != update.message.reply_to_message.from_user.id:
            await app.answer_callback_query(update.id, text="Not Urs 😑", show_alert=True)
            return
        await app.answer_callback_query(update.id, text="alright", show_alert=False)
        msg = await message.edit("Trying To Upload")
        await msg.delete()
        await upload_dir(directory, msg, thumbnail)
        await asyncio.sleep(3)
        await message.reply("Uploaded Successfully!")
        try:
            clean_all(directory)
        except Exception:
            pass

    elif cb_data.startswith("rename"):
        if user_id != update.message.reply_to_message.from_user.id:
            await app.answer_callback_query(update.id, text="Not Urs 😑", show_alert=True)
            return
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
        if user_id != update.message.reply_to_message.from_user.id:
            await app.answer_callback_query(update.id, text="Not Urs 😑", show_alert=True)
            return
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
        await app.answer_callback_query(update.id)
        ms = await update.message.edit("Trying to download")
        d = cb_data.split()
        if d[1]=="cancel":
            await ms.edit("`Cancelled.`")
            return
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
    
    elif cb_data.startswith('c'):
        user = cb_data.split('|')[-1]
        filename = filenames[user]
        dl_loc = f"{dl_directory}{filename}"
        out_loc = f"{directory}{filename}"
        try:
            total = humanbytes(os.stat(dl_loc).st_size)
            current = humanbytes(os.stat(out_loc).st_size)
        except Exception as e:
            LOGGER.error(e)
        await app.answer_callback_query(update.id, text=f"STATS\n\nTotal : {total}\nDone : {current}", show_alert=True)

    elif cb_data == "mode":
        own = update.message.reply_to_message.from_user.id
        if user_id != own:
            await app.answer_callback_query(update.id, text="Not Urs 😑", show_alert=True)
            return
        mode = await get_up_mode(user_id)
        await up_mode(user_id, True if not mode else False)
        msgt = "**Upload Mode Set To** : `{0}`".format("Document" if not mode else "Streamable")
        text = "{0}".format("Document" if mode else "Streamable")
        await app.answer_callback_query(update.id, text="Switched!", show_alert=False)
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=f"{text}", callback_data="mode")]])
        await update.message.edit(f"{msgt}", reply_markup=reply_markup)




async def upload_dir(directory, message, thumbnail=None):
    directory_contents = os.listdir(directory)
    directory_contents.sort()
    start = time.time()
    user_id = message.reply_to_message.from_user.id
    msg = await message.edit("**Uploading.....**")

    for file in directory_contents:
        basename = os.path.basename(file)
        file_loc = f"{directory}{basename}"
        prog = Progress(message, basename, start)
        try:
            await upload_video(
                local_file_name=file_loc,
                message=msg,
                user_id=user_id,
                thumb = thumbnail,
                progress=prog.up_progress
            )
            await asyncio.sleep(3)
        except FloodWait as fd:
            await asyncio.sleep(fd.value)
    LOGGER.info("DOne")
    await msg.delete()



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
