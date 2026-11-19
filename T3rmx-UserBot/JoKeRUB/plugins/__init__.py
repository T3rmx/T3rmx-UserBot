import math
import os
import re
import time


try:
    import heroku3  # optional legacy dependency
except Exception:
    heroku3 = None
try:
    import lottie
except Exception:
    lottie = None
try:
    import requests
except Exception:
    requests = None
try:
    import spamwatch as spam_watch
except Exception:
    spam_watch = None
try:
    from validators.url import url
except Exception:
    def url(_):
        return False

from .. import *
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..core.session import l313l
from ..helpers import *
try:
    from ..helpers.utils import _cattools, _catutils, _format, reply_id
except Exception:
    _cattools = _catutils = _format = reply_id = None
try:
    from l313l.razan.resources.Gif import *
except Exception:
    pass
# =================== CONSTANT ===================
bot = l313l
LOGS = logging.getLogger(__name__)
USERID = getattr(l313l, "uid", 0) if getattr(Config, "OWNER_ID", 0) == 0 else Config.OWNER_ID
ALIVE_NAME = getattr(Config, "ALIVE_NAME", "T3rmx UserBot")
AUTONAME = getattr(Config, "AUTONAME", None)
DEFAULT_BIO = getattr(Config, "DEFAULT_BIO", None)
DEFAULT_GROUP = getattr(Config, "DEFAULT_GROUP", None)


Heroku = None
heroku_api = "https://api.heroku.com"
HEROKU_APP_NAME = getattr(Config, "HEROKU_APP_NAME", None)
HEROKU_API_KEY = getattr(Config, "HEROKU_API_KEY", None)
try:
    if heroku3 and HEROKU_API_KEY:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
except Exception:
    Heroku = None

thumb_image_path = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")

USERID = l313l.uid if Config.OWNER_ID == 0 else Config.OWNER_ID

# mention user
mention = f"[{Config.ALIVE_NAME}](tg://user?id={USERID})"
hmention = f"<a href = tg://user?id={USERID}>{Config.ALIVE_NAME}</a>"

PM_START = []
PMMESSAGE_CACHE = {}
PMMENU = "pmpermit_menu" not in Config.NO_LOAD

# Gdrive
G_DRIVE_CLIENT_ID = Config.G_DRIVE_CLIENT_ID
G_DRIVE_CLIENT_SECRET = Config.G_DRIVE_CLIENT_SECRET
G_DRIVE_DATA = Config.G_DRIVE_DATA
G_DRIVE_FOLDER_ID = Config.G_DRIVE_FOLDER_ID
TMP_DOWNLOAD_DIRECTORY = Config.TMP_DOWNLOAD_DIRECTORY

# spamwatch support
if Config.SPAMWATCH_API:
    token = Config.SPAMWATCH_API
    spamwatch = spam_watch.Client(token)
else:
    spamwatch = None


# ================================================

if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
    os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)


# thumb image
if getattr(Config, "THUMB_IMAGE", None) is not None and requests is not None:
    check = url(Config.THUMB_IMAGE)
    if check:
        try:
            with open(thumb_image_path, "wb") as f:
                f.write(requests.get(Config.THUMB_IMAGE).content)
        except Exception as e:
            LOGS.info(str(e))


def set_key(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = value
    elif isinstance(dictionary[key], list):
        if value in dictionary[key]:
            return
        dictionary[key].append(value)
    else:
        dictionary[key] = [dictionary[key], value]


async def make_gif(event, reply, quality=None, fps=None):
    fps = fps or 1
    quality = quality or 256
    result_p = os.path.join("temp", "animation.gif")
    animation = lottie.parsers.tgs.parse_tgs(reply)
    with open(result_p, "wb") as result:
        await _catutils.run_sync(
            lottie.exporters.gif.export_gif, animation, result, quality, fps
        )
    return result_p



