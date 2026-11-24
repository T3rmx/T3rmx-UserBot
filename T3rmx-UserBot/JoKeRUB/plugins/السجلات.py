"""أوامر السجلات - إرسال ملف السجلات عند الطلب فقط."""

import os

from telethon import events

from JoKeRUB import l313l
from ..core.auth import is_owner
from ..core.logger import logging
from ..utils.logchannel import (
    apply_backup_config,
    delete_backups,
    ensure_log_channel,
    is_backup_message,
    refresh_backup,
    restore_settings_if_empty,
    send_log_alert,
    send_log_file,
)

LOGS = logging.getLogger("t3rmx.logs")


def _log_path() -> str:
    return os.path.abspath(os.environ.get("T3RMX_LOG_FILE", "logs/t3rmx.log"))


async def _replied_backup(event):
    """Return the replied backup document, or None if the reply is not one."""
    if not event.reply_to_msg_id:
        return None
    try:
        reply = await event.get_reply_message()
    except Exception:
        return None
    return reply if is_backup_message(reply) else None


@l313l.on(events.NewMessage(outgoing=True, pattern=r"^/log(?:\s+(\S+))?$"))
async def _send_logs_command(event):
    if not is_owner(event.sender_id):
        return

    target_arg = (event.pattern_match.group(1) or "").strip()
    try:
        # The log channel receives short alerts only; the full file goes to the owner.
        target = int(target_arg) if target_arg else event.sender_id
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


@l313l.ar_cmd(pattern="الاشعارات تفعيل$")
async def _enable_notifications_command(event):
    if not is_owner(event.sender_id):
        return
    chat_id, created = await ensure_log_channel(event.client)
    if not chat_id:
        await event.edit("**تعذر تجهيز قناة الإشعارات. حاول مرة أخرى.**")
        return
    note = (
        "- تم إنشاء قناة الإشعارات وتكتمها وأرشفتها تلقائياً ✓\n"
        if created
        else "- تم استخدام قناة الإشعارات الحالية بدون إنشاء قناة جديدة ✓\n"
    )

    # Give the owner a clickable link instead of a raw numeric chat id.
    try:
        entity = await event.client.get_entity(chat_id)
    except Exception:
        entity = None
    title = getattr(entity, "title", None) or "قناة السجلات"
    username = getattr(entity, "username", None)
    if username:
        link = f"https://t.me/{username}"
    else:
        numeric = str(abs(chat_id))
        if numeric.startswith("100"):
            numeric = numeric[3:]
        link = f"https://t.me/c/{numeric}/1"

    await event.edit(
        note + f"**تم تفعيل الإشعارات. افتح القناة: [{title}]({link})**",
        link_preview=False,
    )


@l313l.ar_cmd(pattern="النسخة الاحتياطية$")
async def _refresh_backup_command(event):
    if not is_owner(event.sender_id):
        return
    await event.edit("**جاري تحديث النسخة الاحتياطية للإعدادات...**")
    ok = await refresh_backup(event.client, force=True)
    await event.edit(
        "**تم إنشاء نسخة احتياطية جديدة وحذف النسخ القديمة بنجاح.**"
        if ok
        else "**تعذر تحديث النسخة الاحتياطية. راجع سجلات الخادم.**"
    )


@l313l.ar_cmd(pattern=r"استعادة النسخة(?:\s+(\d+))?$")
async def _restore_backup_command(event):
    if not is_owner(event.sender_id):
        return
    message_id = (event.pattern_match.group(1) or "").strip() or None
    reply_message = await _replied_backup(event)
    if event.reply_to_msg_id and not reply_message:
        await event.edit("**الرد يجب أن يكون على ملف النسخة الاحتياطية في قناة السجلات.**")
        return
    label = f" `{message_id}`" if message_id else (" المحدد بالرد" if reply_message else "")
    await event.edit(f"**جاري استعادة الإعدادات من النسخة الاحتياطية{label}...**")
    ok = await restore_settings_if_empty(
        event.client,
        force=True,
        message_id=message_id,
        reply_message=reply_message,
    )
    if ok:
        apply_backup_config()
    await event.edit(
        "**تمت استعادة الإعدادات من النسخة الاحتياطية بنجاح.**"
        if ok
        else "**لم يتم العثور على نسخة احتياطية صالحة بهذا المعرّف.**"
    )


@l313l.ar_cmd(pattern=r"حذف النسخة(?:\s+(\d+))?$")
async def _delete_backup_command(event):
    if not is_owner(event.sender_id):
        return
    message_id = (event.pattern_match.group(1) or "").strip() or None
    reply_message = await _replied_backup(event)
    if event.reply_to_msg_id and not reply_message:
        await event.edit("**الرد يجب أن يكون على ملف النسخة الاحتياطية في قناة السجلات.**")
        return
    count = await delete_backups(
        event.client,
        message_id=message_id,
        reply_message=reply_message,
    )
    await event.edit(
        f"**تم حذف {count} نسخة احتياطية من قناة السجلات.**"
        if count
        else "**لم يتم العثور على نسخة احتياطية صالحة بهذا المعرّف.**"
    )


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
