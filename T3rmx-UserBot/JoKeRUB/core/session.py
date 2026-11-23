import asyncio

from telethon.errors import AccessTokenExpiredError, AccessTokenInvalidError
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from telethon.sessions import StringSession

from ..Config import Config
from .aljokerUB import aljokerPyro
from .client import HuReClient
from .logger import logging

LOGS = logging.getLogger("t3rmx.session")

__version__ = getattr(Config, "T3RMX_VERSION", "1.0.0")

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

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

# Assistant bot: always a real client so every assistant plugin registers real
# handlers. Login is attempted asynchronously during startup (never at import
# time) so it uses the same event loop as the userbot.
ASSISTANT_AVAILABLE = False
tgbot = None
if l313l is not None:
    tgbot = HuReClient(
        session="t3rmx-assistant",
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        loop=loop,
        app_version=__version__,
        connection=ConnectionTcpAbridged,
        auto_reconnect=True,
        connection_retries=None,
    )
    l313l.tgbot = tgbot


async def start_assistant() -> bool:
    """Log the assistant bot in with retries. Never skip assistant plugins."""
    global ASSISTANT_AVAILABLE
    if tgbot is None:
        LOGS.warning("Assistant client is unavailable; check STRING_SESSION.")
        return False
    if getattr(tgbot, "is_connected", None) and tgbot.is_connected():
        ASSISTANT_AVAILABLE = True
        return True
    token = getattr(Config, "TG_BOT_TOKEN", None)
    if not token:
        LOGS.warning("TG_BOT_TOKEN is missing; assistant commands cannot connect.")
        return False
    for attempt in range(1, 4):
        try:
            await tgbot.start(bot_token=token)
            ASSISTANT_AVAILABLE = True
            LOGS.info("Assistant bot connected.")
            return True
        except (AccessTokenExpiredError, AccessTokenInvalidError) as exc:
            LOGS.warning("Assistant bot token rejected (%s).", type(exc).__name__)
            try:
                await tgbot.disconnect()
            except Exception:
                pass
            return False
        except Exception as exc:
            LOGS.warning(
                "Assistant bot login attempt %d/3 failed (%s).",
                attempt,
                type(exc).__name__,
            )
            try:
                await tgbot.disconnect()
            except Exception:
                pass
            if attempt < 3:
                await asyncio.sleep(attempt * 10)
    return False
