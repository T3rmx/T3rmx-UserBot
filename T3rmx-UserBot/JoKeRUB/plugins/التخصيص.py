import re
import os
import requests
from JoKeRUB import l313l
from JoKeRUB.core.logger import logging
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG_CHATID


LOGS = logging.getLogger(__name__)
cmdhd = Config.COMMAND_HAND_LER

# Aliases accepted by `.جلب` / `.اضف` / `.حذف`. Keeping the list explicit stops
# these commands from swallowing unrelated commands such as `.حذف النسخة`.
_CUSTOM_VARS = {
    "كليشة الحماية": "pmpermit_txt",
    "كليشة الحمايه": "pmpermit_txt",
    "كليشه الحماية": "pmpermit_txt",
    "كليشه الحمايه": "pmpermit_txt",
    "PM_TEXT": "pmpermit_txt",
    "pmpermit_txt": "pmpermit_txt",
    "اشتراك الخاص": "pchan",
    "اشتراك خاص": "pchan",
    "pchan": "pchan",
    "اشتراك كروب": "gchan",
    "اشتراك الكروب": "gchan",
    "gchan": "gchan",
    "امر النشر": "MUKRR_ET",
    "امر نشر": "MUKRR_ET",
    "MUKRR_ET": "MUKRR_ET",
    "زخرفة الارقام": "JP_FN",
    "زخرفه الارقام": "JP_FN",
    "JP_FN": "JP_FN",
    "البايو": "DEFAULT_BIO",
    "بايو": "DEFAULT_BIO",
    "DEFAULT_BIO": "DEFAULT_BIO",
    "رمز الاسم": "TIME_JEP",
    "علامة الاسم": "TIME_JEP",
    "TIME_JEP": "TIME_JEP",
    "كليشة الفحص": "ALIVE_TEMPLATE",
    "كليشه الفحص": "ALIVE_TEMPLATE",
    "كليشة فحص": "ALIVE_TEMPLATE",
    "كليشه فحص": "ALIVE_TEMPLATE",
    "ALIVE_TEMPLATE": "ALIVE_TEMPLATE",
    "كليشة الحظر": "pmblock",
    "كليشه الحظر": "pmblock",
    "PM_BLOCK": "pmblock",
    "pmblock": "pmblock",
    "كليشة البوت": "START_TEXT",
    "كليشه البوت": "START_TEXT",
    "START_TEXT": "START_TEXT",
    "ايموجي الفحص": "ALIVE_EMOJI",
    "ALIVE_EMOJI": "ALIVE_EMOJI",
    "نص الفحص": "ALIVE_TEXT",
    "ALIVE_TEXT": "ALIVE_TEXT",
    "عدد التحذيرات": "MAX_FLOOD_IN_PMS",
    "MAX_FLOOD_IN_PMS": "MAX_FLOOD_IN_PMS",
    "لون الصوره الوقتيه": "digitalpiccolor",
    "لون صوره وقتيه": "digitalpiccolor",
    "لون الوقتي": "digitalpiccolor",
    "لون وقتي": "digitalpiccolor",
    "لون": "digitalpiccolor",
    "digitalpiccolor": "digitalpiccolor",
    "التخزين": "PM_LOGGER_GROUP_ID",
    "تخزين": "PM_LOGGER_GROUP_ID",
    "PM_LOGGER_GROUP_ID": "PM_LOGGER_GROUP_ID",
    "كليشة الخاص": "aljoker_message",
    "كليشه الخاص": "aljoker_message",
    "aljoker_message": "aljoker_message",
    "اشعارات": "PRIVATE_GROUP_BOT_API_ID",
    "الاشعارات": "PRIVATE_GROUP_BOT_API_ID",
    "PRIVATE_GROUP_BOT_API_ID": "PRIVATE_GROUP_BOT_API_ID",
    "صورة الحماية": "pmpermit_pic",
    "صورة الحمايه": "pmpermit_pic",
    "صوره الحماية": "pmpermit_pic",
    "صوره الحمايه": "pmpermit_pic",
    "PM_PIC": "pmpermit_pic",
    "pmpermit_pic": "pmpermit_pic",
    "صورة الفحص": "ALIVE_PIC",
    "صوره الفحص": "ALIVE_PIC",
    "ALIVE_PIC": "ALIVE_PIC",
    "صورة البنك": "PING_PIC",
    "صوره البنك": "PING_PIC",
    "PING_PIC": "PING_PIC",
}
_VAR_PATTERN = "(" + "|".join(
    re.escape(alias) for alias in sorted(_CUSTOM_VARS, key=lambda a: (-len(a), a))
) + ")$"


