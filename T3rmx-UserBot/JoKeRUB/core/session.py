import sys

from telethon.errors import AccessTokenExpiredError, AccessTokenInvalidError
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from telethon.sessions import StringSession

from ..Config import Config
from .aljokerUB import aljokerPyro
from .client import HuReClient
from .logger import logging

LOGS = logging.getLogger("t3rmx.session")

__version__ = getattr(Config, "T3RMX_VERSION", "1.0.0")

loop = None

if getattr(Config, "STRING_SESSION", None):
    session = aljokerPyro(Config.STRING_SESSION, LOGS)
else:
    session = "t3rmx-userbot"

l313l = None
try:
    l313l = HuReClient(
        session=session,
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        loop=loop,
        app_version=__version__,
        connection=ConnectionTcpAbridged,
        auto_reconnect=True,
        connection_retries=None,
    )
except Exception as e:
    LOGS.error(f"[STRING SESSION] - {str(e)}")
    l313l = None

# Assistant bot (optional, requires valid token)
tgbot = None
try:
    if l313l and getattr(Config, "TG_BOT_TOKEN", None):
        l313l.tgbot = tgbot = HuReClient(
            session="t3rmx-assistant",
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            loop=loop,
            app_version=__version__,
            connection=ConnectionTcpAbridged,
            auto_reconnect=True,
            connection_retries=None,
        ).start(bot_token=Config.TG_BOT_TOKEN)
    elif l313l:
        l313l.tgbot = None
except AccessTokenExpiredError:
    LOGS.error("Bot token expired. Set a valid TG_BOT_TOKEN to enable assistant features.")
    if l313l:
        l313l.tgbot = None
except AccessTokenInvalidError:
    LOGS.error("Invalid bot token. Set a valid TG_BOT_TOKEN to enable assistant features.")
    if l313l:
        l313l.tgbot = None
except Exception as e:
    LOGS.warning(f"Assistant bot setup skipped: {e}")
    if l313l:
        l313l.tgbot = None
