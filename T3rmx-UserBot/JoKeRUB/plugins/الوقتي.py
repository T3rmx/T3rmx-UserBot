
from ..sql_helper.group import auto_g, del_auto_g, get_auto_g
try:
    import webcolors
except Exception:
    webcolors = None
import asyncio
import base64
import os
import shutil
import time
from datetime import datetime
from telethon import events
try:
    from ALJoker import get_string
except Exception:
    def get_string(key):
        return ""
from telethon.errors import ChatAdminRequiredError
from PIL import Image, ImageDraw, ImageFont

try:
    from pySmartDL import SmartDL
except Exception:
    SmartDL = None

from telethon.errors import FloodWaitError, ChannelInvalidError
from telethon.tl import functions
from telethon import types
from JoKeRUB import BOTLOG_CHATID
from ..Config import Config
from ..helpers.utils import _format
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import AUTONAME, DEFAULT_GROUP, DEFAULT_BIO, edit_delete, l313l, logging

try:
    from colour import Color
except Exception:
    Color = None

plugin_category = "tools"
DEFAULTUSERBIO = DEFAULT_BIO or "﴿ لا تَحزَن إِنَّ اللَّهَ مَعَنا ﴾ "
DEFAULTUSERGRO = DEFAULT_GROUP or ""
DEFAULTUSER = AUTONAME or ""
LOGS = logging.getLogger(__name__)

FONT_FILE_TO_USE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

autopic_path = os.path.join(os.getcwd(), "JoKeRUB", "original_pic.png")
digitalpic_path = os.path.join(os.getcwd(), "JoKeRUB", "digital_pic.png")
digital_group_pic_path = os.path.join(os.getcwd(), "JoKeRUB", "digital_group_pic.png")
autophoto_path = os.path.join(os.getcwd(), "JoKeRUB", "photo_pfp.png")
auto_group_photo_path = os.path.join(os.getcwd(), "JoKeRUB", "photo_pfp.png")

digitalpfp = Config.DIGITAL_PIC or "https://telegra.ph/file/63a826d5e5f0003e006a0.jpg"
digitalgrouppfp = Config.DIGITAL_GROUP_PIC or "https://telegra.ph/file/63a826d5e5f0003e006a0.jpg"
jep = Config.DEFAULT_PIC or "JoKeRUB/helpers/styles/PaybAck.ttf"
normzltext = "1234567890"
namew8t = Config.NAME_ET or "اسم وقتي"
biow8t = Config.BIO_ET or "بايو وقتي"
phow8t = Config.PHOTO_ET or "الصورة الوقتية"

def _color_to_rgb(color, default=(255, 255, 255)):
    color = str(color or "").strip()
    if not color:
        return default
    try:
        if Color is not None:
            c = Color(color)
            r, g, b = c.red * 255, c.green * 255, c.blue * 255
            return (int(round(r)), int(round(g)), int(round(b)))
    except Exception:
        pass
    try:
        if webcolors is not None:
            return tuple(webcolors.name_to_rgb(color))
    except Exception:
        pass
    if color.startswith("#"):
        h = color.lstrip("#")
        try:
            if len(h) == 3:
                h = "".join(ch * 2 for ch in h)
            if len(h) == 6:
                return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        except Exception:
            pass
    return default


def check_color(color):
    try:
        color = str(color).replace(" ", "")
        if not color:
            return False
        if Color is not None:
            try:
                Color(color)
                return True
            except Exception:
                pass
        if webcolors is not None:
            try:
                webcolors.name_to_rgb(color)
                return True
            except Exception:
                pass
        if color.startswith("#"):
            h = color.lstrip("#")
            return len(h) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in h)
        return False
    except Exception:
        return False

