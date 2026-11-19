import os
from telethon import functions 
import subprocess
from JoKeRUB.helpers.functions.functions import translate
from datetime import datetime
try:
    from ALJoker import get_string
except Exception:
    def get_string(key):
        return ""



try:
    from gtts import gTTS
except Exception:
    gTTS = None


from JoKeRUB import l313l


from ..core.managers import edit_delete, edit_or_reply

from . import deEmojify, reply_id


@l313l.ar_cmd(pattern="test(?:\s|$)([\s\S]*)")
async def reda(event):
    try:
        tr = translate("انا عراقي", lang_tgt="fa").replace("\ N", "\n")
    except Exception:
        tr = ""
    await edit_or_reply(event, tr or "**تعذر الحصول على ترجمة حالياً**")
    try:
        result = await l313l(functions.users.GetFullUserRequest(
            id='earthlink_telecommunications'
        ))
        await event.reply(result.stringify())
    except Exception:
        await event.reply("**تعذر جلب معلومات المستخدم حالياً**")



@l313l.ar_cmd(pattern="تكلم(?:\s|$)([\s\S]*)")

async def _(event):

    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    start = datetime.now()
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str

    elif "|" in input_str:
        lan, text = input_str.split("|", 1)
        text = text.strip()
        lan = lan.strip()
    else:
        await edit_or_reply(event, "- هذا نص غير صحيح. الاستخدام: `.تكلم <lang>|<text>` أو بالرد على رسالة مع كود اللغة")
        return

    status_event = await edit_or_reply(event, "⌔∮ جـار التسجيل انتـظر قليلا")

    if gTTS is None:
        return await edit_delete(status_event, "**ميزة تحويل النص الى صوت غير متاحة حالياً (حزمة gtts غير مثبتة).**")

    if not os.path.isdir("./temp/"):
        os.makedirs("./temp/")

    required_file_name = "./temp/" + "voice.ogg"

    try:
        tts = gTTS(text, lang=lan)
        tts.save(required_file_name)
        command_to_execute = [
            "ffmpeg",
            "-i",
            required_file_name,
            "-map",
            "0:a",
            "-codec:a",
            "libopus",
            "-b:a",
            "100k",
            "-vbr",
            "on",
            required_file_name + ".opus",
        ]

        try:
            subprocess.check_output(command_to_execute, stderr=subprocess.STDOUT)
        except (subprocess.CalledProcessError, NameError, FileNotFoundError) as exc:
            await status_event.edit(str(exc))
            return
        else:
            os.remove(required_file_name)
            required_file_name = required_file_name + ".opus"

        end = datetime.now()
        ms = (end - start).seconds

        await event.client.send_file(
            event.chat_id,
            required_file_name,
            reply_to=event.message.reply_to_msg_id,
            allow_cache=False,
            voice_note=True,
        )

        os.remove(required_file_name)

        await edit_delete(
            status_event,
            "تحويل النص {} الى مقطع صوتي في {} ثواني ".format(text[0:20], ms),
        )

    except Exception as e:
        await edit_or_reply(status_event, f"خطأ:\n{e}")