@l313l.ar_cmd(pattern=f"جلب {_VAR_PATTERN}")
async def getvar(event):
    alias = event.pattern_match.group(1)
    value = gvarstatus(_CUSTOM_VARS[alias])
    if value is None:
        return await edit_delete(
            event, "**⎙ :: عزيزي المستخدم انت لم تقوم باضافه هذا الفار اصلا**"
        )
    await edit_or_reply(event, str(value))


@l313l.ar_cmd(pattern=f"اضف {_VAR_PATTERN}")
async def custom_HuRe(event):
    alias = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    text = reply.text if reply else None
    if text is None:
        return await edit_delete(
            event, "**⌔∮ يجب عليك الرد على النص او الرابط حسب الفار الذي تضيفه **"
        )
    key = _CUSTOM_VARS[alias]
    addgvar(key, text)
    await edit_or_reply(event, f"**₰ تم بنجاح تحديث فار {alias} 𓆰،**")
    if BOTLOG_CHATID:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#اضف_فار\n**{alias}** تم تحديثه بنجاح في قاعده البيانات.",
        )


@l313l.ar_cmd(pattern=f"حذف {_VAR_PATTERN}")
async def custom_HuRe_delete(event):
    alias = event.pattern_match.group(1)
    key = _CUSTOM_VARS[alias]
    if gvarstatus(key) is None:
        return await edit_delete(
            event, "**⎙ :: عزيزي المستخدم انت لم تقوم باضافه هذا الفار اصلا**"
        )
    delgvar(key)
    await edit_or_reply(
        event, "₰ هذا الفار تم حذفه بنجاح وارجاع قيمته الى القيمه الاصلية ✅"
    )
    if BOTLOG_CHATID:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#حذف_فار\n**فار {alias}** تم حذفه من قاعده البيانات.",
        )


@l313l.ar_cmd(pattern="اضف صورة (الفحص|فحص) ?(.*)")
async def alive_aljoker(event):
    reply = await event.get_reply_message()
    if reply and reply.media:
        input_str = event.pattern_match.group(1)
        jokevent = await event.edit("` ⌔︙ جـار رفع الـصورة الى أمر الفحص `")
        try:
            hussein = await event.client.download_media(reply)
            if hussein.endswith((".webp")):
                resize_image(hussein)
            with open(hussein, "rb") as file:
                response = requests.post(
                    "https://uguu.se/upload.php",
                    files={"files[]": file},
                )
            
            if response.status_code == 200 and response.json().get("success"):
                url = response.json()["files"][0]["url"]
                addgvar("ALIVE_PIC", url)
                await jokevent.edit(f"** ⌔︙  تم اضافة الصورة الى الفحص ✓ **")
            else:
                await jokevent.edit(f"** ⌔︙حدث خطأ في رفع الصورة: **\n`{response.json()}`")

            os.remove(hussein)
        except Exception as exc:
            await event.edit(f"** ⌔︙خـطأ : **\n`{exc}`")
            if os.path.exists(hussein):
                os.remove(hussein)
    else:
        await event.edit("**᯽︙ يُرجى الرد على الصورة لطفًا**")
