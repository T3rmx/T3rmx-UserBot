"""Arabic log-channel helper.

Creates a private Telegram log channel once, stores its id in globals, and sends
only short text alerts there. The full log file is sent only on the owner's /log command.
"""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from telethon.tl.functions.channels import CreateChannelRequest

from ..Config import Config
from ..core.logger import logging
from ..sql_helper.globals import addgvar, gvarstatus

LOGS = logging.getLogger("t3rmx.logchannel")

LOG_CHANNEL_GVAR = "T3RMX_LOG_CHANNEL_ID"
LOG_CHANNEL_TITLE = "سجلات T3rmx"
STORAGE_GROUP_GVAR = "T3RMX_STORAGE_GROUP_ID"
BACKUP_MSG_GVAR = "T3RMX_SETTINGS_BACKUP_MSG_ID"
BACKUP_FP_GVAR = "T3RMX_SETTINGS_BACKUP_FINGERPRINT"
BACKUP_RESTORED_GVAR = "T3RMX_SETTINGS_RESTORED"
CONFIG_PREFIX = "T3RMX_CFG_"
BACKUP_MARKER = "#T3RMX_BACKUP"

# Never include credentials or connection secrets in the backup file.
_SECRET_KEY_PARTS = (
    "SESSION", "TOKEN", "API", "APP_ID", "API_HASH", "PASSWORD", "SECRET", "KEY",
    "CRED", "AUTH", "DB_URI", "DATABASE_URL", "VERIFICATION", "PRIVATE_KEY",
    "G_DRIVE_DATA", "SCREEN_SHOT_LAYER", "OPEN_WEATHER", "IBM_WATSON", "OCR_SPACE",
    "GENIUS", "REM_BG", "CURRENCY", "LASTFM", "SPAMWATCH", "GITHUB_ACCESS",
    "DEEP_AI", "HEROKU", "ACCESS_KEY", "VC_SESSION",
)

_BACKUP_INTERNAL_KEYS = {
    BACKUP_MSG_GVAR,
    BACKUP_FP_GVAR,
    BACKUP_RESTORED_GVAR,
}


def _log_path() -> str:
    return os.path.abspath(os.environ.get("T3RMX_LOG_FILE", "logs/t3rmx.log"))


def _normalize_chat_id(value) -> int | None:
    try:
        cid = int(str(value).strip())
    except Exception:
        return None
    if cid == 0:
        return None
    if str(cid).startswith("-100"):
        return cid
    return int("-100" + str(abs(cid)))


async def get_log_channel_id():
    """Resolve the log channel id from globals or configured fallback."""
    stored = gvarstatus(LOG_CHANNEL_GVAR)
    if stored:
        cid = _normalize_chat_id(stored)
        if cid:
            return cid
    configured = getattr(Config, "PRIVATE_GROUP_BOT_API_ID", 0)
    if configured:
        return _normalize_chat_id(configured)
    return None


async def _mute_and_archive(client, channel):
    """Mute and archive a freshly created log channel. Best effort only."""
    import datetime

    from telethon.tl.functions.account import UpdateNotifySettingsRequest
    from telethon.tl.types import InputPeerChannel, InputPeerNotifySettings

    try:
        peer = InputPeerChannel(channel.id, channel.access_hash)
        await client(
            UpdateNotifySettingsRequest(
                peer=peer,
                settings=InputPeerNotifySettings(
                    mute_until=datetime.datetime.utcnow()
                    + datetime.timedelta(days=365 * 10),
                    silent=True,
                ),
            )
        )
    except Exception as e:
        LOGS.debug("تعذر كتم قناة السجلات: %s", e)

    try:
        await client.edit_folder(channel, 1)
    except Exception as e:
        LOGS.debug("تعذر أرشفة قناة السجلات: %s", e)


