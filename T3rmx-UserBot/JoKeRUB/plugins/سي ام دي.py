import os
from pathlib import Path
import importlib.util

from ..Config import Config
from ..core.auth import is_owner
from ..utils import load_module, remove_plugin
from . import CMD_HELP, CMD_LIST, SUDO_LIST, l313l, edit_delete, edit_or_reply, reply_id

plugin_category = "tools"

DELETE_TIMEOUT = 5
thumb_image_path = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")

@l313l.ar_cmd(
    pattern="جد بكج (.*)",
    command=("جد بكج", plugin_category),
    info={
        "header": "البحث عن بكج.",
        "description": "لمعرفة هل ان البكج موجود ام لا.",
    },
)
async def findpkg(event):
    pkgname = event.pattern_match.group(1)
    try:
         if importlib.util.find_spec(pkgname) is None:
             raise ImportError(pkgname)
         await edit_or_reply(event, f"᯽︙ الباكج موجود ✓\n{pkgname}")
    except (ImportError, ValueError, ModuleNotFoundError):
         await edit_or_reply(event, f"᯽︙ الباكج غير موجود X \n{pkgname}")

@l313l.ar_cmd(
    pattern="تنصيب بلجن$",
    command=("تنصيب بلجن", plugin_category),
    info={
        "header": "To install an external plugin.",
        "description": "Reply to any external plugin(supported by cat) to install it in your bot.",
        "usage": "{tr}تنصيب بلجن",
    },
)
async def install(event):
    "To install an external plugin."
    if not is_owner(getattr(event, "sender_id", None)):
        return await edit_or_reply(event, "**هذا الأمر مخصص لمالك البوت فقط.**")
    if event.reply_to_msg_id:
        downloaded_file_name = None
        try:
            downloaded_file_name = await event.client.download_media(
                await event.get_reply_message(),
                "JoKeRUB/plugins/",
            )
            if "(" not in downloaded_file_name:
                path1 = Path(downloaded_file_name)
                shortname = path1.stem
                load_module(shortname.replace(".py", ""))
                await edit_delete(
                    event,
                    f"᯽︙ تـم تثبيـت المـلف `{os.path.basename(downloaded_file_name)}`",
                    10,
                )
            else:
                os.remove(downloaded_file_name)
                await edit_delete(
                    event, "**خـطأ  هذا الملف تم تنصيبه مسبقا او يوجد في السورس **", 10
                )
        except Exception as e:
            await edit_delete(event, f"**خـطأ:**\n`{str(e)}`", 10)
            try:
                if downloaded_file_name and os.path.exists(downloaded_file_name):
                    os.remove(downloaded_file_name)
            except Exception:
                pass


@l313l.ar_cmd(
    pattern="الغاء التنصيب (.*)",
    command=("الغاء التنصيب", plugin_category),
    info={
        "header": "To uninstall a plugin temporarily.",
        "description": "To stop functioning of that plugin and remove that plugin from bot.",
        "note": "To unload a plugin permanently from bot set NO_LOAD var in heroku with that plugin name, give space between plugin names if more than 1.",
        "usage": "{tr}uninstall <plugin name>",
        "examples": "{tr}uninstall markdown",
    },
)
async def unload(event):
    "To uninstall a plugin."
    if not is_owner(getattr(event, "sender_id", None)):
        return await edit_or_reply(event, "**هذا الأمر مخصص لمالك البوت فقط.**")
    shortname = event.pattern_match.group(1)
    path = Path(f"JoKeRUB/plugins/{shortname}.py")
    if not os.path.exists(path):
        return await edit_delete(
            event, f"᯽︙ لا يوجد هكذا ملف مع المسار {path} لحذفه"
        )
    os.remove(path)
    if shortname in CMD_LIST:
        CMD_LIST.pop(shortname)
    if shortname in SUDO_LIST:
        SUDO_LIST.pop(shortname)
    if shortname in CMD_HELP:
        CMD_HELP.pop(shortname)
    try:
        remove_plugin(shortname)
        await edit_or_reply(event, f"᯽︙ {shortname} تم الغاء تثبيت الملف بنجاح")
    except Exception as e:
        await edit_or_reply(event, f"᯽︙ تم الغاء التثبيت بنجاح {shortname}\n{str(e)}")
