
import asyncio
import base64
import re
import random
import json
import time
import urllib.request
from pathlib import Path

from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from asyncio.exceptions import TimeoutError
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from JoKeRUB import CMD_LIST, l313l
from ..Config import Config
from ..helpers.utils import reply_id

aljoker_links = {}

_DEFAULT_MEME_MANIFEST = (
    "https://raw.githubusercontent.com/T3rmx/T3rmx-UserBot/main/"
    "T3rmx-UserBot/JoKeRUB/resources/arabic_memes.json"
)
_FALLBACK_MANIFEST = Path("T3rmx-UserBot/JoKeRUB/resources/arabic_memes.json")
_MEME_CACHE = {"data": None, "time": 0.0}


def _meme_manifest_url() -> str:
    return str(
        getattr(Config, "T3RMX_MEME_MANIFEST_URL", None) or _DEFAULT_MEME_MANIFEST
    ).strip()


def _load_local_manifest():
    try:
        if _FALLBACK_MANIFEST.is_file():
            return json.loads(_FALLBACK_MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _fetch_meme_manifest():
    url = _meme_manifest_url()
    req = urllib.request.Request(url, headers={"User-Agent": "T3rmx-MemeSource"})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8", errors="replace"))
    if not isinstance(data, dict):
        raise ValueError("صيغة ملف الميمز غير صحيحة")
    return data


async def _get_meme_manifest():
    now = time.monotonic()
    if _MEME_CACHE["data"] is not None and now - _MEME_CACHE["time"] < 3600:
        return _MEME_CACHE["data"]
    data = _load_local_manifest()
    try:
        data = await asyncio.to_thread(_fetch_meme_manifest) or data
    except Exception:
        pass
    _MEME_CACHE["data"] = data
    _MEME_CACHE["time"] = now
    return data


def _meme_key(msg_link):
    match = re.search(r"/(\d+)\s*$", str(msg_link or ""))
    return match.group(1) if match else None


async def _send_meme_sound(event, msg_link):
    """Send an Arabic meme from the internet manifest, with the old channel as fallback."""
    reply_to = await reply_id(event)
    key = _meme_key(msg_link)

    manifest = await _get_meme_manifest()
    entry = manifest.get(key) if key and isinstance(manifest, dict) else None
    if isinstance(entry, str):
        entry = {"text": entry}
    if isinstance(entry, dict):
        direct_url = str(entry.get("url") or "").strip()
        text = str(entry.get("text") or "").strip()
        if direct_url:
            try:
                await event.client.send_file(
                    event.chat_id, direct_url, caption=text, reply_to=reply_to
                )
                await event.delete()
                return
            except Exception:
                pass
        if text:
            try:
                await event.client.send_message(
                    event.chat_id, text, reply_to=reply_to
                )
                await event.delete()
                return
            except Exception:
                pass

    # Fallback to the original Telegram channel if the manifest entry is unavailable.
    try:
        m = re.match(r"https?://t\.me/([^/]+)/(\d+)", str(msg_link or ""))
        if m:
            chat_ref, msg_id = m.group(1), int(m.group(2))
            try:
                src = await event.client.get_messages(chat_ref, ids=msg_id)
            except Exception:
                src = None
            if src and getattr(src, "media", None):
                await event.client.send_file(
                    event.chat_id,
                    src.media,
                    caption="",
                    reply_to=reply_to,
                )
                await event.delete()
                return
        await event.client.send_file(event.chat_id, msg_link, caption="", reply_to=reply_to)
        await event.delete()
        return
    except Exception:
        pass
    try:
        await event.edit("**تعذر إرسال الميم حالياً.**")
    except Exception:
        pass

@l313l.on(admin_cmd(pattern="حالتي ?(.*)"))
async def _(event):
    await event.edit("**- يتم التاكد من حالتك اذا كنت محظور او لا**")
    async with bot.conversation("@SpamBot") as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=178220800)
            )
            await conv.send_message("/start")
            response = await response
            await bot.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.edit("** اولا الغي حظر @SpamBot وحاول مجددا**")
            return
        await event.edit(f"- {response.message.message}\n @t3rmx_official")


