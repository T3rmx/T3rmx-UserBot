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

class NullAssistantBot:
    """Safe stand-in when the assistant bot cannot start.

    Plugins register buttons/inline handlers at import time. With a real client
    missing, a no-op client keeps every plugin loadable instead of crashing on
    `None.on(...)`. Assistant-only actions simply do nothing.
    """

    available = False
    me = None

    def on(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def add_event_handler(self, *args, **kwargs):
        return None

    def __getattr__(self, name):
        async def noop(*args, **kwargs):
            return None

        return noop


# Assistant bot (optional, requires valid token)
ASSISTANT_AVAILABLE = False
tgbot = NullAssistantBot()
if l313l is not None:
    l313l.tgbot = tgbot

try:
    if l313l and getattr(Config, "TG_BOT_TOKEN", None):
        real_bot = HuReClient(
            session="t3rmx-assistant",
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            loop=loop,
            app_version=__version__,
            connection=ConnectionTcpAbridged,
            auto_reconnect=True,
            connection_retries=None,
        ).start(bot_token=Config.TG_BOT_TOKEN)
        l313l.tgbot = tgbot = real_bot
        ASSISTANT_AVAILABLE = True
except AccessTokenExpiredError:
    LOGS.warning("Bot token expired; assistant features are disabled.")
except AccessTokenInvalidError:
    LOGS.warning("Invalid bot token; assistant features are disabled.")
except Exception as e:
    LOGS.warning("Assistant bot unavailable (%s); assistant features are disabled.", type(e).__name__)