@l313l.ar_cmd(pattern="اضف صورة (البنك|بنك) ?(.*)")
async def ping_aljoker(event):
    reply = await event.get_reply_message()
    if reply and reply.media:
        input_str = event.pattern_match.group(1)
        jokevent = await event.edit("` ⌔︙ جـار رفع الـصورة الى أمر البنك `")
        try:
            hussein = await event.client.download_media(reply)
            if hussein.endswith((".webp")):
                resize_image(hussein)
            with open(hussein, "rb") as file:
                response = requests.post(
                    "https://uguu.se/upload.php",
                    files={"files[]": file},
                )
            
            if response.status_code == 200 and response.json().get("success"):
                url = response.json()["files"][0]["url"]
                addgvar("PING_PIC", url)
                await jokevent.edit(f"** ⌔︙  تم اضافة الصورة الى البنك ✓ **")
            else:
                await jokevent.edit(f"** ⌔︙حدث خطأ في رفع الصورة: **\n`{response.json()}`")

            os.remove(hussein)
        except Exception as exc:
            await event.edit(f"** ⌔︙خـطأ : **\n`{exc}`")
            if os.path.exists(hussein):
                os.remove(hussein)
    else:
        await event.edit("**᯽︙ يُرجى الرد على الصورة لطفًا**")
@l313l.ar_cmd(pattern="اضف صورة (الحماية|الحمايه|حماية|حمايه) ?(.*)")
async def secu_aljoker(event):
    reply = await event.get_reply_message()
    if reply and reply.media:
        input_str = event.pattern_match.group(1)
        jokevent = await event.edit("` ⌔︙ جـار رفع الـصورة الى أمر الحماية `")
        try:
            hussein = await event.client.download_media(reply)
            if hussein.endswith((".webp")):
                resize_image(hussein)
            with open(hussein, "rb") as file:
                response = requests.post(
                    "https://uguu.se/upload.php",
                    files={"files[]": file},
                )
            
            if response.status_code == 200 and response.json().get("success"):
                url = response.json()["files"][0]["url"]
                addgvar("pmpermit_pic", url)
                await jokevent.edit(f"** ⌔︙  تم اضافة الصورة الى الحماية ✓ **")
            else:
                await jokevent.edit(f"** ⌔︙حدث خطأ في رفع الصورة: **\n`{response.json()}`")

            os.remove(hussein)
        except Exception as exc:
            await event.edit(f"** ⌔︙خـطأ : **\n`{exc}`")
            if os.path.exists(hussein):
                os.remove(hussein)
    else:
        await event.edit("**᯽︙ يُرجى الرد على الصورة لطفًا**")
@l313l.ar_cmd(pattern="اضف صورة (الخاص|خاص) ?(.*)")
async def khas_aljoker(event):
    reply = await event.get_reply_message()
    if reply and reply.media:
        input_str = event.pattern_match.group(1)
        jokevent = await event.edit("` ⌔︙ جـار رفع الـصورة الى أمر الخاص `")
        try:
            hussein = await event.client.download_media(reply)
            if hussein.endswith((".webp")):
                resize_image(hussein)
            with open(hussein, "rb") as file:
                response = requests.post(
                    "https://uguu.se/upload.php",
                    files={"files[]": file},
                )
            
            if response.status_code == 200 and response.json().get("success"):
                url = response.json()["files"][0]["url"]
                addgvar("aljoker_url", url)
                await jokevent.edit(f"** ⌔︙  تم اضافة الصورة الى الخاص ✓ **")
            else:
                await jokevent.edit(f"** ⌔︙حدث خطأ في رفع الصورة: **\n`{response.json()}`")

            os.remove(hussein)
        except Exception as exc:
            await event.edit(f"** ⌔︙خـطأ : **\n`{exc}`")
            if os.path.exists(hussein):
                os.remove(hussein)
    else:
        await event.edit("**᯽︙ يُرجى الرد على الصورة لطفًا**")