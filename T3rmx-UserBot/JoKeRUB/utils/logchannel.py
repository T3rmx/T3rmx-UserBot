"""Arabic log-channel helper.

Creates a private Telegram log channel once, stores its id in globals, and sends
only short text alerts there. The full log file is sent only on the owner's /log command.
"""

import os

from telethon.tl.functions.channels import CreateChannelRequest

from ..Config import Config
from ..core.logger import logging
from ..sql_helper.globals import addgvar, gvarstatus

LOGS = logging.getLogger("t3rmx.logchannel")

LOG_CHANNEL_GVAR = "T3RMX_LOG_CHANNEL_ID"


def _log_path() -> str:
    return os.path.abspath(os.environ.get("T3RMX_LOG_FILE", "logs/t3rmx.log"))


def _normalize_chat_id(value) -> int | None:
    try:
        cid = int(str(value).strip())
    except Exception:
        return None
    if cid == 0:
        return None
    if str(cid).startswith("-100"):
        return cid
    return int("-100" + str(abs(cid)))


async def get_log_channel_id():
    """Resolve the log channel id from globals or configured fallback."""
    stored = gvarstatus(LOG_CHANNEL_GVAR)
    if stored:
        cid = _normalize_chat_id(stored)
        if cid:
            return cid
    configured = getattr(Config, "PRIVATE_GROUP_BOT_API_ID", 0)
    if configured:
        return _normalize_chat_id(configured)
    return None


async def ensure_log_channel(client):
    """Create a private log channel once and remember its id."""
    stored = gvarstatus(LOG_CHANNEL_GVAR)
    if stored:
        existing = _normalize_chat_id(stored)
        if existing:
            return existing

    title = "سجلات T3rmx"
    about = "قناة خاصة للتنبيهات المختصرة. لا يتم إرسال ملف السجلات هنا تلقائياً."
    result = await client(
        CreateChannelRequest(
            title=title,
            about=about,
            broadcast=True,
        )
    )
    channel = result.chats[0]
    cid = _normalize_chat_id(channel.id)
    if not cid:
        return None
    addgvar(LOG_CHANNEL_GVAR, str(cid))
    if not getattr(Config, "PRIVATE_GROUP_BOT_API_ID", 0):
        addgvar("PRIVATE_GROUP_BOT_API_ID", str(cid))
    LOGS.info("تم إنشاء قناة السجلات بنجاح")
    return cid


async def send_log_alert(client, text: str) -> bool:
    """Send a short Arabic alert to the log channel. Never attaches a file."""
    try:
        cid = await get_log_channel_id()
        if not cid:
            return False
        clean = str(text).strip()
        if len(clean) > 900:
            clean = clean[:900] + " …"
        await client.send_message(cid, clean, link_preview=False)
        return True
    except Exception as e:
        LOGS.debug("تعذر إرسال تنبيه السجلات: %s", e)
        return False


async def send_log_file(client, chat_id=None) -> bool:
    """Send the full log file as a document, only when explicitly requested."""
    try:
        target = chat_id or await get_log_channel_id()
        if not target:
            return False
        path = _log_path()
        await client.send_file(
            target,
            path,
            force_document=True,
            caption="**ملف سجلات T3rmx**",
        )
        return True
    except Exception as e:
        LOGS.debug("تعذر إرسال ملف السجلات: %s", e)
        return False
