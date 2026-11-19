import os
from pathlib import Path

from telethon.tl.types import InputMessagesFilterDocument

from ..Config import Config
from ..utils import load_module
from . import BOTLOG, BOTLOG_CHATID, l313l

plugin_category = "tools"

if Config.PLUGIN_CHANNEL:

    async def install():
        documentss = await l313l.get_messages(
            Config.PLUGIN_CHANNEL, None, filter=InputMessagesFilterDocument
        )
        total = int(documentss.total)
        for module in range(total):
            plugin_to_install = documentss[module].id
            plugin_name = documentss[module].file.name
            if os.path.exists(f"JoKeRUB/plugins/{plugin_name}"):
                return
            downloaded_file_name = await l313l.download_media(
                await l313l.get_messages(Config.PLUGIN_CHANNEL, ids=plugin_to_install),
                "JoKeRUB/plugins/",
            )
            path1 = Path(downloaded_file_name)
            shortname = path1.stem
            try:
                load_module(shortname.replace(".py", ""))
            except Exception:
                pass
            if BOTLOG:
                await l313l.send_message(
                    BOTLOG_CHATID,
                    f"᯽︙ تـم تـنصـيب المـلف `{os.path.basename(downloaded_file_name)}` بـناج ✅.",
                )

    l313l.loop.create_task(install())
