import asyncio
from shutil import rmtree
from time import time
from pyrogram import client
from bot.modules.downloader import Downloader
from bot.modules.dl_progress import Progress
from bot.modules.logger import LOGGER
from bot.modules.callback import name
import os

custom_name = ""


async def incoming_func(app, message):
    command = message.text
    user_id = message.from_user.id
    mess = message.reply_to_message
    st = time()
    download_location = f"/usr/src/app/Download/{user_id}/"
    ext_location = f"/usr/src/app/extracted/{user_id}/"
    download = Downloader(app, message, custom_name, url)
    c = mess.text.split(" | ")
    try:
        url = c[0]
        new_name = c[1]
    except:
        url = c
        new_name = ""

    if mess:
        res = user_validation(user_id, message)
        if res:
            if mess.media and user_id:
                file_name = await download.download_from_file(app)
                LOGGER.info(f"Downloaded : {file_name}")
                if command.endswith('extract'):
                    LOGGER.info("Extracting...")
                    await download.extractit(file_name, ext_location)
                else:
                    msg = await message.reply("**Trying to upload...**")
                    prog = Progress(msg, file_name, st)
                    files = os.listdir(download_location)
                    LOGGER.info(files)
                    await download.upload(
                        file_name,
                        msg,
                        prog.up_progress
                    )
                    await msg.delete()
                    await message.reply("Uploaded Successfully!")

            elif mess.text.startswith("http"):

                file_name = await download.download_from_link()
                if file_name is False:
                    return
                else:
                    if command.endswith('extract'):
                        await download.extractit(file_name, ext_location)
                        
                    else:
                        if new_name != "":
                            os.rename(f"{download_location}{file_name}", f"{download_location}{new_name}")
                            file_name = new_name
                                      
                        msg = await message.reply("**Trying to upload...**")
                        await asyncio.sleep(3)
                        prog = Progress(msg, file_name, st)
                        try:
                            await download.upload(
                                file_name,
                                msg,
                                prog.up_progress
                            )
                            await message.reply("Uploaded Successfully!", quote=True)
                        except Exception as e:
                            LOGGER.error(e)

            else:
                await message.reply_text("Doesn't seem to be a <b>Download Source</b>", quote=True)

            remove_user(user_id)

        elif not res:
            await message.reply("<b>Ongoing Process Found!</b> Please wait until it's complete", quote=True)
            LOGGER.info("Working ig")
            return

    else:
        lol = await message.reply_text("Reply to a <b>Direct Link or Telegram Media</b>", quote=True)
        await asyncio.sleep(10)
        await lol.delete()
        return




async def set_name(app: client, message):
    msg = await app.send_message(message.from_user.id, "Send me a Custom File Name\n\n**REMEMBER** The custom name "
                                                       "must end with a valid extension and must have character `*` "
                                                       "in it( which will be replaced as File Number(like 01 for the "
                                                       "first file ))\n\nExample : `Demon Slayer Ep*.mkv`")
    mess = await app.listen(message.from_user.id)
    global custom_name
    custom_name = mess.text
    await mess.delete()
    await msg.edit(f"Custom Name Set To - <b>{custom_name}</b>")
    name(custom_name)


async def remove_name(app: client, message):
    global custom_name
    custom_name = ""
    m = await message.reply(text="Custom name removed successfully!")
    await asyncio.sleep(8)
    await m.delete()
    name(custom_name)


def search(listed, item):
    for i in range(len(listed)):
        if listed[i] == item:
            return True
    return False


def user_validation(user_id, msg):
    if os.path.exists("./process/users.txt"):
        LOGGER.info("exist")
        f = open("./process/users.txt", mode="r+")
        fr = f.readlines()
        f.close()
        for line in fr:
            LOGGER.info(line)
            if line.strip("\n") == str(user_id):
                LOGGER.info("user exist")
                return False
        fd = open("./process/users.txt", mode="w")
        fd.write(f"{user_id}\n")
        fd.close()
        return True
    else:
        try:
            os.mkdir("./process")
        except:
            pass
        f = open("./process/users.txt", mode="x")
        f.write(f"{user_id}\n")
        f.close()
        return True


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
