import logging
import logging.handlers
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler(
            filename="./log.txt",
            mode='w'
        ),
        logging.StreamHandler(sys.stdout)
    ],
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.WARNING)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