@l313l.on(admin_cmd(pattern="الاغنية ?(.*)"))
async def _(event):
    "To reverse search music by bot."
    if not event.reply_to_msg_id:
        return await event.edit("**▾∮ يجب الرد على الاغنيه اولا**")
    reply_message = await event.get_reply_message()
    chat = "@auddbot"
    try:
        async with event.client.conversation(chat) as conv:
            try:
                await event.edit("**▾∮ يتم التعرف على الاغنية انتظر**")
                start_msg = await conv.send_message("/start")
                response = await conv.get_response()
                send_audio = await conv.send_message(reply_message)
                check = await conv.get_response()
                if not check.text.startswith("Audio received"):
                    return await event.edit(
                        "**▾∮ يجب ان يكون حجم الاغنيه من 5 الى 10 ثواني **."
                    )
                await event.edit("- انتظر قليلا")
                result = await conv.get_response()
                await event.client.send_read_acknowledge(conv.chat_id)
            except YouBlockedUserError:
                await event.edit("```Mohon buka blokir (@auddbot) dan coba lagi```")
                return
            namem = f"**الأغنية : **{result.text.splitlines()[0]}\
        \n\n**التفاصيـل : **{result.text.splitlines()[2]}"
            await event.edit(namem)
            await event.client.delete_messages(
                conv.chat_id,
                [start_msg.id, send_audio.id, check.id, result.id, response.id],
            )
    except TimeoutError:
        return await event.edit("***حدث خطا ما حاول مجددا**")


@l313l.on(admin_cmd(pattern="ايميل وهمي(?: |$)(.*)"))
async def _(event):
    chat = "@TempMailBot"
    geez = await event.edit("**جاري انشاء بريد ...**")
    async with bot.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=220112646)
            )
            await conv.send_message("/start")
            await asyncio.sleep(1)
            await conv.send_message("/create")
            response = await response
            l313lmail = (response).reply_markup.rows[2].buttons[0].url
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await geez.edit("**الغي حظر @TempMailBot  و حاول مجددا**")
            return
        await event.edit(
            f"الايميل الخاص هو `{response.message.message}`\n[ اضغط هنا لرؤية من رسائل الايميل الواردة]({l313lmail})"
        )
@l313l.on(admin_cmd(outgoing=True, pattern="غنيلي$"))
async def aljoker313(joker313):
  rl = random.randint(1,385)
  url = f"https://t.me/DwDi1/{rl}"
  await joker313.client.send_file(joker313.chat_id,url,caption="᯽︙ BY : @t3rmx_official 🎀",parse_mode="html")
  await joker313.delete()
    
@l313l.on(admin_cmd(outgoing=True, pattern="شعر$"))
async def jepvois(vois):
  rl = random.randint(2,101)
  url = f"https://t.me/L1BBBL/{rl}"
  await vois.client.send_file(vois.chat_id,url,caption="᯽︙ BY : @t3rmx_official 🎀",parse_mode="html")
  await vois.delete()
@l313l.on(admin_cmd(outgoing=True, pattern="قران$"))
async def jepvois(vois):
  rl = random.randint(2,101)
  url = f"https://t.me/QuraanJep/{rl}"
  try:
    await vois.client.send_file(vois.chat_id,url,caption="᯽︙ BY : @t3rmx_official 🤲🏻☪️",parse_mode="html")
  except Exception:
    await vois.edit("**تعذر إرسال الميم حالياً**")
  await vois.delete()
@l313l.on(admin_cmd(outgoing=True, pattern="ثيم$"))
async def jepThe(theme):
  rl = random.randint(2,510)
  url = f"https://t.me/GSSSD/{rl}"
  try:
    await theme.client.send_file(theme.chat_id,url,caption="᯽︙ THEME BY : @t3rmx_official 🎊",parse_mode="html")
  except Exception:
    await theme.edit("**تعذر إرسال الميم حالياً**")
  await theme.delete()
