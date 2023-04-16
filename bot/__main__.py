from bot.modules.junction import incoming_func, set_name, remove_name
from bot.modules.callback import cb
from pyrogram import idle, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.modules.logger import LOGGER
from bot.utils.thumb import set_thumb, rm_thumb
from bot.utils.youtube_dl import yt_dl
from bot.database.db_client import add_user
from bot.modules.utils import log, restart, db_users_count, settings
from pyrogram import Client
import os

if __name__ == "__main__":
    app = Client(
        "hello",
        api_id=11873433,
        api_hash="96abaf0d59cd1f5482bdc93ba6030424",
        bot_token="5553254288:AAHvhjrbImGLZNQlHgb_TEG43Fuf3UfD47g"
    )
    app.start()


async def startr():
    try:
        with open("/usr/src/app/.restartmg") as fk:
            chat_id, msg_id = map(int, fk)
            await app.edit_message_text(chat_id=chat_id, message_id=msg_id, text="Restarted Successfully!")
            os.remove("/usr/src/app/.restartmg")
    except Exception as e:
        LOGGER.error(e)


@app.on_message(filters.command('start'))
async def start_command(app, message):
    help_button = [
        [
            InlineKeyboardButton("Help", callback_data="help"),
            InlineKeyboardButton("Owner", url="https://t.me/the_fourth_minato")
        ]
    ]
    user = message.from_user.id
    name = message.from_user.first_name
    await add_user(user)
    await message.reply_text(f"Hello <a href='t.me/{user}'>{name}</a>! 😉\n\nThis is a all in one bot and "
                             f"can do a lot of things. 😁\nStill under Devlopment so u can may Encounter some errors. "
                             f"\n\nMaintained and Purely coded by :\n\n@The_Fourth_Minato 💫\n\n"
                             f"**FIXING SOME ERRORS**",
                             quote=True,
                             reply_markup=InlineKeyboardMarkup(help_button)
                             )


# ##############################################################################################################################
leech_handler = MessageHandler(
    incoming_func,
    filters=filters.command(['leech', 'extract', 'compress', 'mirror'])
)
app.add_handler(leech_handler)

set_custom_name = MessageHandler(
    set_name,
    filters=filters.command('setname')
)
app.add_handler(set_custom_name)

callback = CallbackQueryHandler(cb)
app.add_handler(callback)

rm_custom_name = MessageHandler(
    remove_name,
    filters=filters.command("rmname")
)
app.add_handler(rm_custom_name)

set_name_handler = MessageHandler(
    set_thumb,
    filters=filters.command("setthumb")
)
app.add_handler(set_name_handler)

rm_thumb_handler = MessageHandler(
    rm_thumb,
    filters=filters.command("rmthumb")
)
app.add_handler(rm_thumb_handler)

ytdl_handler = MessageHandler(
    yt_dl,
    filters=filters.command('ytdl')
)
app.add_handler(ytdl_handler)

log_handler = MessageHandler(
    log,
    filters=filters.command('logs')
)
app.add_handler(log_handler)

restart_handler = MessageHandler(
    restart,
    filters=filters.command('restart')
)
app.add_handler(restart_handler)

users_handler = MessageHandler(
    db_users_count,
    filters=filters.command('users')
)
app.add_handler(users_handler)

settings_handler = MessageHandler(
    settings,
    filters=filters.command('settings')
)
app.add_handler(settings_handler)
###########################################################################################################################

LOGGER.info("The Bot Has Been Started 😎")
app.run(startr())
idle()

app.stop()