async def digitalpicloop():
    colorco = gvarstatus("digitalpiccolor") or Config.DIGITAL_PIC_COLOR or "white"
    if not check_color(colorco):
        colorco = "white"
    colo = _color_to_rgb(colorco, default=(255, 255, 255))
    DIGITALPICSTART = gvarstatus("digitalpic") == "true"
    i = 0
    while DIGITALPICSTART:
        try:
            if not os.path.exists(digitalpic_path):
                if SmartDL is None:
                    LOGS.warning("digitalpicloop disabled: pySmartDL is not installed")
                    return
                downloader = SmartDL(digitalpfp, digitalpic_path, progress_bar=False)
                downloader.start(blocking=False)
                while not downloader.isFinished():
                    await asyncio.sleep(0.5)
            shutil.copy(digitalpic_path, autophoto_path)
            Image.open(autophoto_path)
            current_time = datetime.now().strftime("%I:%M")
            img = Image.open(autophoto_path)
            drawn_text = ImageDraw.Draw(img)
            try:
                fnt = ImageFont.truetype(jep, 65)
            except Exception:
                fnt = ImageFont.load_default()
            drawn_text.text((200, 200), current_time, font=fnt, fill=colo)
            img.save(autophoto_path)
            try:
                if i > 0:
                    await l313l(
                        functions.photos.DeletePhotosRequest(
                            await l313l.get_profile_photos("me", limit=1)
                        )
                    )
                i += 1
                await l313l(functions.photos.UploadProfilePhotoRequest(file=await l313l.upload_file(autophoto_path)))
            finally:
                try:
                    os.remove(autophoto_path)
                except Exception:
                    pass
            await asyncio.sleep(getattr(Config, "CHANGE_TIME", 60) or 60)
        except Exception as e:
            LOGS.debug("digitalpicloop stopped: %s", e)
            return
        DIGITALPICSTART = gvarstatus("digitalpic") == "true"

async def digitalgrouppicloop():
    "2KfZhNij2YPZiNin2K8g2KrZj9mG2LPYrtiMINmE2YPZhiDYp9mE2YHZg9ixINmI2KfZhNmH2YjZitipINmE2Kcg2KrZj9mG2LPYri4g2YPZhiDZhdi32YjYsdmL2Kcg2YrYtdmG2LnYjCDZhNinINmF2KzYsdivINi02K7YtSDZiti62YrZkdixINij2LPZhdin2KEuIOKAlCBUM3JteA=="

    dgp = gvarstatus("digitalgrouppic")
    colorco = gvarstatus("digitalgrouppiccolor") or Config.DIGITAL_PIC_COLOR or "white"
    if not check_color(colorco):
        colorco = "white"
    colo = _color_to_rgb(colorco, default=(255, 255, 255))
    i = 0
    DIGITALPICSTART = gvarstatus("digitalgrouppic") != None
    while DIGITALPICSTART:
        try:
            if not os.path.exists(digital_group_pic_path):
                if SmartDL is None:
                    LOGS.warning("digitalgrouppicloop disabled: pySmartDL is not installed")
                    return
                downloader = SmartDL(digitalgrouppfp, digital_group_pic_path, progress_bar=False)
                downloader.start(blocking=False)
                while not downloader.isFinished():
                    await asyncio.sleep(0.5)
            shutil.copy(digital_group_pic_path, autophoto_path)
            Image.open(auto_group_photo_path)
            current_time = datetime.now().strftime("%I:%M")
            img = Image.open(auto_group_photo_path)
            drawn_text = ImageDraw.Draw(img)
            try:
                fnt = ImageFont.truetype(jep, 65)
            except Exception:
                fnt = ImageFont.load_default()
            drawn_text.text((200, 200), current_time, font=fnt, fill=colo)
            img.save(auto_group_photo_path)
            file = await l313l.upload_file(auto_group_photo_path)
            try:
                if i > 0 and dgp is not None:
                    async for photo in l313l.iter_profile_photos(int(dgp), limit=1):
                        await l313l(
                            functions.photos.DeletePhotosRequest(
                                id=[
                                    types.InputPhoto(
                                        id=photo.id,
                                        access_hash=photo.access_hash,
                                        file_reference=photo.file_reference,
                                    )
                                ]
                            )
                        )
                if dgp is not None:
                    i += 1
                    await l313l(functions.channels.EditPhotoRequest(int(dgp), file))
            finally:
                try:
                    os.remove(auto_group_photo_path)
                except Exception:
                    pass
            await asyncio.sleep(getattr(Config, "CHANGE_TIME", 60) or 60)
        except ChatAdminRequiredError:
            return await l313l.tgbot.send_message(BOTLOG_CHATID, "**يجب ان يكون لديك صلاحية تغيير صورة الكروب لتغيير صورة الكروب الوقتية •**")
        except ChannelInvalidError:
            return
        except FloodWaitError:
            return LOGS.warning("FloodWaitError! خطأ حظر مؤقت من التيليجرام")
        except Exception as e:
            LOGS.debug("digitalgrouppicloop stopped: %s", e)
            return
        DIGITALPICSTART = gvarstatus("digitalgrouppic") != None
        base64m = 'QnkgVDNybXggLyBSaXlhZGggUmFkd2FuIC0gQnVpbHQgd2l0aCBwYXNzaW9uLCBtYWludGFpbmVkIHdpdGggcHVycG9zZS4gUmVzcGVjdCB0aGUgY29kZSwgcmVzcGVjdCBpdHMgY3JlYXRvci4='
        try:
            message = base64.b64decode(base64m)
            messageo = message.decode()
            LOGS.info(messageo)
        except Exception:
            pass