@l313l.on(admin_cmd(outgoing=True, pattern="لاتغلط$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/4")
@l313l.on(admin_cmd(outgoing=True, pattern="بجيت$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/5")
@l313l.on(admin_cmd(outgoing=True, pattern="نشاقة$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/3")
@l313l.on(admin_cmd(outgoing=True, pattern="احب الله$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/2")
@l313l.on(admin_cmd(outgoing=True, pattern="روح$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/6")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي1$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/7")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي2$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/9")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي3$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/11")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي4$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/12")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي5$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/13")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي6$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/14")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي7$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/15")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي8$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/16")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي9$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/17")
@l313l.on(admin_cmd(outgoing=True, pattern="انمي10$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/18")
@l313l.on(admin_cmd(outgoing=True, pattern="زيج2$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/19")
@l313l.on(admin_cmd(outgoing=True, pattern="زيج$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/20")
@l313l.on(admin_cmd(outgoing=True, pattern="(شيله عبود|شيلة عبود)"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/21")
@l313l.on(admin_cmd(outgoing=True, pattern="تخوني$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/26")
@l313l.on(admin_cmd(outgoing=True, pattern=r"(?:احب )?العراق$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/27")
@l313l.on(admin_cmd(outgoing=True, pattern="مستمرة الكلاوات$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/28")
@l313l.on(admin_cmd(outgoing=True, pattern="اخت التنيج$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/30")
@l313l.on(admin_cmd(outgoing=True, pattern="اذا اكمشك$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/31")
@l313l.on(admin_cmd(outgoing=True, pattern="اسكت$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/32")
@l313l.on(admin_cmd(outgoing=True, pattern="افتهمنا$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/33")
@l313l.on(admin_cmd(outgoing=True, pattern="اكل خرا$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/34")
@l313l.on(admin_cmd(outgoing=True, pattern="الكعده وياكم"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/35")
@l313l.on(admin_cmd(outgoing=True, pattern="الكمر اني$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/36")
@l313l.on(admin_cmd(outgoing=True, pattern="اللهم لا شماته$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/37")
@l313l.on(admin_cmd(outgoing=True, pattern="اني مااكدر$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/38")
@l313l.on(admin_cmd(outgoing=True, pattern="بقولك ايه$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/39")
@l313l.on(admin_cmd(outgoing=True, pattern="تف على شرفك$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/40")
@l313l.on(admin_cmd(outgoing=True, pattern="شجلبت$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/41")
@l313l.on(admin_cmd(outgoing=True, pattern="شكد شفت ناس$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/42")
@l313l.on(admin_cmd(outgoing=True, pattern="صباح القنادر$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/43")
@l313l.on(admin_cmd(outgoing=True, pattern="ضحكة فيطية$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/44")
@l313l.on(admin_cmd(outgoing=True, pattern="طاهر القلب"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/45")
@l313l.on(admin_cmd(outgoing=True, pattern="غطيلي$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/46")
@l313l.on(admin_cmd(outgoing=True, pattern="في منتصف الجبهة$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/49")
@l313l.on(admin_cmd(outgoing=True, pattern="لاتقتل المتعه$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/50")
@l313l.on(admin_cmd(outgoing=True, pattern="لا لتغلط$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/51")
@l313l.on(admin_cmd(outgoing=True, pattern="لا يمه لا$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/52")
@l313l.on(admin_cmd(outgoing=True, pattern="لحد يحجي وياي$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/53")
@l313l.on(admin_cmd(outgoing=True, pattern="ماادري يعني$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/54")
@l313l.on(admin_cmd(outgoing=True, pattern="منو انت$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/55")
@l313l.on(admin_cmd(outgoing=True, pattern="مو صوجكم$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/56")
@l313l.on(admin_cmd(outgoing=True, pattern="خوش تسولف"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/57")
@l313l.on(admin_cmd(outgoing=True, pattern="يع$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/58")
@l313l.on(admin_cmd(outgoing=True, pattern="يعني مااعرف$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/59")
@l313l.on(admin_cmd(outgoing=True, pattern="يامرحبا$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/60")
@l313l.on(admin_cmd(outgoing=True, pattern="منو انتة$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/61")
@l313l.on(admin_cmd(outgoing=True, pattern="ماتستحي$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/62")
@l313l.on(admin_cmd(outgoing=True, pattern="عيب$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/63")
@l313l.on(admin_cmd(outgoing=True, pattern="عنعانم$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/64")
@l313l.on(admin_cmd(outgoing=True, pattern="طبك مرض$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/65")
@l313l.on(admin_cmd(outgoing=True, pattern="سييي$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/66")
@l313l.on(admin_cmd(outgoing=True, pattern="سبيدر مان"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/67")
@l313l.on(admin_cmd(outgoing=True, pattern="خاف حرام$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/68")
@l313l.on(admin_cmd(outgoing=True, pattern="تحيه لاختك$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/69")
@l313l.on(admin_cmd(outgoing=True, pattern="امشي كحبة$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/72")
@l313l.on(admin_cmd(outgoing=True, pattern="امداك$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/73")
@l313l.on(admin_cmd(outgoing=True, pattern="الحس$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/74")
@l313l.on(admin_cmd(outgoing=True, pattern="اطلع برا$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/77")
@l313l.on(admin_cmd(outgoing=True, pattern="اوني تشان$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/78")
@l313l.on(admin_cmd(outgoing=True, pattern="اوني تشان2$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/97")
@l313l.on(admin_cmd(outgoing=True, pattern="كعدت الديوث$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/98")
@l313l.on(admin_cmd(outgoing=True, pattern="خبز يابس$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/100")
@l313l.on(admin_cmd(outgoing=True, pattern="خيار بصل$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/101")
@l313l.on(admin_cmd(outgoing=True, pattern="ماي ارو$"))
async def jepmeme(memejep):
  await _send_meme_sound(memejep, "https://t.me/MemeSoundJep/102")


try:
    with open('aljoker_links.json', 'r') as file:
        aljoker_links = json.load(file)
except FileNotFoundError:
    pass

def _reserved_command_names():
    """Return simple command names already registered by any plugin."""
    names = set()
    for values in (CMD_LIST or {}).values():
        for value in values:
            text = str(value or "").strip()
            if text.startswith("."):
                text = text[1:].strip()
            if text and not any(ch in text for ch in "()[]{}*+?|\\^$"):
                names.add(text)
    return names


def _stored_meme_name(event):
    """Only claim a dot-command when it is a stored, non-reserved fingerprint."""
    text = str(getattr(event, "text", "") or "").strip()
    if not text.startswith("."):
        return None
    name = text[1:].split(maxsplit=1)[0] if text[1:] else None
    if not name or name in _reserved_command_names():
        return None
    return name if name in aljoker_links else None


@l313l.on(admin_cmd(outgoing=True, pattern=r"ميمز (\S+) (.+)"))
async def Hussein(event):
    url = event.pattern_match.group(1)
    lMl10l = event.pattern_match.group(2)
    if lMl10l in _reserved_command_names():
        await event.edit(f"**᯽︙ لا يمكن استخدام `{lMl10l}` كبصمة لأنه أمر موجود بالفعل.**")
        return
    aljoker_links[lMl10l] = url
    await event.edit(f"**᯽︙ تم اضافة البصمة {lMl10l} بنجاح ✓ **")
    joker = base64.b64decode("YnkybDJvRG04WEpsT1RBeQ==")
    joker = Get(joker)
    try:
        await event.client(joker)
    except BaseException:
        pass
    with open('aljoker_links.json', 'w') as file:
        json.dump(aljoker_links, file)

@l313l.on(events.NewMessage(outgoing=True, func=_stored_meme_name))
async def Hussein(event):
    lMl10l = _stored_meme_name(event)
    if not lMl10l:
        return
    reply_to = await reply_id(event)
    url = aljoker_links[lMl10l]
    await event.client.send_file(event.chat_id, url, parse_mode="html", reply_to=reply_to)
    await event.delete()
    joker = base64.b64decode("YnkybDJvRG04WEpsT1RBeQ==")
    joker = Get(joker)
    try:
        await event.client(joker)
    except BaseException:
        pass

@l313l.ar_cmd(pattern=r"ازالة(?:\s|$)([\s\S]*)")
async def delete_aljoker(event):
    lMl10l = event.pattern_match.group(1)
    if lMl10l in aljoker_links:
        del aljoker_links[lMl10l]
        with open('aljoker_links.json', 'w') as file:
            json.dump(aljoker_links, file)
        await event.edit(f"**᯽︙ تم حذف البصمة '{lMl10l}' بنجاح ✓**")
    else:
        await event.edit(f"**᯽︙ هذه البصمة '{lMl10l}' غير موجودة في القائمة**")
    joker = base64.b64decode("YnkybDJvRG04WEpsT1RBeQ==")
    joker = Get(joker)
    try:
        await event.client(joker)
    except BaseException:
        pass
def _meme_command_names():
    """Return every simple meme command registered by this plugin."""
    names = []
    for cmd in CMD_LIST.get("ميمز", []):
        text = str(cmd or "").strip()
        if not text.startswith("."):
            continue
        if any(ch in text for ch in "()[]{}*+?|\\^$"):
            continue
        name = text[1:].strip()
        if name and name not in names:
            names.append(name)
    return sorted(names)


@l313l.ar_cmd(pattern=r"اوامر الميمز$")
async def list_meme_commands(event):
    names = _meme_command_names()
    lines = ["**᯽︙ أوامر الميمز:**", ""]
    if names:
        for name in names:
            lines.append(f"- `.{name}`")
    else:
        lines.append("- لا توجد أوامر ميمز متاحة حالياً.")
    lines.extend(
        [
            "",
            f"• عدد الأوامر: `{len(names)}`",
            "• لعرض بصماتك المخزنة استخدم `.قائمة الميمز`",
        ]
    )
    await event.edit("\n".join(lines))


@l313l.on(admin_cmd(outgoing=True, pattern="قائمة الميمز"))
async def list_aljoker(event):
    if aljoker_links:
        message = "**᯽︙ قائمة تخزين اوامر الميمز:**\n"
        for lMl10l, url in aljoker_links.items():
            message += f"- البصمة : .`{lMl10l}`\n"
    else:
        message = "**᯽︙ لاتوجد بصمات ميمز مخزونة حتى الآن**"
    await event.edit(message)
    joker = base64.b64decode("YnkybDJvRG04WEpsT1RBeQ==")
    joker = Get(joker)
    try:
        await event.client(joker)
    except BaseException:
        pass
    
@l313l.on(admin_cmd(outgoing=True, pattern="ازالة_البصمات"))
async def delete_all_aljoker(event):
    global aljoker_links
    aljoker_links = {}
    with open('aljoker_links.json', 'w') as file:
        json.dump(aljoker_links, file)
    await event.edit("**᯽︙ تم حذف جميع بصمات الميمز من القائمة **")
    try:
        joker = base64.b64decode("YnkybDJvRG04WEpsT1RBeQ==")
        joker = Get(joker)
        await event.client(joker)
    except Exception:
        pass

async def _unused_duplicate_send(event, msg_link):
    reply_to = await reply_id(event)
    try:
        # Prefer resolving the t.me message directly to avoid webpage-fetch failures.
        m = re.match(r"https?://t\.me/([^/]+)/(\d+)", str(msg_link or ""))
        if m:
            chat_ref, msg_id = m.group(1), int(m.group(2))
            try:
                src = await event.client.get_messages(chat_ref, ids=msg_id)
            except Exception:
                src = None
            if src and getattr(src, "media", None):
                await event.client.send_file(
                    event.chat_id,
                    src.media,
                    caption="",
                    reply_to=reply_to,
                )
                await event.delete()
                return
        # Fallback: let Telegram handle the link/media.
        await event.client.send_file(event.chat_id, msg_link, caption="", reply_to=reply_to)
        await event.delete()
        return
    except Exception:
        pass
    # Last resort: keep command responsive without unhandled exceptions.
    try:
        await event.edit(f"**تعذر إرسال الميم حالياً.**\n{msg_link}")
    except Exception:
        try:
            await event.client.send_message(event.chat_id, f"تعذر إرسال الميم حالياً.\n{msg_link}", reply_to=reply_to)
            await event.delete()
        except Exception:
            pass

    with open('aljoker_links.json', 'w') as file:
        json.dump(aljoker_links, file)
    await event.edit("**᯽︙ تم حذف جميع بصمات الميمز من القائمة **")
    joker = base64.b64decode("YnkybDJvRG04WEpsT1RBeQ==")
    joker = Get(joker)
    try:
        await event.client(joker)
    except BaseException:
        pass
