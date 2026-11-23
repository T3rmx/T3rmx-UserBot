import asyncio
import glob
import os
import sys
import urllib.request
from datetime import timedelta
from pathlib import Path

import requests
from telethon import Button, functions, types, utils

from JoKeRUB import BOTLOG, BOTLOG_CHATID, PM_LOGGER_GROUP_ID
from ..Config import Config

def _env_truthy(name: str) -> bool:
    val = os.environ.get(name)
    return bool(val and str(val).strip())


def _missing_required_config():
    """Return missing required runtime variables (without exposing values)."""
    missing = []

    app_id = getattr(Config, "APP_ID", 0)
    try:
        app_id_ok = int(app_id) > 0
    except Exception:
        app_id_ok = False
    if not app_id_ok and not (_env_truthy("APP_ID") or _env_truthy("API_ID")):
        missing.append("APP_ID (or API_ID)")

    if not (getattr(Config, "API_HASH", None) and str(getattr(Config, "API_HASH", "")).strip()):
        missing.append("API_HASH")

    if not (getattr(Config, "STRING_SESSION", None) and str(getattr(Config, "STRING_SESSION", "")).strip()):
        missing.append("STRING_SESSION")

    if not (getattr(Config, "TG_BOT_TOKEN", None) and str(getattr(Config, "TG_BOT_TOKEN", "")).strip()):
        missing.append("TG_BOT_TOKEN")

    tg_user = getattr(Config, "TG_BOT_USERNAME", None)
    if not (tg_user and str(tg_user).strip()):
        missing.append("TG_BOT_USERNAME")

    # Owner ID is required for safe privileged-command control in deployed instances.
    env_owner = os.environ.get("T3RMX_OWNER_ID") or os.environ.get("OWNER_ID")
    try:
        owner_val = int(str(env_owner).strip()) if env_owner and str(env_owner).strip() else int(getattr(Config, "T3RMX_OWNER_ID", 0) or getattr(Config, "OWNER_ID", 0) or 0)
    except Exception:
        owner_val = 0
    if owner_val <= 0:
        missing.append("T3RMX_OWNER_ID")

    # Hosted/template deployments must use a persistent PostgreSQL database.
    hosted_keys = ("RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID", "RAILWAY_SERVICE_ID", "DYNO", "RENDER", "RENDER_SERVICE_ID", "KUBERNETES_SERVICE_HOST")
    on_hosted = any(os.environ.get(k) for k in hosted_keys)
    require_pg = on_hosted or str(os.environ.get("T3RMX_REQUIRE_POSTGRES", "") or "").strip().lower() in {"1", "true", "yes", "on"}
    if require_pg:
        db_uri = getattr(Config, "DB_URI", None) or os.environ.get("DATABASE_URL") or os.environ.get("DB_URI")
        if not (db_uri and str(db_uri).strip()):
            missing.append("DATABASE_URL")
        else:
            dbs = str(db_uri).strip().lower()
            if dbs.startswith("sqlite:"):
                missing.append("DATABASE_URL (PostgreSQL required; SQLite is not durable in hosted deployments)")

    return missing


def validate_runtime_config():
    missing = _missing_required_config()
    if missing:
        raise RuntimeError(
            "Missing or invalid required configuration: "
            + ", ".join(missing)
            + ". Set the required environment variables and redeploy."
        )

from aiohttp import web
from ..core.web_server import web_server
from ..core.logger import logging
from ..core.session import l313l
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from .pluginmanager import load_module
from .tools import create_supergroup

LOGS = logging.getLogger("t3rmx.startup")
logging.getLogger("telethon").setLevel(logging.WARNING)

cmdhr = Config.COMMAND_HAND_LER
bot = l313l
ENV = bool(os.environ.get("ENV", False))

if ENV:
    VPS_NOLOAD = ["سيرفر"]
elif os.path.exists("config.py"):
    VPS_NOLOAD = ["هيروكو"]
else:
    VPS_NOLOAD = []


