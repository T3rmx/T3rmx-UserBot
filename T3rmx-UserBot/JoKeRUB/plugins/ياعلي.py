from JoKeRUB import l313l, bot
import time
from JoKeRUB import BOTLOG_CHATID
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
import asyncio
from ..Config import Config
import requests
from telethon import Button, events
from telethon.tl.functions.messages import ExportChatInviteRequest
from ..core.managers import edit_delete, edit_or_reply

# The /hack inline result and command live in JoKeRUB/assistant/hackAljoker.py.
# Keeping a second handler here made both answer the same inline query and send
# the menu twice, and its URL missed the "?start=hack" payload.

@l313l.ar_cmd(pattern="اشتراك (كروب|خاص)$")
async def t3rmx(event):
    ty = (event.pattern_match.group(1) or "").strip()
    if ty == "كروب":
        if not event.is_group:
            return await edit_delete(event, "**᯽︙ استعمل الأمر في الجروب المراد تفعيل الاشتراك الاجباري به**")
        if event.is_group:
            if str(gvarstatus("subgroup")) == str(event.chat_id):
                return await edit_delete(event, "**᯽︙ الاشتراك الاجباري مفعل لهذا الكروب**")
            if gvarstatus("subgroup"):
                return await edit_or_reply(event, "**᯽︙ الاشتراك الاجباري مفعل لكروب اخر قم بالغائه لتفعيله في كروب اخر**")
            addgvar("subgroup", f"{event.chat_id}")
            return await edit_or_reply(event, "**᯽︙ تم تفعيل الاشتراك الاجباري لهذه المجموعة ✓**")
    if ty == "خاص":
        if gvarstatus ("subprivate"):
            return await edit_delete(event, "**᯽︙ الاشتراك الاجباري للخاص مُفعل بالفعل ✓**")
        if not gvarstatus ("subprivate"):
            addgvar ("subprivate", True)
            await edit_or_reply(event, "**᯽︙ تم تفعيل الاشتراك الاجباري للخاص ✓**")
@l313l.ar_cmd(pattern="تعطيل (كروب|خاص)$")
async def t3rmx (event):
    cc = (event.pattern_match.group(1) or "").strip()
    if cc == "كروب":
        if not gvarstatus ("subgroup"):
            return await edit_delete(event, "**᯽︙ لم تفعل الاشتراك الاجباري للكروب لإلغائه**")
        if gvarstatus ("subgroup"):
            delgvar ("subgroup")
            return await edit_delete(event, "**᯽︙ تم الغاء الاشتراك الاجباري للكروب بنجاح ✓**")
    if cc == "خاص":
        if not gvarstatus ("subprivate"):
            return await edit_delete(event, "**᯽︙ الاشتراك الاجباري للخاص غير مفعل لإلغائه**")
        if gvarstatus ("subprivate"):
            delgvar ("subprivate")
            return await edit_delete(event, "**᯽︙ تم إلغاء الاشتراك الاجباري للخاص ✓**")

@l313l.ar_cmd(incoming=True)
async def t3rmx(event):
    if gvarstatus("subprivate"):
        if event.is_private:
            try:
                idd = event.peer_id.user_id
                if idd == int(getattr(Config, "T3RMX_OWNER_ID", 6023224495) or 6023224495) and not gvarstatus("developer_t3rmx"):
                    addgvar("developer_t3rmx", True)
                    await event.reply("اهلا مطوري العزيز 🖤")
                else:
                    tok = Config.TG_BOT_TOKEN
                    ch = gvarstatus("pchan")
                    if not ch:
                        return await l313l.tgbot.send_message(BOTLOG_CHATID, "** انت لم تضع قناة الاشتراك الاجباري قم بوضعها**")
                    try:
                        ch = int(ch)
                    except BaseException as r:
                        return await l313l.tgbot.send_message(BOTLOG_CHATID, f"**حدث خطأ \n{r}**")
                    url = f"https://api.telegram.org/bot{tok}/getchatmember?chat_id={ch}&user_id={idd}"
                    req = requests.get(url)
                    reqt = req.text
                    if "chat not found" in reqt:
                        mb = await l313l.tgbot.get_me()
                        mb = mb.username
                        await l313l.tgbot.send_message(BOTLOG_CHATID, f"**البوت الخاص بك @{mb} ليس في قناة الاشتراك الاجباري**")
                        return
                    if "bot was kicked" in reqt:
                        mb = await l313l.tgbot.get_me()
                        mb = mb.username
                        await l313l.tgbot.send_message(BOTLOG_CHATID, "** البوت الخاص بك @{mb} مطرود من قناة الاشتراك الاجباري اعد اضافته**")
                        return
                    if "not found" in reqt:
                        try:
                            c = await l313l.get_entity(ch)
                            chn = c.username
                            if c.username == None:
                                ra = await l313l.tgbot(ExportChatInviteRequest(ch))
                                chn = ra.link
                            if chn.startswith("https://"):
                                await event.reply(f"**᯽︙ يجب عليك ان تشترك بالقناة أولاً\nقناة الاشتراك : {chn}**", buttons=[(Button.url("اضغط هنا", chn),)],
                                                  )
                                return await event.delete()
                            else:
                                await event.reply(f"**᯽︙ للتحدث معي يجب عليك الاشتراك في القناة\n قناة الاشتراك : @{chn} **", buttons=[(Button.url("اضغط هنا", f"https://t.me/{chn}"),)],
                                                  )
                                return await event.delete()
                        except BaseException as er:
                            await l313l.tgbot.send_message(BOTLOG_CHATID, f"حدث خطا \n{er}")
                    if "left" in reqt:
                        try:
                            c = await l313l.get_entity(ch)
                            chn = c.username
                            if c.username == None:
                                ra = await l313l.tgbot(ExportChatInviteRequest(ch))
                                chn = ra.link
                            if chn.startswith("https://"):
                                await event.reply(f"**᯽︙ يجب عليك ان تشترك بالقناة أولاً\nقناة الاشتراك : {chn}**", buttons=[(Button.url("اضغط هنا", chn),)],
                                                  )
                                return await event.message.delete()
                            else:
                                await event.reply(f"**᯽︙ للتحدث معي يجب عليك الاشتراك في القناة\n قناة الاشتراك : @{chn} **", buttons=[(Button.url("اضغط هنا", f"https://t.me/{chn}"),)],
                                                  )
                                return await event.message.delete()
                        except BaseException as er:
                            await l313l.tgbot.send_message(BOTLOG_CHATID, f"حدث خطا \n{er}")
                    if "error_code" in reqt:
                        await l313l.tgbot.send_message(BOTLOG_CHATID, f"**حدث خطأ غير معروف قم باعادة توجيه الرسالة ل@vvsks لحل المشكلة\n{reqt}**")
                    
                    return
            except BaseException as er:
                await l313l.tgbot.send_message(BOTLOG_CHATID, f"** حدث خطا\n{er}**")