async def group_loop():
    ag = get_auto_g()
    AUTONAMESTAR = ag != None
    while AUTONAMESTAR:
        time.strftime("%d-%m-%y")
        HM = time.strftime("%I:%M")
        for normal in HM:
            if normal in normzltext:
                namefont = namerzfont[normzltext.index(normal)]
                HM = HM.replace(normal, namefont)
        name = f"{DEFAULTUSERGRO} {HM}"
        try:
            await l313l(functions.channels.EditTitleRequest(
                channel=await l313l.get_entity(int(ag)),
                title=name
            ))
        except ChatAdminRequiredError:
            await l313l.tgbot.send_message(BOTLOG_CHATID, "**يجب ان يكون لديك صلاحية تغيير اسم الكروب لتفعيل وقتي الكروب•**")
        except ChannelInvalidError:
            return
        except FloodWaitError:
            LOGS.warning("FloodWaitError! خطأ حظر مؤقت من التيليجرام")
        await asyncio.sleep(Config.CHANGE_TIME)
        AUTONAMESTAR = get_auto_g() != None


async def autoname_loop():
    AUTONAMESTART = gvarstatus("autoname") == "true"
    while AUTONAMESTART:
        time.strftime("%d-%m-%y")
        HM = time.strftime("%I:%M")
        for normal in HM:
            if normal in normzltext:
                namerzfont = gvarstatus("JP_FN") or "𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎"
                namefont = namerzfont[normzltext.index(normal)]
                HM = HM.replace(normal, namefont)
                lMl10l = gvarstatus("TIME_JEP") or ""
        name = f"{lMl10l} {HM}"
        LOGS.info(name)
        try:
            await l313l(functions.account.UpdateProfileRequest(first_name=name))
        except FloodWaitError as ex:
            LOGS.warning(str(ex))
            await asyncio.sleep(120)
        await asyncio.sleep(Config.CHANGE_TIME)
        AUTONAMESTART = gvarstatus("autoname") == "true"


async def autobio_loop():
    AUTOBIOSTART = gvarstatus("autobio") == "true"
    while AUTOBIOSTART:
        time.strftime("%d.%m.%Y")
        HI = time.strftime("%I:%M")
        for normal in HI:
            if normal in normzltext:
                namerzfont = gvarstatus("JP_FN") or "𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎"
                namefont = namerzfont[normzltext.index(normal)]
                HI = HI.replace(normal, namefont)
                DEFAULTUSERBIO = gvarstatus("DEFAULT_BIO") or " ﴿ لا تَحزَن إِنَّ اللَّهَ مَعَنا ﴾  "
        bio = f"{DEFAULTUSERBIO} {HI}"
        LOGS.info(bio)
        try:
            await l313l(functions.account.UpdateProfileRequest(about=bio))
        except FloodWaitError as ex:
            LOGS.warning(str(ex))
        await asyncio.sleep(Config.CHANGE_TIME)
        AUTOBIOSTART = gvarstatus("autobio") == "true"


@l313l.on(admin_cmd(pattern=f"{phow8t}(?:\s|$)([\s\S]*)"))
async def _(event):
    "To set random colour pic with time to profile pic"
    downloader = SmartDL(digitalpfp, digitalpic_path, progress_bar=False)
    downloader.start(blocking=False)
    while not downloader.isFinished():
        pass
    if gvarstatus("digitalpic") is not None and gvarstatus("digitalpic") == "true":
        return await edit_delete(event, "**الصـورة الـوقتية شغـالة بالأصـل 🧸♥**")
    addgvar("digitalpic", True)
    await edit_delete(event, "**تم تفـعيل الصـورة الـوقتية بنجـاح ✓**")
    await digitalpicloop()

@l313l.on(admin_cmd(pattern="كروب وقتي"))
async def _(event):
    ison = get_auto_g()
    if event.is_group or event.is_channel:
        if ison is not None and ison == str(event.chat_id):
            return await edit_delete(event, "**الاسم الوقتي شغال للكروب/القناة**")
        chid = event.chat_id
        auto_g(str(chid))
        await edit_delete(event, "**تم تفـعيل الاسـم الوقتي للقناة/الكروب ✓**")
        await group_loop()
    else:
        return await edit_delete(event, "**يمكنك استعمال الاسم الوقتي في الكروب او في القناة فقط**")

