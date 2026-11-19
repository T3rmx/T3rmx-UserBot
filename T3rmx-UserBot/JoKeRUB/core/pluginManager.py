import asyncio
import os
import sys

from telethon import TelegramClient

from ..Config import Config
from ..core.logger import logging
from ..sql_helper.global_collection import (
    add_to_collectionlist,
    del_keyword_collectionlist,
    get_collectionlist_items,
)

LOGS = logging.getLogger("t3rmx.core.pluginmanager")


async def install_pip_packages(packages):
    """Install pip packages only when explicitly allowed.

    Runtime package installation is disabled by default for security and reproducibility.
    """
    if not getattr(Config, "T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False):
        LOGS.warning("Blocked runtime pip package installation request (disabled by default).")
        return False
    try:
        args = ["-m", "pip", "install", "--upgrade", "--user", *packages]
        cmd = await asyncio.create_subprocess_exec(
            sys.executable.replace(" ", "\\ "),
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await cmd.communicate()
        return cmd.returncode == 0
    except Exception as e:
        LOGS.error(f"Runtime pip install failed: {e}")
        return False


async def restart_script(client: TelegramClient, jasme):
    """Restart the current process (in-repo runtime)."""
    try:
        ulist = get_collectionlist_items()
        for i in ulist:
            if i == "restart_update":
                del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.debug(e)
    try:
        add_to_collectionlist("restart_update", [jasme.chat_id, jasme.id])
    except Exception as e:
        LOGS.debug(e)
    executable = sys.executable.replace(" ", "\\ ")
    args = [executable, "-m", "JoKeRUB"]
    os.execle(executable, *args, os.environ)
    sys.exit(0)


async def get_message_link(client, event):
    chat = await event.get_chat()
    if event.is_private:
        return f"tg://openmessage?user_id={chat.id}&message_id={event.id}"
    chat_id = getattr(chat, "id", None)
    return f"https://t.me/c/{chat_id}/{event.id}"
