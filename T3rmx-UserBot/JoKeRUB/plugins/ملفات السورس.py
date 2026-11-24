from JoKeRUB import l313l

try:
    import pkg_resources
except Exception:  # optional legacy dependency
    pkg_resources = None
from ..core.auth import is_owner
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _catutils, parse_pre, yaml_format
from ..Config import Config
import json
import requests
import os
from telethon import events 
plugin_category = "tools"


@l313l.ar_cmd(pattern="المكاتب")
async def t3rmx(event):
    if pkg_resources is None:
        try:
            from importlib import metadata as importlib_metadata
            installed_packages_list = sorted(
                f"{dist.metadata['Name']}=={dist.version}" for dist in importlib_metadata.distributions()
            )
        except Exception as e:
            return await edit_or_reply(event, f"**تعذر عرض المكاتب المثبتة:** `{e}`")
    else:
        installed_packages = pkg_resources.working_set
        installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
    msg = "**قائمة المكاتب المثبته**\n"
    for i in installed_packages_list:
        msg += f"{i}\n"
    msg += "**T3rmx UserBot**"
    await edit_or_reply(event, msg)

@l313l.ar_cmd(
    pattern="الملفات$",
    command=("الملفات", plugin_category),
    info={
        "header": "To list all plugins in JoKeRUB.",
        "usage": "{tr}plugins",
    },
)
async def _(event):
    "To list all plugins in JoKeRUB"
    cmd = "ls JoKeRUB/plugins"
    o = (await _catutils.runcmd(cmd))[0]
    OUTPUT = f"**[T3rmx UserBot](tg://need_update_for_some_feature/) الملفات:**\n{o}"
    await edit_or_reply(event, OUTPUT)


@l313l.ar_cmd(
    pattern="فاراتي$",
    command=("فاراتي", plugin_category),
    info={
        "header": "To list all environment values in JoKeRUB.",
        "description": "to show all heroku vars/Config values in your JoKeRUB",
        "usage": "{tr}env",
    },
)
async def _(event):
    "To show all config values in JoKeRUB"
    if not is_owner(getattr(event, "sender_id", None)):
        return await edit_or_reply(event, "**هذا الأمر مخصص لمالك البوت فقط.**")
    cmd = "env"
    o = (await _catutils.runcmd(cmd))[0]
    OUTPUT = (
        f"**[T3rmx UserBot](tg://need_update_for_some_feature/) قائمة الفارات:**\n\n\n{o}\n\n**انتبه: قد تحتوي هذه البيانات على معلومات حساسة، لا تشاركها مع غير الموثوقين.**"
    )
    await edit_or_reply(event, "**تم ارسال المعلومات في الرسائل المحفوضة \nانتبه من الاشخاص الي يطلبون منك كتابة هذا الامر يريد ان يخترقك!**")
    await l313l.send_message("me", OUTPUT)

@l313l.ar_cmd(
    pattern="متى$",
    command=("متى", plugin_category),
    info={
        "header": "To get date and time of message when it posted.",
        "usage": "{tr}when <reply>",
    },
)
async def _(event):
    "To get date and time of message when it posted."
    reply = await event.get_reply_message()
    if reply:
        try:
            result = reply.fwd_from.date
        except Exception:
            result = reply.date
    else:
        result = event.date
    await edit_or_reply(
        event, f"**᯽︙ نـشـرت هـذه الـرسالة فـي  :** `{yaml_format(result)}`"
    )
@l313l.ar_cmd(pattern="رابط مباشر")
async def upload_t3rmx(event):
    r = await event.get_reply_message()
    if r is None:
        return await edit_delete(event, "**᯽︙قم بالرد على ملف لرفعهُ**")
    if r.media is None:
        return await edit_delete(event, "**᯽︙قم بالرد على ملف لرفعهُ**")
    file = await event.client.download_media(r, Config.TEMP_DIR)
    await edit_or_reply(event, "**᯽︙ يُجري عملية الرفع . .**")
    payload = {}
    image = {"file": open(file, "rb")}
    response = requests.request("POST", "https://api.anonfiles.com/upload", files=image, data = payload)
    res = response.json()
    if res["status"] == False:
        er = res["error"]["message"]
        return await edit_delete(event, f"حدث خطأ عند رفع الملف\n{er}") 
    url = res["data"]["file"]["url"]["short"]
    size = res["data"]["file"]["metadata"]["size"]["readable"]
    await edit_or_reply(event, f"**تم رفع الملف ✓**\n**᯽︙ الرابط:** {url}\n**᯽︙الحجم:** {size}")
    os.remove(file)