async def ensure_log_channel(client):
    """Return the log channel id, creating it once if needed.

    Returns a ``(chat_id, created)`` tuple. Existing configured log chats are
    reused so repeated commands never create duplicates.
    """
    stored = gvarstatus(LOG_CHANNEL_GVAR)
    if stored:
        existing = _normalize_chat_id(stored)
        if existing:
            return existing, False

    configured = getattr(Config, "PRIVATE_GROUP_BOT_API_ID", 0)
    if configured:
        existing = _normalize_chat_id(configured)
        if existing:
            addgvar(LOG_CHANNEL_GVAR, str(existing))
            Config.PRIVATE_GROUP_BOT_API_ID = existing
            Config.BOTLOG = True
            Config.BOTLOG_CHATID = existing
            return existing, False

    title = LOG_CHANNEL_TITLE
    about = "قناة خاصة للتنبيهات المختصرة. لا يتم إرسال ملف السجلات هنا تلقائياً."

    # On a fresh deploy the local database may be empty. Find the existing
    # channel by title before creating a duplicate.
    try:
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            entity = dialog.entity
            if (
                getattr(entity, "title", None) == title
                and getattr(entity, "broadcast", False)
            ):
                cid = _normalize_chat_id(entity.id)
                if cid:
                    await _mute_and_archive(client, entity)
                    addgvar(LOG_CHANNEL_GVAR, str(cid))
                    if not getattr(Config, "PRIVATE_GROUP_BOT_API_ID", 0):
                        addgvar("PRIVATE_GROUP_BOT_API_ID", str(cid))
                    Config.PRIVATE_GROUP_BOT_API_ID = cid
                    Config.BOTLOG = True
                    Config.BOTLOG_CHATID = cid
                    LOGS.info("تم العثور على قناة السجلات الحالية وإعادة استخدامها")
                    return cid, False
    except Exception as e:
        LOGS.debug("تعذر البحث عن قناة السجلات الحالية: %s", e)
    result = await client(
        CreateChannelRequest(
            title=title,
            about=about,
            broadcast=True,
        )
    )
    channel = result.chats[0]
    cid = _normalize_chat_id(channel.id)
    if not cid:
        return None, False
    await _mute_and_archive(client, channel)
    addgvar(LOG_CHANNEL_GVAR, str(cid))
    if not getattr(Config, "PRIVATE_GROUP_BOT_API_ID", 0):
        addgvar("PRIVATE_GROUP_BOT_API_ID", str(cid))
    Config.PRIVATE_GROUP_BOT_API_ID = cid
    Config.BOTLOG = True
    Config.BOTLOG_CHATID = cid
    LOGS.info("تم إنشاء قناة السجلات بنجاح")
    return cid, True


async def ensure_storage_group(client):
    """Return the storage chat id, creating the private group once if needed.

    Returns a ``(chat_id, created)`` tuple. An already configured
    ``PM_LOGGER_GROUP_ID`` is reused and remembered instead of creating a new
    group.
    """
    stored = gvarstatus(STORAGE_GROUP_GVAR)
    if stored:
        cid = _normalize_chat_id(stored)
        if cid:
            return cid, False

    configured = getattr(Config, "PM_LOGGER_GROUP_ID", -100)
    if configured and configured != -100:
        cid = _normalize_chat_id(configured)
        if cid:
            addgvar(STORAGE_GROUP_GVAR, str(cid))
            return cid, False

    # A fresh database still must not create a duplicate: look for a storage
    # group that already exists in the account's dialogs and reuse it.
    titles = ("تخزين T3rmx", "مجموعة التخزين6023224495")
    try:
        found = {}
        for dialog in await client.get_dialogs():
            entity = dialog.entity
            name = getattr(entity, "title", None)
            if not name or not getattr(entity, "megagroup", False):
                continue
            for index, wanted in enumerate(titles):
                if name == wanted:
                    found.setdefault(index, entity)
        for index in sorted(found):
            cid = _normalize_chat_id(found[index].id)
            if cid:
                addgvar(STORAGE_GROUP_GVAR, str(cid))
                addgvar("PM_LOGGER_GROUP_ID", str(cid))
                Config.PM_LOGGER_GROUP_ID = cid
                LOGS.info("تم العثور على كروب التخزين الحالي وإعادة استخدامه")
                return cid, False
    except Exception as e:
        LOGS.debug("تعذر البحث عن كروب التخزين الحالي: %s", e)

    title = titles[0]
    about = "مجموعة خاصة لحفظ الرسائل والملفات. لا تُرسل هنا السجلات تلقائياً."
    result = await client(
        CreateChannelRequest(title=title, about=about, megagroup=True)
    )
    group = result.chats[0]
    cid = _normalize_chat_id(group.id)
    if not cid:
        return None, False
    addgvar(STORAGE_GROUP_GVAR, str(cid))
    addgvar("PM_LOGGER_GROUP_ID", str(cid))
    Config.PM_LOGGER_GROUP_ID = cid
    LOGS.info("تم إنشاء كروب التخزين بنجاح")
    return cid, True


async def send_log_alert(client, text: str) -> bool:
    """Send a short Arabic alert to the log channel. Never attaches a file."""
    try:
        cid = await get_log_channel_id()
        if not cid:
            return False
        clean = str(text).strip()
        if len(clean) > 900:
            clean = clean[:900] + " …"
        await client.send_message(cid, clean, link_preview=False)
        return True
    except Exception as e:
        LOGS.debug("تعذر إرسال تنبيه السجلات: %s", e)
        return False