@l313l.on(admin_cmd(pattern="كروب صورة وقتي"))
async def _(event):
    ison = gvarstatus("digitalgrouppic")
    if event.is_group or event.is_channel:
        if ison is not None and ison == str(event.chat_id):
            return await edit_delete(event, "**الصورة الوقتية شغالة للكروب/القناة**")
        chid = event.chat_id
        addgvar("digitalgrouppic", str(chid))
        await edit_delete(event, "**تم تفعيل الصورة الوقتية للكروب/ القناة ✓**")
        await digitalgrouppicloop()
    else:
        return await edit_delete(event, "**يمكنك استعمال الصورة الوقتية في كروب او قناة**")

@l313l.on(admin_cmd(pattern=f"{namew8t}(?:\s|$)([\s\S]*)"))
async def _(event):
    "To set your display name along with time"
    if gvarstatus("autoname") is not None and gvarstatus("autoname") == "true":
        return await edit_delete(event, "**الاسـم الـوقتي شغـال بالأصـل 🧸♥**")
    addgvar("autoname", True)
    await edit_delete(event, "**تم تفـعيل اسـم الـوقتي بنجـاح ✓**")
    await autoname_loop()


@l313l.on(admin_cmd(pattern=f"{biow8t}(?:\s|$)([\s\S]*)"))
async def _(event):
    "To update your bio along with time"
    if gvarstatus("autobio") is not None and gvarstatus("autobio") == "true":
        return await edit_delete(event, "**الـبايو الـوقتي شغـال بالأصـل 🧸♥**")
    addgvar("autobio", True)
    await edit_delete(event, "**تم تفـعيل البـايو الـوقتي بنجـاح ✓**")
    await autobio_loop()


@l313l.ar_cmd(
    pattern="انهاء ([\s\S]*)",
    command=("انهاء", plugin_category),
)
async def _(event):  # sourcery no-metrics
    "To stop the functions of autoprofile plugin"
    input_str = event.pattern_match.group(1)
    if input_str == "الصورة الوقتية":
        if gvarstatus("digitalpic") is not None and gvarstatus("digitalpic") == "true":
            delgvar("digitalpic")
            await event.client(
                functions.photos.DeletePhotosRequest(
                    await event.client.get_profile_photos("me", limit=1)
                )
            )
            return await edit_delete(event, "**تم ايقاف الصورة الوقتية بنـجاح ✓ **")
        return await edit_delete(event, "**لم يتم تفعيل الصورة الوقتية بالأصل 🧸♥**")
    if input_str == "اسم وقتي":
        if gvarstatus("autoname") is not None and gvarstatus("autoname") == "true":
            delgvar("autoname")
            await event.client(
                functions.account.UpdateProfileRequest(last_name=DEFAULTUSER)
            )
            return await edit_delete(event, "**تم ايقاف  الاسم الوقتي بنـجاح ✓ **")
        return await edit_delete(event, "**لم يتم تفعيل الاسم الوقتي بالأصل 🧸♥**")
    if input_str == "بايو وقتي":
        if gvarstatus("autobio") is not None and gvarstatus("autobio") == "true":
            delgvar("autobio")
            await event.client(
                functions.account.UpdateProfileRequest(about=DEFAULTUSERBIO)
            )
            return await edit_delete(event, "**  تم ايقاف البايو الوقـتي بنـجاح ✓**")
        return await edit_delete(event, "**لم يتم تفعيل البايو الوقتي 🧸♥**")
    if input_str == "كروب صورة وقتي":
        if gvarstatus("digitalgrouppic") is not None:
            delgvar("digitalgrouppic")
            return await edit_delete(event, "**  تم ايقاف صورة الكروب الوقتية بنجاح ✓**")
        return await edit_delete(event, "**لم يتم تفعيل صورة الكروب/ القناة الوقتية بالأصل**")
    if input_str == "كروب وقتي":
        if get_auto_g() is not None:
            del_auto_g()
            return await edit_delete(event, "** تـم ايقاف الاسم الوقتي للكروب/القناة ✓**")
        return await edit_delete(event, "** لم يتم تفعيل الاسم الوقتي للكروب/القناة بالأصل **")
    END_CMDS = [
        "الصورة الوقتية",
        "اسم وقتي",
        "بايو وقتي",
        "كروب وقتي",
        "كروب صورة وقتي",
    ]
    if input_str not in END_CMDS:
        await edit_delete(
            event,
            f"عـذرا يجـب استـخدام الامـر بشـكل صحـيح 🧸♥",
            parse_mode=_format.parse_pre,
        )


l313l.loop.create_task(digitalpicloop())
l313l.loop.create_task(digitalgrouppicloop())
l313l.loop.create_task(autoname_loop())
l313l.loop.create_task(autobio_loop())
l313l.loop.create_task(group_loop())
