import asyncio

from JoKeRUB import l313l
from JoKeRUB.core.logger import logging

from ..Config import Config
from ..core.managers import edit_delete
from ..helpers.tools import media_type
from ..helpers.utils import _format
from ..sql_helper import no_log_pms_sql
from ..sql_helper.globals import addgvar, gvarstatus
from ..utils.logchannel import ensure_storage_group

LOGS = logging.getLogger(__name__)

plugin_category = "البوت"


class LOG_CHATS:
    def __init__(self):
        self.RECENT_USER = None
        self.NEWPM = None
        self.COUNT = 0


LOG_CHATS_ = LOG_CHATS()


def _created_note(created):
    if created:
        return "- تم إنشاء كروب التخزين تلقائياً ✓\n"
    return ""


@l313l.ar_cmd(incoming=True, func=lambda e: e.is_private, edited=False, forword=None)
async def monito_p_m_s(event):  # sourcery no-metrics
    if Config.PM_LOGGER_GROUP_ID == -100:
        return
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") == "false":
        return
    sender = await event.get_sender()
    if not sender.bot:
        chat = await event.get_chat()
        if not no_log_pms_sql.is_approved(chat.id) and chat.id != 777000:
            if LOG_CHATS_.RECENT_USER != chat.id:
                LOG_CHATS_.RECENT_USER = chat.id
                if LOG_CHATS_.NEWPM:
                    if LOG_CHATS_.COUNT > 1:
                        try:
                            await LOG_CHATS_.NEWPM.edit(
                                LOG_CHATS_.NEWPM.text.replace(
                                    " **📮┊رسـاله جـديده**", f"{LOG_CHATS_.COUNT} **رسـائل**"
                                )
                            )
                        except BaseException as er:
                            print(f"صار خطأ\n{er}")
                    else:
                        await event.client.send_message(
Config.PM_LOGGER_GROUP_ID,
                            LOG_CHATS_.NEWPM.text.replace(
                                " **📮┊رسـاله جـديده**", f"{LOG_CHATS_.COUNT} **رسـائل**"
                            )
                        )
                    LOG_CHATS_.COUNT = 0
                LOG_CHATS_.NEWPM = await event.client.send_message(
                    Config.PM_LOGGER_GROUP_ID,
                    f"**🛂┊المسـتخـدم :** {_format.mentionuser(sender.first_name , sender.id)} **- قام بـ إرسـال رسـالة جـديـده** \n**🎟┊الايـدي :** `{chat.id}`",
                )
            try:
                if event.message:
                    await event.client.forward_messages(
                        Config.PM_LOGGER_GROUP_ID, event.message, silent=True
                    )
                LOG_CHATS_.COUNT += 1
            except Exception as e:
                LOGS.warn(str(e))


@l313l.ar_cmd(incoming=True, func=lambda e: e.mentioned, edited=False, forword=None)
async def log_tagged_messages(event):
    hmm = await event.get_chat()
    from .afk import AFK_

    if gvarstatus("GRPLOG") and gvarstatus("GRPLOG") == "false":
        return
    if (
        (no_log_pms_sql.is_approved(hmm.id))
        or (Config.PM_LOGGER_GROUP_ID == -100)
        or ("on" in AFK_.USERAFK_ON)
        or (await event.get_sender() and (await event.get_sender()).bot)
    ):
        return
    full = None
    try:
        full = await event.client.get_entity(event.message.from_id)
    except Exception as e:
        LOGS.info(str(e))
    messaget = None
    try:
        messaget = await media_type(event)
    except BaseException:
        messaget = None
    resalt = f"#التــاكــات\n\n<b>⌔┊الكــروب : </b><code>{hmm.title}</code>"
    if full is not None:
        resalt += (
            f"\n\n<b>⌔┊المـرسـل : </b> {_format.htmlmentionuser(full.first_name , full.id)}"
        )
    if messaget is not None:
        resalt += f"\n\n<b>⌔┊رسـالـة ميـديـا : </b><code>{messaget}</code>"
    else:
        resalt += f"\n\n<b>⌔┊الرســالـه : </b>{event.message.message}"
    resalt += f"\n\n<b>⌔┊رابـط الرسـاله : </b><a href = 'https://t.me/c/{hmm.id}/{event.message.id}'> link</a>"
    if not event.is_private:
        await event.client.send_message(
            Config.PM_LOGGER_GROUP_ID,
            resalt,
            parse_mode="html",
            link_preview=False,
        )


@l313l.ar_cmd(
    pattern="خزن(?:\s|$)([\s\S]*)",
    command=("خزن", plugin_category),
    info={
        "header": "To log the replied message to bot log group so you can check later.",
        "الاسـتخـدام": [
            "{tr}خزن",
        ],
    },
)
async def log(log_text):
    "To log the replied message to the storage group"
    storage_id, created = await ensure_storage_group(log_text.client)
    if not storage_id:
        await log_text.edit("**⌔┊تعذر تجهيز كروب التخزين .. حاول مرة أخرى**")
        return
    note = _created_note(created)
    if log_text.reply_to_msg_id:
        reply_msg = await log_text.get_reply_message()
        await reply_msg.forward_to(storage_id)
    elif log_text.pattern_match.group(1):
        user = f"#التخــزين / ايـدي الدردشــه : {log_text.chat_id}\n\n"
        textx = user + log_text.pattern_match.group(1)
        await log_text.client.send_message(storage_id, textx)
    else:
        await log_text.edit(
            note + "**⌔┊بالــرد على اي رسـاله لحفظهـا في كـروب التخــزين**"
        )
        return
    await log_text.edit(note + "**⌔┊تـم الحفـظ في كـروب التخـزين .. بنجـاح ✓**")
    await asyncio.sleep(2)
    await log_text.delete()