async def send_log_file(client, chat_id=None) -> bool:
    """Send the full log file as a document, only when explicitly requested."""
    try:
        target = chat_id or await get_log_channel_id()
        if not target:
            return False
        path = _log_path()
        await client.send_file(
            target,
            path,
            force_document=True,
            caption="**ملف سجلات T3rmx**",
        )
        return True
    except Exception as e:
        LOGS.debug("تعذر إرسال ملف السجلات: %s", e)
        return False


def _is_secret_key(key: str) -> bool:
    upper = str(key).upper()
    return any(part in upper for part in _SECRET_KEY_PARTS)


def _jsonable(value):
    if isinstance(value, set):
        return sorted(value)
    if isinstance(value, tuple):
        return list(value)
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


def _collect_settings():
    from ..sql_helper.globals import get_all_gvars

    data = get_all_gvars() or {}
    return {
        str(key): str(value)
        for key, value in sorted(data.items())
        if str(key) not in _BACKUP_INTERNAL_KEYS
        and not str(key).startswith(CONFIG_PREFIX)
        and not _is_secret_key(str(key))
    }


def _collect_config():
    result = {}
    for key in dir(Config):
        if key.startswith("_") or _is_secret_key(key):
            continue
        value = getattr(Config, key)
        if not isinstance(value, (str, int, float, bool, type(None), list, tuple, set, dict)):
            continue
        result[key] = _jsonable(value)
    return dict(sorted(result.items()))


def _collect_command_files():
    root = Path(__file__).resolve().parents[1]
    files = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except Exception:
            continue
        files.append({"path": str(path.relative_to(root)), "sha256": digest})
    return files


