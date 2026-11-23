import sys

import JoKeRUB
from JoKeRUB import BOTLOG_CHATID, PM_LOGGER_GROUP_ID
from .Config import Config
from .core.logger import logging
from .core.session import l313l
from .utils import (
    add_bot_to_logger_group,
    load_plugins,
    setup_bot,
    mybot,
    startupmessage,
    verifyLoggerGroup,
    saves,
)

LOGS = logging.getLogger("t3rmx")

print(getattr(JoKeRUB, "T3RMX_DISPLAY_NAME", "T3rmx UserBot"))
print(f"Repository: {getattr(JoKeRUB, 'T3RMX_REPOSITORY', 'https://github.com/T3rmx/T3rmx-UserBot')}")
print("License: " + JoKeRUB.__license__)

cmdhr = Config.COMMAND_HAND_LER


try:
    LOGS.info("Starting T3rmx UserBot...")
    l313l.loop.run_until_complete(setup_bot())
    LOGS.info("Core setup completed.")
except Exception as e:
    LOGS.error(f"{str(e)}")
    sys.exit(1)

try:
    LOGS.info("Initializing assistant bot session...")
    l313l.loop.run_until_complete(mybot())
    LOGS.info("Assistant bot initialized.")
except Exception as e:
    LOGS.warning(f"Assistant bot initialization warning: {e}")


class CatCheck:
    def __init__(self):
        self.sucess = True


Catcheck = CatCheck()


async def startup_process():
    # Log groups and optional features are controlled by configuration (safe defaults).
    await verifyLoggerGroup()
    await load_plugins("plugins")
    # Assistant plugins register handlers on the assistant client; load them only
    # when that client exists (the bot token may be absent or Telegram may fail).
    if getattr(l313l, "tgbot", None) is not None:
        await load_plugins("assistant")
    else:
        LOGS.info("Assistant plugins skipped: assistant bot is unavailable.")

    # Optional, explicitly controlled startup actions
    try:
        await saves()
    except Exception as e:
        LOGS.debug(f"Startup optional actions skipped: {e}")

    print("------------------------------------------------------------")
    print(f"{getattr(Config, 'T3RMX_DISPLAY_NAME', 'T3rmx UserBot')} is running.")
    print(f"Send {cmdhr}الاوامر or {cmdhr}help in chat to view commands.")
    print(f"Repository: {getattr(Config, 'T3RMX_REPOSITORY', 'https://github.com/T3rmx/T3rmx-UserBot')}")
    print("------------------------------------------------------------")

    if getattr(Config, "T3RMX_ENABLE_AUTO_LOG_GROUPS", False):
        try:
            await add_bot_to_logger_group(BOTLOG_CHATID)
        except Exception:
            pass
        try:
            if PM_LOGGER_GROUP_ID != -100:
                await add_bot_to_logger_group(PM_LOGGER_GROUP_ID)
        except Exception:
            pass
    try:
        await startupmessage()
    except Exception as e:
        LOGS.debug(f"Startup message skipped: {e}")

    Catcheck.sucess = True
    return


l313l.loop.run_until_complete(startup_process())

if len(sys.argv) not in (1, 3, 4):
    try:
        l313l.disconnect()
    except Exception:
        pass
elif not Catcheck.sucess:
    # Avoid forced platform restarts; exit with error for supervisor/systemd/platform to handle if desired.
    sys.exit(1)
else:
    try:
        l313l.run_until_disconnected()
    except ConnectionError:
        pass