async def setup_bot():
    """Initialize the user session and local web server (for health/bind where needed)."""
    validate_runtime_config()
    await l313l.connect()
    try:
        config = await l313l(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == l313l.session.server_address:
                if l313l.session.dc_id != option.id:
                    LOGS.warning(
                        f"Fixed DC mismatch in session: {l313l.session.dc_id} -> {option.id}"
                    )
                l313l.session.set_dc(option.id, option.ip_address, option.port)
                l313l.session.save()
                break
    except Exception as e:
        LOGS.debug(f"DC config check skipped: {e}")

    # Resolve bot username if assistant bot is available
    try:
        if getattr(l313l, "tgbot", None):
            bot_details = await l313l.tgbot.get_me()
            if getattr(bot_details, "username", None):
                Config.TG_BOT_USERNAME = bot_details.username  # normalized without @
    except Exception as e:
        LOGS.debug(f"Assistant bot username resolution skipped: {e}")

    # Optional web bind (useful for some platforms); safe best-effort
    try:
        if Config.PORT:
            app = web.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            redaport = int(Config.PORT)
            await web.TCPSite(app, bind_address, redaport).start()
    except Exception as e:
        LOGS.debug(f"Web server bind skipped: {e}")

    l313l.me = await l313l.get_me()
    l313l.uid = utils.get_peer_id(l313l.me)
    if getattr(l313l, "tgbot", None):
        try:
            l313l.tgbot.uid = utils.get_peer_id(await l313l.tgbot.get_me())
        except Exception:
            pass
    if getattr(Config, "OWNER_ID", 0) == 0:
        Config.OWNER_ID = l313l.uid


async def startupmessage():
    await register_vc_interface()
    """Send startup message to configured logger chat (if enabled)."""
    try:
        if BOTLOG and getattr(Config, "BOTLOG_CHATID", None):
            display = getattr(Config, "T3RMX_DISPLAY_NAME", "T3rmx UserBot")
            repo = getattr(Config, "T3RMX_REPOSITORY", "https://github.com/T3rmx/T3rmx-UserBot")
            logo = getattr(Config, "T3RMX_LOGO", "assets/branding/t3rmx-logo.jpg")
            caption = (
                f"**{display} is running successfully.**\n"
                f"Repository: {repo}\n"
                f"Send `{cmdhr}الاوامر` or `{cmdhr}help` to view commands."
            )
            try:
                Config.CATUBLOGO = await l313l.tgbot.send_file(
                    BOTLOG_CHATID,
                    logo,
                    caption=caption,
                )
            except Exception:
                await l313l.send_message(BOTLOG_CHATID, caption)
    except Exception as e:
        LOGS.debug(f"Startup message not sent: {e}")
        return None

    # Resume restart/update notifications (in-session state)
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
        else:
            return None
    except Exception:
        return None
    try:
        if msg_details:
            await l313l.check_testcases()
            message = await l313l.get_messages(msg_details[0], ids=msg_details[1])
            text = (message.text or "") + "\n\n**T3rmx UserBot restarted successfully.**"
            await l313l.edit_message(msg_details[0], msg_details[1], text)
            if gvarstatus("restartupdate") is not None:
                await l313l.send_message(
                    msg_details[0],
                    f"{cmdhr}ping",
                    reply_to=msg_details[1],
                    schedule=timedelta(seconds=10),
                )
            del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.debug(f"Restart update notice skipped: {e}")
        return None


async def mybot():
    """Initialize assistant bot identity/customization if possible (safe, optional)."""
    try:
        if not getattr(l313l, "tgbot", None):
            return
        starkbot = await l313l.tgbot.get_me()
        bot_name = starkbot.first_name or ""
        botname = f"@{starkbot.username}" if getattr(starkbot, "username", None) else None
        if bot_name.endswith("Assistant") or bot_name.endswith("assistant"):
            LOGS.info("Assistant bot is ready.")
        # No forced BotFather interactions or branding mutations by default.
    except Exception as e:
        LOGS.debug(f"Assistant customization skipped: {e}")


async def add_bot_to_logger_group(chat_id):
    """Best-effort add assistant bot to configured logger group."""
    if not getattr(l313l, "tgbot", None):
        return
    try:
        bot_details = await l313l.tgbot.get_me()
    except Exception:
        return
    try:
        await l313l(
            functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await l313l(
                functions.channels.InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.debug(f"Could not add assistant bot to logger group: {e}")


async def saves():
    """Reserved for explicit, safe startup actions.

    Legacy auto-joins to external channels are disabled by default.
    """
    return


async def load_plugins(folder, extfolder=None):
    """Load in-repo plugins/modules."""
    if extfolder:
        path = f"{extfolder}/*.py"
        plugin_path = extfolder
    else:
        path = f"JoKeRUB/{folder}/*.py"
        plugin_path = f"JoKeRUB/{folder}"
    files = glob.glob(path)
    files.sort()
    success = 0
    failure = []
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            pluginname = shortname.replace(".py", "")
            try:
                if (pluginname not in Config.NO_LOAD) and (
                    pluginname not in VPS_NOLOAD
                ):
                    flag = True
                    check = 0
                    while flag:
                        try:
                            load_module(
                                pluginname,
                                plugin_path=plugin_path,
                            )
                            if shortname in failure:
                                failure.remove(shortname)
                            success += 1
                            break
                        except ModuleNotFoundError as e:
                            # Runtime dependency installation is disabled by default for safety.
                            if getattr(Config, "T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False):
                                try:
                                    from ..helpers.utils import install_pip
                                    install_pip(e.name)
                                    check += 1
                                    continue
                                except Exception:
                                    pass
                            check += 1
                            if shortname not in failure:
                                failure.append(shortname)
                            LOGS.warning(
                                f"Could not load {shortname}: missing optional dependency module {getattr(e, 'name', None) or e} (path: {plugin_path})"
                            )
                            if check > 1:
                                break
                else:
                    # Respect NO_LOAD without deleting source files.
                    pass
            except Exception as e:
                if shortname not in failure:
                    failure.append(shortname)
                LOGS.info(
                    f"Could not load {shortname}: {e} (path: {plugin_path})"
                )
    if extfolder and getattr(Config, "BOTLOG", False) and getattr(Config, "BOTLOG_CHATID", None):
        if not failure:
            failure.append("None")
        try:
            await l313l.tgbot.send_message(
                BOTLOG_CHATID,
                f"External modules loaded: {success}\nFailed: {', '.join(failure)}",
            )
        except Exception:
            pass


async def aljoker_the_best(client, group_name):
    async for dialog in client.iter_dialogs():
        if dialog.is_group and dialog.title == group_name:
            return dialog.id
    return None



async def register_vc_interface():
    """Register preserved VC/music command interface with graceful unavailable handling."""
    try:
        try:
            from t3rmx_vc.commands import register_vc_commands
        except Exception:
            from T3rmx_VC.t3rmx_vc.commands import register_vc_commands
        n = register_vc_commands(l313l)
        LOGS.debug(f"T3rmx-VC command interface registered ({n})")
    except Exception as e:
        LOGS.debug(f"VC command registration skipped: {e}")

async def verifyLoggerGroup():
    """Validate configured logger groups.

    Automatic creation of supergroups is opt-in via T3RMX_ENABLE_AUTO_LOG_GROUPS.
    """
    flag = False

    # Create a private log channel once. Only short text alerts go there;
    # the full log file is sent only when the owner uses /log.
    if getattr(Config, "T3RMX_AUTO_LOG_CHANNEL", True):
        try:
            from ..utils.logchannel import ensure_log_channel
            log_channel_id = await ensure_log_channel(l313l)
            if log_channel_id and not getattr(Config, "BOTLOG", False):
                addgvar("PRIVATE_GROUP_BOT_API_ID", str(log_channel_id))
                flag = True
        except Exception as e:
            LOGS.debug(f"Auto log channel creation skipped: {e}")

    if BOTLOG:
        try:
            entity = await l313l.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, types.User) and getattr(entity, "default_banned_rights", None):
                if getattr(entity.default_banned_rights, "send_messages", None):
                    LOGS.info("Missing send permissions in configured BOTLOG chat.")
                if getattr(entity.default_banned_rights, "invite_users", None):
                    LOGS.info("Missing invite permissions in configured BOTLOG chat.")
        except Exception as e:
            LOGS.debug(f"BOTLOG validation skipped: {e}")
    else:
        if getattr(Config, "T3RMX_ENABLE_AUTO_LOG_GROUPS", False):
            try:
                group_title = f"{getattr(Config, 'T3RMX_DISPLAY_NAME', 'T3rmx')} Logs"
                botlog_group_id = await aljoker_the_best(l313l, group_title)
                if botlog_group_id:
                    addgvar("PRIVATE_GROUP_BOT_API_ID", botlog_group_id)
                else:
                    _, groupid = await create_supergroup(
                        group_title, l313l, Config.TG_BOT_USERNAME, "T3rmx UserBot log group", None
                    )
                    addgvar("PRIVATE_GROUP_BOT_API_ID", groupid)
                flag = True
            except Exception as e:
                LOGS.debug(f"Auto log group creation skipped: {e}")

    if PM_LOGGER_GROUP_ID == -100 and getattr(Config, "T3RMX_ENABLE_AUTO_LOG_GROUPS", False):
        try:
            group_title = f"{getattr(Config, 'T3RMX_DISPLAY_NAME', 'T3rmx')} PM Storage"
            pm_logger_group_id = await aljoker_the_best(l313l, group_title)
            if pm_logger_group_id:
                addgvar("PM_LOGGER_GROUP_ID", pm_logger_group_id)
            else:
                _, groupid = await create_supergroup(
                    group_title, l313l, Config.TG_BOT_USERNAME, "T3rmx UserBot PM storage group", None
                )
                addgvar("PM_LOGGER_GROUP_ID", groupid)
            flag = True
        except Exception as e:
            LOGS.debug(f"Auto PM log group creation skipped: {e}")

    if flag:
        executable = sys.executable.replace(" ", "\\ ")
        args = [executable, "-m", "JoKeRUB"]
        os.execle(executable, *args, os.environ)
        sys.exit(0)


async def install_externalrepo(repo, branch, cfolder):
    """Disabled by default for safety.

    External runtime code installation is not performed unless explicitly enabled.
    This preserves the interface for compatibility but avoids unverified fetch/exec.
    """
    if not getattr(Config, "T3RMX_ALLOW_EXTERNAL_REPOS", False):
        msg = (
            "External repository installation is disabled by default for security. "
            "Use in-repo modules (e.g. T3rmx-VC) or enable explicitly only with a trusted source."
        )
        LOGS.warning(msg)
        try:
            if getattr(Config, "BOTLOG", False) and getattr(Config, "BOTLOG_CHATID", None):
                await l313l.tgbot.send_message(BOTLOG_CHATID, msg)
        except Exception:
            pass
        return
    # Even when enabled, require explicit branch and avoid auto pip installs by default.
    # Implementation intentionally conservative.
    LOGS.warning("External repository installation requested but is not automatically executed in this build.")
    return