def _build_payload():
    settings = _collect_settings()
    config = _collect_config()
    commands = _collect_command_files()
    fingerprint_source = json.dumps(
        {"settings": settings, "config": config, "commands": commands},
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    return {
        "format": 1,
        "settings": settings,
        "config": config,
        "commands": commands,
        "fingerprint": hashlib.sha256(fingerprint_source).hexdigest(),
    }


def apply_backup_config() -> int:
    """Apply non-secret config values previously saved in globals."""
    from ..sql_helper.globals import get_all_gvars

    applied = 0
    for key, value in (get_all_gvars() or {}).items():
        key = str(key)
        if not key.startswith(CONFIG_PREFIX):
            continue
        name = key[len(CONFIG_PREFIX):]
        if not name or _is_secret_key(name):
            continue
        try:
            parsed = json.loads(value)
        except Exception:
            parsed = value
        setattr(Config, name, parsed)
        applied += 1
    return applied


async def _find_backup_messages(client, chat_id):
    try:
        found = await client.get_messages(chat_id, search=BACKUP_MARKER, limit=20)
    except Exception as e:
        LOGS.debug("تعذر البحث عن النسخة الاحتياطية: %s", e)
        return []
    messages = []
    for message in found or []:
        caption = message.message or ""
        if message.document and BACKUP_MARKER in caption:
            messages.append(message)
    return messages


def is_backup_message(message) -> bool:
    """True when a message is one of our settings backup documents."""
    return bool(
        message is not None
        and getattr(message, "document", None)
        and BACKUP_MARKER in (getattr(message, "message", None) or "")
    )


async def _resolve_backup_message(client, chat_id, message_id=None, reply_message=None):
    """Pick a backup by reply, by numeric id, or fall back to the newest one."""
    if reply_message is not None:
        return reply_message if is_backup_message(reply_message) else None
    if message_id:
        try:
            found = await client.get_messages(chat_id, ids=[int(message_id)])
        except Exception as e:
            LOGS.debug("تعذر جلب النسخة الاحتياطية بالمعرّف: %s", e)
            return None
        if found and is_backup_message(found[0]):
            return found[0]
        return None
    backups = await _find_backup_messages(client, chat_id)
    return max(backups, key=lambda message: message.id) if backups else None


async def _delete_old_backups(client, chat_id, keep_id=None):
    for message in await _find_backup_messages(client, chat_id):
        if keep_id is not None and message.id == keep_id:
            continue
        try:
            await message.delete()
        except Exception as e:
            LOGS.debug("تعذر حذف نسخة احتياطية قديمة: %s", e)


async def restore_settings_if_empty(
    client, force: bool = False, message_id=None, reply_message=None
) -> bool:
    """Restore settings/config from the log channel.

    Normally runs only on an empty database. ``force=True`` is used by the
    owner's explicit restore command. A specific backup can be chosen with
    ``message_id`` or by replying to its document with ``reply_message``.
    """
    from ..sql_helper.globals import addgvar, get_all_gvars, gvarstatus

    if gvarstatus(BACKUP_RESTORED_GVAR) and not force:
        return False
    existing = {
        str(key): value
        for key, value in (get_all_gvars() or {}).items()
        if str(key) not in _BACKUP_INTERNAL_KEYS
        and not str(key).startswith(CONFIG_PREFIX)
    }
    if existing and not force:
        return False

    chat_id, _ = await ensure_log_channel(client)
    if not chat_id:
        return False
    chosen = await _resolve_backup_message(
        client, chat_id, message_id=message_id, reply_message=reply_message
    )
    if not chosen:
        return False

    fd, temp_path = tempfile.mkstemp(prefix="t3rmx-backup-", suffix=".json")
    os.close(fd)
    try:
        await chosen.download_media(file=temp_path)
        data = json.loads(Path(temp_path).read_text(encoding="utf-8"))
    except Exception as e:
        LOGS.debug("تعذر قراءة النسخة الاحتياطية: %s", e)
        return False
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass

    restored = 0
    for key, value in (data.get("settings") or {}).items():
        key = str(key)
        if key in _BACKUP_INTERNAL_KEYS or key.startswith(CONFIG_PREFIX) or _is_secret_key(key):
            continue
        addgvar(key, str(value))
        restored += 1

    for key, value in (data.get("config") or {}).items():
        if not key or _is_secret_key(str(key)):
            continue
        addgvar(CONFIG_PREFIX + str(key), json.dumps(_jsonable(value)))
        setattr(Config, str(key), _jsonable(value))

    addgvar(BACKUP_RESTORED_GVAR, "1")
    addgvar(BACKUP_MSG_GVAR, str(chosen.id))
    addgvar(BACKUP_FP_GVAR, str(data.get("fingerprint") or ""))
    await _delete_old_backups(client, chat_id, keep_id=chosen.id)
    LOGS.info(
        "تمت استعادة الإعدادات من النسخة الاحتياطية %s (%d مفاتيح)",
        chosen.id,
        restored,
    )
    return True


async def refresh_backup(client, force: bool = False) -> bool:
    """Upload a fresh settings/config backup, removing older backup messages."""
    from ..sql_helper.globals import addgvar, gvarstatus

    chat_id, _ = await ensure_log_channel(client)
    if not chat_id:
        return False

    payload = _build_payload()
    fingerprint = payload["fingerprint"]
    stored_id = gvarstatus(BACKUP_MSG_GVAR)
    if not force and gvarstatus(BACKUP_FP_GVAR) == fingerprint and stored_id:
        try:
            existing = await client.get_messages(chat_id, ids=[int(stored_id)])
            if existing and (existing[0].message or "").find(BACKUP_MARKER) >= 0:
                return False
        except Exception:
            pass

    fd, temp_path = tempfile.mkstemp(prefix="t3rmx-backup-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2)
        message = await client.send_file(
            chat_id,
            temp_path,
            force_document=True,
            caption=f"{BACKUP_MARKER} {fingerprint}",
        )
    except Exception as e:
        LOGS.debug("تعذر رفع النسخة الاحتياطية: %s", e)
        return False
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass

    for key, value in (payload.get("config") or {}).items():
        addgvar(CONFIG_PREFIX + str(key), json.dumps(_jsonable(value)))
    addgvar(BACKUP_RESTORED_GVAR, "1")
    addgvar(BACKUP_FP_GVAR, fingerprint)
    addgvar(BACKUP_MSG_GVAR, str(message.id))
    await _delete_old_backups(client, chat_id, keep_id=message.id)
    LOGS.info("تم تحديث النسخة الاحتياطية للإعدادات")
    return True


async def delete_backups(client, message_id=None, reply_message=None) -> int:
    """Delete a chosen backup (or all backups) from the log channel."""
    from ..sql_helper.globals import delgvar, gvarstatus

    chat_id, _ = await ensure_log_channel(client)
    if not chat_id:
        return 0

    specific = message_id is not None or reply_message is not None
    if specific:
        chosen = await _resolve_backup_message(
            client, chat_id, message_id=message_id, reply_message=reply_message
        )
        targets = [chosen] if chosen else []
    else:
        targets = await _find_backup_messages(client, chat_id)

    stored_id = str(gvarstatus(BACKUP_MSG_GVAR) or "")
    deleted = 0
    for message in targets:
        try:
            await message.delete()
            deleted += 1
        except Exception as e:
            LOGS.debug("تعذر حذف النسخة الاحتياطية: %s", e)

    if not specific or (targets and stored_id == str(targets[0].id)):
        for key in (BACKUP_MSG_GVAR, BACKUP_FP_GVAR, BACKUP_RESTORED_GVAR):
            delgvar(key)
    LOGS.info("تم حذف نسخ الإعدادات الاحتياطية (%d)", deleted)
    return deleted
