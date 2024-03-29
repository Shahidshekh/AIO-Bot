import asyncio
from shutil import rmtree
from time import time
from pyrogram import client
from bot.modules.downloader import Downloader, compress
from bot.modules.uploader import upload_video, upload_to_gdrive
from bot.modules.dl_progress import Progress
from bot.modules.logger import LOGGER
from bot.modules.callback import name
from bot.modules.mirrorGD import upload_gd
import os
from bot import authorized_chats

custom_name = ""


async def incoming_func(app, message):
    command = message.text
    user_id = message.from_user.id
    mess = message.reply_to_message
    thumbnail = None
    download_location = f"/usr/src/app/Download/{user_id}/"
    ext_location = f"/usr/src/app/extracted/{user_id}/"
    thumb_path = f"/usr/src/app/thumb/{message.from_user.id}.jpg"
    if os.path.exists(thumb_path):
        thumbnail = thumb_path
    download = Downloader(app, message, custom_name)
    reso = search(authorized_chats, str(message.chat.id))
    if not reso:
        await message.reply(
            text="I'm not familiar to this chat...\nPlease Contact @the_fourth_minato for authorization", quote=True)
        return

    if mess:
        res = user_validation(user_id, message)
        if res:
            if mess.media and user_id:
                file_name = await download.download_from_file(app)
                LOGGER.info(f"Downloaded : {file_name}")
                if command.lower().endswith('extract'):
                    LOGGER.info("Extracting...")
                    await download.extractit(file_name, ext_location)

                elif command.lower().endswith('mirror'):
                    mes = await mess.reply('Uploading to GDrive........')
                    await upload_gd(file_name, mes)
                    #await upload_to_gdrive(file_name, mes, user_id)

                elif command.lower().endswith('compress'):
                    try:
                        os.makedirs(ext_location)
                    except Exception:
                        pass

                    filename = os.path.basename(file_name)
                    out = f"{ext_location}{filename}"
                    await compress(file_name, out, message, user_id)
                else:
                    msg = await message.reply("**Trying to upload...**")
                    await upload_video(
                        user_id=user_id,
                        local_file_name=file_name,
                        message=msg,
                        thumb=thumbnail
                    )
                    await msg.delete()
                    await message.reply("Uploaded Successfully!")

            elif mess.text.startswith("http"):
                try:
                    c = mess.text.split(" | ")
                    url = c[0]
                    new_name = c[1]
                except:
                    url = mess.text
                    new_name = ""
                file_name = await download.download_from_link(url)
                if file_name is False:
                    return
                else:
                    if command.lower().endswith('extract'):
                        await download.extractit(file_name, ext_location)

                    elif command.lower().endswith('mirror'):
                        mes = await mess.reply('Uploading to GDrive........')
                        await upload_gd(file_name, mes)

                    elif command.lower().endswith('compress'):
                        try:
                            os.makedirs(ext_location)
                        except Exception:
                            pass
                        filename = os.path.basename(file_name)
                        out = f"{ext_location}{filename}"
                        await compress(file_name, out, message, user_id)
                    else:
                        if new_name != "":
                            os.rename(file_name, f"{download_location}{new_name}")
                            file_name = f"{download_location}{new_name}"

                        msg = await message.reply("**Trying to upload...**", quote=True)
                        await asyncio.sleep(3)
                        try:
                            await upload_video(
                                local_file_name=file_name,
                                message=msg,
                                user_id=user_id,
                                thumb=thumbnail
                            )
                            await message.reply("Uploaded Successfully!", quote=True)
                        except Exception as e:
                            LOGGER.error(e)

            else:
                await message.reply_text("Doesn't seem to be a <b>Download Source</b>", quote=True)

            remove_user(user_id)
            LOGGER.info("Cleaning...")
            try:
                rmtree(download_location)
            except Exception as e:
                LOGGER.info(e)

        elif not res:
            await message.reply("<b>Ongoing Process Found!</b> Please wait until it's complete", quote=True)
            return

    else:
        lol = await message.reply_text("Reply to a <b>Direct Link or Telegram Media</b>", quote=True)
        await asyncio.sleep(20)
        await message.delete()
        await lol.delete()
        return


async def set_name(app: client, message):
    msg = await app.send_message(message.chat.id, "Send me a Custom File Name\n\n**REMEMBER** The custom name "
                                                  "must end with a valid extension and must have character `*` "
                                                  "in it( which will be replaced as File Number(like 01 for the "
                                                  "first file ))\n\nExample : `Demon Slayer Ep*.mkv`")
    mess = await app.listen(message.chat.id)
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
