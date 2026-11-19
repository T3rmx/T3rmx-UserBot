import time

try:
    import heroku3  # optional, legacy compatibility
except Exception:
    heroku3 = None

from .Config import Config
from .core.logger import logging
from .core.session import l313l
from .sql_helper.globals import addgvar, delgvar, gvarstatus

__version__ = getattr(Config, "T3RMX_VERSION", "1.0.0")
__license__ = "GNU Affero General Public License v3.0 (see LICENSE)"
__author__ = "T3rmx Project"
__copyright__ = "T3rmx UserBot"

l313l.version = __version__
l313l.tgbot.version = __version__
LOGS = logging.getLogger("t3rmx")
bot = l313l

StartTime = time.time()
JEPVERSION = __version__
T3RMX_VERSION = __version__
T3RMX_REPOSITORY = getattr(Config, "T3RMX_REPOSITORY", "https://github.com/T3rmx/T3rmx-UserBot")
T3RMX_DISPLAY_NAME = getattr(Config, "T3RMX_DISPLAY_NAME", "T3rmx UserBot")

# Upstream/repository (compatibility)
UPSTREAM_REPO_URL = getattr(Config, "UPSTREAM_REPO", T3RMX_REPOSITORY) or T3RMX_REPOSITORY

# Bot logging configuration (safe defaults; no invented IDs)
if getattr(Config, "PRIVATE_GROUP_BOT_API_ID", 0) == 0:
    if gvarstatus("PRIVATE_GROUP_BOT_API_ID") is None:
        Config.BOTLOG = False
        Config.BOTLOG_CHATID = "me"
    else:
        try:
            Config.BOTLOG_CHATID = int(gvarstatus("PRIVATE_GROUP_BOT_API_ID"))
            Config.PRIVATE_GROUP_BOT_API_ID = int(gvarstatus("PRIVATE_GROUP_BOT_API_ID"))
            Config.BOTLOG = True
        except Exception:
            Config.BOTLOG = False
            Config.BOTLOG_CHATID = "me"
else:
    try:
        val = int(Config.PRIVATE_GROUP_BOT_API_ID)
        Config.BOTLOG_CHATID = val if str(val).startswith("-") else int("-" + str(val))
        Config.PRIVATE_GROUP_BOT_API_ID = val
        Config.BOTLOG = True
    except Exception:
        Config.BOTLOG = False
        Config.BOTLOG_CHATID = "me"

if getattr(Config, "PM_LOGGER_GROUP_ID", 0) == 0:
    if gvarstatus("PM_LOGGER_GROUP_ID") is None:
        Config.PM_LOGGER_GROUP_ID = -100
    else:
        try:
            Config.PM_LOGGER_GROUP_ID = int(gvarstatus("PM_LOGGER_GROUP_ID"))
        except Exception:
            Config.PM_LOGGER_GROUP_ID = -100
elif str(Config.PM_LOGGER_GROUP_ID)[0] != "-":
    try:
        Config.PM_LOGGER_GROUP_ID = int("-" + str(Config.PM_LOGGER_GROUP_ID))
    except Exception:
        Config.PM_LOGGER_GROUP_ID = -100

# Optional Heroku app handle (legacy compatibility only)
HEROKU_APP = None
try:
    if heroku3 and getattr(Config, "HEROKU_API_KEY", None) and getattr(Config, "HEROKU_APP_NAME", None):
        HEROKU_APP = heroku3.from_key(Config.HEROKU_API_KEY).apps()[Config.HEROKU_APP_NAME]
except Exception:
    HEROKU_APP = None


# Global Configiables
COUNT_MSG = 0
USERS = {}
COUNT_PM = {}
LASTMSG = {}
CMD_HELP = {}
ISAFK = False
AFKREASON = None
CMD_LIST = {}
SUDO_LIST = {}
# for later purposes
INT_PLUG = ""
LOAD_PLUG = {}

# Variables
BOTLOG = getattr(Config, "BOTLOG", False)
BOTLOG_CHATID = getattr(Config, "BOTLOG_CHATID", "me")
PM_LOGGER_GROUP_ID = getattr(Config, "PM_LOGGER_GROUP_ID", -100)
