from yt_dlp import YoutubeDL
from bot.modules.logger import LOGGER
from re import split as re_split
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot import ytdlurls


async def yt_dl(app, message):
    url = message.reply_to_message
    user_id = message.from_user.id
    urls = [url]
    opts = {"logger": LOGGER}
    ytdlurls.update({f"{user_id}": f"{url.text}"})
    LOGGER.info(ytdlurls)
    buttons = []
    lol = await message.reply("Getting Formats...", quote=True)
    with YoutubeDL() as ytdl:
        info = ytdl.extract_info(str(url.text), download=False)
        if 'entries' in info:
            for i in ['144', '240', '360', '480', '720', '1080', '1440', '2160']:
                video_format = f"bv*[height<={i}][ext=mp4]"
                LOGGER.info(video_format)
                video_format = f"bv*[height<={i}][ext=webm]"
                LOGGER.info(video_format)

        else:
            formats = info.get('formats')
            formats_dict = {}
            if formats is not None:
                for frmt in formats:
                    if not frmt.get('tbr') or not frmt.get('height'):
                        continue

                    if frmt.get('fps'):
                        quality = f"{frmt['height']}p{frmt['fps']}-{frmt['ext']}"
                    else:
                        quality = f"{frmt['height']}p-{frmt['ext']}"

                    if frmt.get('filesize'):
                        size = frmt['filesize']
                    elif frmt.get('filesize_approx'):
                        size = frmt['filesize_approx']
                    else:
                        size = 0

                    if quality in list(formats_dict.keys()):
                        formats_dict[quality][frmt['tbr']] = size
                    else:
                        subformat = {}
                        subformat[frmt['tbr']] = size
                        formats_dict[quality] = subformat

                for _format in formats_dict:
                    if len(formats_dict[_format]) == 1:
                        qual_fps_ext = re_split(r'p|-', _format, maxsplit=2)
                        height = qual_fps_ext[0]
                        fps = qual_fps_ext[1]
                        ext = qual_fps_ext[2]
                        if fps != '':
                            video_format = f"bv*[height={height}][fps={fps}][ext={ext}]"
                        else:
                            video_format = f"bv*[height={height}][ext={ext}]"
                        size = humanbytes(list(formats_dict[_format].values())[0])
                        buttons.append(
                            InlineKeyboardButton(text=f"{_format}--{size}", callback_data=f"yt {video_format} {user_id}")
                        )
                    resize = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
                butt_markup = InlineKeyboardMarkup(resize)
                await lol.edit("select format :", reply_markup=butt_markup)


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
