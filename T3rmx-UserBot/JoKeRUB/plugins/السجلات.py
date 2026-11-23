"""أوامر السجلات - إرسال ملف السجلات عند الطلب فقط."""

import os

from telethon import events

from JoKeRUB import l313l
from ..core.auth import is_owner
from ..core.logger import logging
from ..utils.logchannel import get_log_channel_id, send_log_alert, send_log_file

LOGS = logging.getLogger("t3rmx.logs")


def _log_path() -> str:
    return os.path.abspath(os.environ.get("T3RMX_LOG_FILE", "logs/t3rmx.log"))


@l313l.on(events.NewMessage(outgoing=True, pattern=r"^/log(?:\s+(\S+))?$"))
async def _send_logs_command(event):
    if not is_owner(event.sender_id):
        return

    target_arg = (event.pattern_match.group(2) or "").strip()
    try:
        target = int(target_arg) if target_arg else await get_log_channel_id()
    except Exception:
        target = target_arg

    if not target:
        await event.edit("**لم يتم تحديد قناة السجلات بعد.**")
        return

    await event.edit("**جاري إرسال ملف السجلات...**")
    ok = await send_log_file(event.client, target)
    if ok:
        await event.edit(f"**تم إرسال ملف السجلات إلى `{target}` بنجاح.**")
    else:
        await event.edit("**تعذر إرسال ملف السجلات. راجع سجلات الخادم.**")


@l313l.on(events.NewMessage(outgoing=True, pattern=r"^/(سجل|سجلات)$"))
async def _send_log_alert_command(event):
    if not is_owner(event.sender_id):
        return
    ok = await send_log_alert(event.client, "**اختبار التنبيه: قناة السجلات تعمل بشكل صحيح.**")
    await event.edit("**تم إرسال تنبيه تجريبي.**" if ok else "**تعذر إرسال التنبيه.**")


@l313l.on(events.NewMessage(outgoing=True, pattern=r"^/(مكانالسجل)$"))
async def _log_path_command(event):
    if not is_owner(event.sender_id):
        return
    await event.edit(f"**مسار ملف السجلات:** `{_log_path()}`")