@l313l.ar_cmd(
    pattern="تفعيل التخزين$",
    command=("تفعيل التخزين", plugin_category),
    info={
        "header": "To turn on logging of messages from that chat.",
        "الاسـتخـدام": [
            "{tr}log",
        ],
    },
)
async def set_no_log_p_m(event):
    "To turn on logging of messages from that chat."
    storage_id, created = await ensure_storage_group(event.client)
    if not storage_id:
        return await edit_delete(
            event, "**⌔┊تعذر تجهيز كروب التخزين .. حاول مرة أخرى**", 10
        )
    note = _created_note(created)
    chat = await event.get_chat()
    if no_log_pms_sql.is_approved(chat.id):
        no_log_pms_sql.disapprove(chat.id)
        await edit_delete(
            event, note + "**⌔┊تـم تفعيـل التخـزين لهـذه الدردشـه .. بنجـاح ✓**", 5
        )
    else:
        await edit_delete(
            event, note + "**⌔┊التخـزين مفعّل لهـذه الدردشـه بالفعـل ✓**", 5
        )


@l313l.ar_cmd(
    pattern="تعطيل التخزين$",
    command=("تعطيل التخزين", plugin_category),
    info={
        "header": "To turn off logging of messages from that chat.",
        "الاسـتخـدام": [
            "{tr}nolog",
        ],
    },
)
async def set_no_log_p_m(event):
    "To turn off logging of messages from that chat."
    storage_id, created = await ensure_storage_group(event.client)
    if not storage_id:
        return await edit_delete(
            event, "**⌔┊تعذر تجهيز كروب التخزين .. حاول مرة أخرى**", 10
        )
    note = _created_note(created)
    chat = await event.get_chat()
    if not no_log_pms_sql.is_approved(chat.id):
        no_log_pms_sql.approve(chat.id)
        await edit_delete(
            event, note + "**⌔┊تـم تعطيـل التخـزين لهـذه الدردشـه .. بنجـاح ✓**", 5
        )
    else:
        await edit_delete(
            event, note + "**⌔┊التخـزين معطّل لهـذه الدردشـه بالفعـل ✓**", 5
        )


@l313l.ar_cmd(
    pattern="تخزين الخاص (تفعيل|تعطيل)$",
    command=("تخزين الخاص", plugin_category),
    info={
        "header": "To turn on or turn off logging of Private messages in pmlogger group.",
        "الاسـتخـدام": [
            "{tr}pmlog on",
            "{tr}pmlog off",
        ],
    },
)
async def set_pmlog(event):
    "To turn on or turn off logging of Private messages"
    storage_id, created = await ensure_storage_group(event.client)
    if not storage_id:
        return await edit_delete(
            event, "**⌔┊تعذر تجهيز كروب التخزين .. حاول مرة أخرى**", 10
        )
    note = _created_note(created)
    input_str = event.pattern_match.group(1)
    if input_str == "تعطيل":
        h_type = False
    elif input_str == "تفعيل":
        h_type = True
    PMLOG = not gvarstatus("PMLOG") or gvarstatus("PMLOG") != "false"
    if PMLOG:
        if h_type:
            await event.edit(note + "**- تخزين الخاص بالفعـل ممكـن ✓**")
        else:
            addgvar("PMLOG", h_type)
            await event.edit(note + "**- تـم تعطيـل تخـزين رسـائل الخـاص .. بنجـاح✓**")
    elif h_type:
        addgvar("PMLOG", h_type)
        await event.edit(note + "**- تـم تفعيـل تخـزين رسـائل الخـاص .. بنجـاح✓**")
    else:
        await event.edit(note + "**- تخزين الخاص بالفعـل معطـل ✓**")


@l313l.ar_cmd(
    pattern="تخزين الكروبات (تفعيل|تعطيل)$",
    command=("تخزين الكروبات", plugin_category),
    info={
        "header": "To turn on or turn off group tags logging in pmlogger group.",
        "الاسـتخـدام": [
            "{tr}grplog on",
            "{tr}grplog off",
        ],
    },
)
async def set_grplog(event):
    "To turn on or turn off group tags logging"
    storage_id, created = await ensure_storage_group(event.client)
    if not storage_id:
        return await edit_delete(
            event, "**⌔┊تعذر تجهيز كروب التخزين .. حاول مرة أخرى**", 10
        )
    note = _created_note(created)
    input_str = event.pattern_match.group(1)
    if input_str == "تعطيل":
        h_type = False
    elif input_str == "تفعيل":
        h_type = True
    GRPLOG = not gvarstatus("GRPLOG") or gvarstatus("GRPLOG") != "false"
    if GRPLOG:
        if h_type:
            await event.edit(note + "**- تخزين الكـروبات بالفعـل ممكـن ✓**")
        else:
            addgvar("GRPLOG", h_type)
            await event.edit(note + "**- تـم تعطيـل تخـزين تاكـات الكـروبات .. بنجـاح✓**")
    elif h_type:
        addgvar("GRPLOG", h_type)
        await event.edit(note + "**- تـم تفعيـل تخـزين تاكـات الكـروبات .. بنجـاح✓**")
    else:
        await event.edit(note + "**- تخزين الكـروبات بالفعـل معطـل ✓**")
