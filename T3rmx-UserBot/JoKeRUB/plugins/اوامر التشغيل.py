import asyncio
import sys
from asyncio.exceptions import CancelledError
from time import sleep

from telethon import events

from JoKeRUB import l313l

from ..core.auth import is_owner
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper.global_collection import (
    add_to_collectionlist,
    del_keyword_collectionlist,
    get_collectionlist_items,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID, HEROKU_APP

LOGS = logging.getLogger(__name__)
plugin_category = "tools"

@l313l.ar_cmd(
    pattern="اعادة تشغيل$",
    command=("اعادة تشغيل", plugin_category),
    info={
        "header": "Restarts the bot (owner only).",
        "usage": "{tr}اعادة تشغيل",
    },
    disable_errors=True,
)
async def _(event):
    "Restarts the bot !!"
    if not is_owner(getattr(event, "sender_id", None)):
        return await edit_or_reply(event, "**هذا الأمر مخصص لمالك البوت فقط.**")
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "**T3rmx ↻** \n**᯽︙ تم طلب اعادة تشغيل السورس ✅ ↻**")
    lMl10l = await edit_or_reply(event, "᯽︙ سيتم اعادة التشغيل انتظر ")
    await event.edit("0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒")
    await asyncio.sleep(2)
    await event.edit("4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒")
    await asyncio.sleep(2)
    await event.edit("8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒")
    await asyncio.sleep(2)
    await event.edit("20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒")
    await asyncio.sleep(2)
    await event.edit("36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒")
    await asyncio.sleep(2)
    await event.edit("52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒")
    await asyncio.sleep(2)
    await event.edit("84%\n█████████████████████▒▒▒▒")
    await asyncio.sleep(2)
    await event.edit("100%\n████████████████████████")
    await asyncio.sleep(2)
    await event.edit("**᯽︙ تم اعادة تشغيل بنجاح ✓ \nانتظر 2-5 دقائق**")
    await asyncio.sleep(2)
    try:
        ulist = get_collectionlist_items()
        for i in ulist:
            if i == "restart_update":
                del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
    try:
        add_to_collectionlist("restart_update", [lMl10l.chat_id, lMl10l.id])
    except Exception as e:
        LOGS.error(e)
    try:
        delgvar("ipaddress")
        await l313l.disconnect()
    except CancelledError:
        pass
    except Exception as e:
        LOGS.error(e)


@l313l.ar_cmd(
    pattern="اطفاء$",
    command=("اطفاء", plugin_category),
    info={
        "header": "Shutdowns the bot (owner only).",
        "description": "Stops the running process. On managed platforms, restart must be done from the platform dashboard.",
        "usage": "{tr}اطفاء",
    },
)
async def _(event):
    "Shutdowns the bot"
    if not is_owner(getattr(event, "sender_id", None)):
        return await edit_or_reply(event, "**هذا الأمر مخصص لمالك البوت فقط.**")
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "**᯽︙ إيقاف التشغيـل ✕ **\n**᯽︙ تـم طلب إيقـاف تشغيـل البـوت ✓**")
    await edit_or_reply(event, "**᯽︙ جـاري إيقـاف تشغيـل البـوت الآن ..**\n**أعد تشغيله يدوياً من بيئة النشر عند الحاجة.**")
    if HEROKU_APP is not None:
        try:
            HEROKU_APP.process_formation()["worker"].scale(0)
            return
        except Exception as e:
            LOGS.warning(f"Heroku shutdown request failed, exiting process instead: {e}")
    sys.exit(0)

@l313l.ar_cmd(
    pattern="التحديثات (تشغيل|ايقاف)$",
    command=("التحديثات", plugin_category),
    info={
        "header": "᯽︙ لتحديـث الدردشـة بعـد إعـادة التشغيـل  أو إعـادة التحميـل  ",
        "description": "⌔︙سيتـم إرسـال بنـك cmds ڪـرد على الرسالـة السابقـة الأخيـرة لـ (إعادة تشغيل/إعادة تحميل/تحديث cmds) 💡.",
        "usage": [
            "{tr}التحديثات <تشغيل/ايقاف",
        ],
    },
)
async def set_pmlog(event):
    "᯽︙ لتحديـث الدردشـة بعـد إعـادة التشغيـل  أو إعـادة التحميـل  "
    if not is_owner(getattr(event, "sender_id", None)):
        return await edit_or_reply(event, "**هذا الأمر مخصص لمالك البوت فقط.**")
    input_str = event.pattern_match.group(1)
    if input_str == "ايقاف":
        if gvarstatus("restartupdate") is None:
            return await edit_delete(event, "**᯽︙ تـم تعطيـل التـحديـثات بالفعـل ❗️**")
        delgvar("restartupdate")
        return await edit_or_reply(event, "**⌔︙تـم تعطيـل التـحديـثات بنجـاح ✓**")
    if gvarstatus("restartupdate") is None:
        addgvar("restartupdate", "turn-oned")
        return await edit_or_reply(event, "**⌔︙تـم تشغيل التـحديـثات بنجـاح ✓**")
    await edit_delete(event, "**᯽︙ تـم تشغيل التـحديـثات بالفعـل ❗️**")
@l313l.on(events.NewMessage(incoming=True))
async def _owner_remote_restart(event):
    if not event.reply_to or not is_owner(getattr(event, "sender_id", None)):
        return
    reply_msg = await event.get_reply_message()
    try:
        owner_id = getattr(reply_msg.from_id, "user_id", reply_msg.from_id)
    except Exception:
        owner_id = getattr(reply_msg, "sender_id", None)
    if owner_id != l313l.uid:
        return
    if (event.message.message or "").strip() != "اعادة تشغيل":
        return
    lMl10l = await event.reply("**᯽︙ سيتم اعادة التشغيل بأمر المالك **")
    try:
        ulist = get_collectionlist_items()
        for i in ulist:
            if i == "restart_update":
                del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
    try:
        add_to_collectionlist("restart_update", [lMl10l.chat_id, lMl10l.id])
    except Exception as e:
        LOGS.error(e)
    try:
        delgvar("ipaddress")
        await l313l.disconnect()
    except CancelledError:
        pass
    except Exception as e:
        LOGS.error(e)


@l313l.on(events.NewMessage(incoming=True))
async def _owner_remote_shutdown(event):
    if not event.reply_to or not is_owner(getattr(event, "sender_id", None)):
        return
    reply_msg = await event.get_reply_message()
    try:
        owner_id = getattr(reply_msg.from_id, "user_id", reply_msg.from_id)
    except Exception:
        owner_id = getattr(reply_msg, "sender_id", None)
    if owner_id != l313l.uid:
        return
    if (event.message.message or "").strip() != "اطفاء":
        return
    await event.reply("**᯽︙ تم استلام أمر الإيقاف من المالك.**")
    if HEROKU_APP is not None:
        try:
            HEROKU_APP.process_formation()["worker"].scale(0)
            return
        except Exception as e:
            LOGS.warning(f"Heroku shutdown request failed, exiting process instead: {e}")
    sys.exit(0)
