import asyncio
from threading import Thread
from yt_dlp import YoutubeDL, DownloadError
from bot.modules.logger import LOGGER
from random import SystemRandom
from time import sleep
from pyrogram.errors import MessageNotModified, FloodWait
from re import search as re_search
from threading import RLock
import time
import math


class MyLogger:
    def __init__(self, obj):
        self.obj = obj

    def debug(self, msg):
        # Hack to fix changing extension
        match = re_search(r'.Merger..Merging formats into..(.*?).$', msg)  # To mkv
        if not match and not self.obj.is_playlist:
            match = re_search(r'.ExtractAudio..Destination..(.*?)$', msg)  # To mp3
        if match and not self.obj.is_playlist:
            newname = match.group(1)
            newname = newname.split("/")[-1]
            self.obj.name = newname

    @staticmethod
    def warning(msg):
        LOGGER.warning(msg)

    @staticmethod
    def error(msg):
        if msg != "ERROR: Cancelling...":
            LOGGER.error(msg)


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


class Youtube_dl:
    def __init__(self, message):
        self.message = message
        self.__is_cancelled = False
        self.__downloading = False
        self.name = ""
        self.isfinished = False
        self.is_playlist = False
        self.__resource_lock = RLock()
        self.progress = 0
        self.size = 0
        self.speed = ''
        self.elapsed = 0
        self.eta = 0
        self.downloaded_bytes = 0
        self.opts = {'progress_hooks': [self.__onDownloadProgress],
                     'logger': MyLogger(self),
                     'usenetrc': True,
                     'embedsubtitles': True,
                     'prefer_ffmpeg': True,
                     'cookiefile': 'cookies.txt'}

    @property
    def nothing(self):
        return

    def __onDownloadProgress(self, d):
        if self.__is_cancelled:
            raise ValueError("Cancelling...")
        if d['status'] == "finished":
            if self.is_playlist:
                self._last_downloaded = 0
            self.isfinished = True
            self.__downloading = False
        elif d['status'] == "downloading":
            self.__downloading = True
            with self.__resource_lock:
                self.speed = d['speed']
                if self.is_playlist:
                    downloadedBytes = d['downloaded_bytes']
                    chunk_size = downloadedBytes - self._last_downloaded
                    self._last_downloaded = downloadedBytes
                    self.downloaded_bytes += chunk_size
                else:
                    if d.get('total_bytes'):
                        self.size = d['total_bytes']
                    elif d.get('total_bytes_estimate'):
                        self.size = d['total_bytes_estimate']
                    self.downloaded_bytes = d['downloaded_bytes']
                self.elapsed = d['elapsed']
                self.eta = d['eta']
                try:
                    self.progress = (self.downloaded_bytes / self.size) * 100
                except ZeroDivisionError:
                    pass

    async def start_dl(self, link):
        LOGGER.info(self.opts)
        with YoutubeDL(self.opts) as ytdl:
            try:
                LOGGER.info("Starting dl")
                Thread(target=ytdl.download, args=([link])).start()
                await self.progress_msg()
            except DownloadError as de:
                LOGGER.info(de)
            except Exception as ep:
                LOGGER.error(ep)

    async def add_download(self, link, path, qual):
        self.opts['format'] = qual
        LOGGER.info("downloading (yt-dlp)")
        with YoutubeDL() as yd:
            info = yd.extract_info(link, download=False)
            name_args = yd.prepare_filename(info)
            self.name = name_args.split('.')[0]
            LOGGER.info(self.name)
        self.opts['outtmpl'] = f"{path}{self.name}"
        await self.start_dl(link)

    async def progress_msg(self):
        msgg = await self.message.edit("Downloading")
        LOGGER.info(self.isfinished)
        start = time.time()
        while True:
            unfinished = "".join('◉' for i in range(math.floor(self.progress / 5)))
            finished = "".join('◌' for i in range(20 - math.floor(self.progress / 5)))
            progress = f"[{unfinished}{finished}]"
            now = time.time()
            elapsed = now - start
            msg = f'''
**Downloading using YTDLP**

**Name** : `{self.name}`

{progress} {self.progress : .2f}%

**Done** : `{humanbytes(self.downloaded_bytes)} of {humanbytes(self.size)}`
**Speed** : `{humanbytes(self.speed)}/s`
**Elapsed** : `{TimeFormatter(int(elapsed))}`
**ETA : `{TimeFormatter(self.eta)}`'''
            if self.__downloading:
                try:
                    await msgg.edit(msg)
                    await asyncio.sleep(3)
                except MessageNotModified as md:
                    await asyncio.sleep(2)
                except FloodWait as fd:
                    await asyncio.sleep(fd.value)
                except Exception as e:
                    LOGGER.error(e)

            elif self.isfinished:
                await msgg.edit(f"Downloaded!\n\n{self.name}\n({humanbytes(self.size)})")
                break

    def prog_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.progress_msg())
        loop.close()
