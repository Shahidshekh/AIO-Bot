import asyncio
import os
import aria2p
import sys
from pyrogram.errors import FloodWait, MessageNotModified
from time import time
from bot.modules.logger import LOGGER
import math
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

sys.setrecursionlimit(10 ** 4)


async def aria_start():
    aria2_daemon_start_cmd = ["aria2c", "--check-certificate=false", "--allow-overwrite=true", "--daemon=true",
                              "--enable-rpc=true", "--disk-cache=0", "--follow-torrent=mem",
                              "--max-connection-per-server=16", "--min-split-size=10M", "--rpc-listen-all=true",
                              f"--rpc-listen-port=6800", "--rpc-max-request-size=1024M", "--seed-ratio=0.01",
                              "--seed-time=1", "--max-overall-upload-limit=2M", "--split=16", f"--bt-stop-timeout=200"]

    command = await asyncio.create_subprocess_exec(
        *aria2_daemon_start_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    start, aria = await command.communicate()
    aria2 = aria2p.API(
        aria2p.Client(host="http://localhost", port=6800, secret="")
    )
    return aria2


async def progress_aria(aria2, gid, event, user):
    cancel_butt = [[InlineKeyboardButton(text="cancel", callback_data=f"cancel {gid}")]]
    cancel = InlineKeyboardMarkup(cancel_butt)
    while True:
        try:
            file = aria2.get_download(gid)
            complete = file.is_complete
            if not complete:
                if not file.error_message:
                    if file.has_failed:
                        LOGGER.error(f"Failed to download {file.name}")
                        await event.reply(f"Download Failed :{file.name}")
                        file.remove(force=True, files=True)
                        return
                else:
                    msg = file.error_message
                    LOGGER.error(msg)
                    await asyncio.sleep(5)
                    await event.reply(f"`{msg}`")
                    remove_user(user)
                    return
                if file.is_active:
                    percentage = int(file.progress_string(0).split('%')[0])
                    finished = "".join('◉' for i in range(math.floor(percentage / 5)))
                    unfinished = "".join('◌' for i in range(20 - math.floor(percentage / 5)))
                    progress = f"[{finished}{unfinished}]"
                    prog = file.progress_string()
                    total = file.total_length_string()
                    speed = file.download_speed_string()
                    eta = file.eta_string()
                    smsg = f"**Downloading** \n**Name**:<code>{file.name}</code>\n\n{progress}\n\n**Done** : __{prog}_"\
                           f"_of __{total}__\n**Speed** : __{speed}__\n**ETA** : __{eta}__ "
                    try:
                        await event.edit(smsg, reply_markup=cancel)
                    except MessageNotModified:
                        await asyncio.sleep(5)
            else:
                await event.edit(f"`Downloaded` : \n`{file.name}` 😎️\n`Total Size` : ({file.total_length_string()})")
                LOGGER.info(f"Downloaded :{file.name} Size : {file.total_length_string()}")
                await asyncio.sleep(5.0)
                await event.delete()
                return file.name

        except MessageNotModified:
            await asyncio.sleep(3.0)

        except FloodWait as fd:
            LOGGER.error(fd)
            time.sleep(fd.x)
            return

        except Exception as e:
            LOGGER.error(e)
            return


def add_url(aria_instance, url, path):
    options = None
    uris = [url]
    LOGGER.info(uris)

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            LOGGER.info(e)

    try:
        download = aria_instance.add_uris(uris, {'dir': path})
    except Exception as e:
        return (
            False,
            "**Failed**"
        )

    else:
        return True, "" + download.gid + ""
    
    
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
