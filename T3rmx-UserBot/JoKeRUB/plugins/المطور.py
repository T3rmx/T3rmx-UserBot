# T3rmx UserBot - المطور / Developer controls
# Preserves sec/developer-control mechanism restricted to the configured T3rmx owner.

import asyncio
import io
import os
import re
import sys
import time
from pathlib import Path

from telethon import events
from telethon.tl import functions

from JoKeRUB import StartTime, l313l
from ..Config import Config
from ..core.auth import authorized_for_sec, is_owner
from ..helpers.functions import catalive, check_data_base_heal_th, get_readable_time
from ..helpers.utils import reply_id
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import mention

plugin_category = "tools"


def _t3rmx_info_text():
    name = getattr(Config, "T3RMX_DISPLAY_NAME", "T3rmx UserBot")
    repo = getattr(Config, "T3RMX_REPOSITORY", "https://github.com/T3rmx/T3rmx-UserBot")
    owner = getattr(Config, "T3RMX_OWNER_USERNAME", "vvsks")
    try:
        from ..core.auth import owner_id as _owner_id
        owner_id = _owner_id()
    except Exception:
        owner_id = getattr(Config, "T3RMX_OWNER_ID", 6023224495)
    updates = getattr(Config, "T3RMX_UPDATES_CHANNEL", "")
    support = getattr(Config, "T3RMX_SUPPORT_GROUP", "") or getattr(Config, "T3RMX_SUPPORT_CHANNEL", "")
    lines = [
        f"**{name} - Developer / Owner**",
        "━━━━━━━━━━━━━━━━",
        f"• Owner: @{owner}",
        f"• Owner ID: `{owner_id}`",
        f"• Repository: {repo}",
    ]
    if updates:
        lines.append(f"• Updates: {updates}")
    if support:
        lines.append(f"• Support: {support}")
    lines.append("━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


@l313l.ar_cmd(
    pattern="المطور$",
    command=("المطور", plugin_category),
    info={
        "header": "Show T3rmx owner/developer information",
        "usage": ["{tr}المطور"],
    },
)
async def show_developer(event):
    reply_to_id = await reply_id(event)
    logo = getattr(Config, "T3RMX_LOGO", "assets/branding/t3rmx-logo.jpg")
    caption = _t3rmx_info_text()
    try:
        if logo and os.path.exists(logo):
            await event.client.send_file(event.chat_id, logo, caption=caption, reply_to=reply_to_id)
            await event.delete()
            return
    except Exception:
        pass
    await event.client.send_message(event.chat_id, caption, reply_to=reply_to_id, link_preview=False)
    try:
        await event.delete()
    except Exception:
        pass


@l313l.tgbot.on(events.CallbackQuery(data=re.compile(b"stats")))
async def on_stats_callback(event):
    try:
        statstext = await catalive(StartTime)
    except Exception:
        statstext = "T3rmx UserBot is running."
    await event.answer(statstext, cache_time=0, alert=True)


# --- Developer-only controls (sec mechanism, restricted to configured owner) ---

@l313l.ar_cmd(
    pattern=r"sec( -a)?(?:\s|$)([\s\S]*)",
    command=("sec", plugin_category),
    info={
        "header": "Owner-only: execute a shell command on the host (use with extreme caution).",
        "options": {"-a": "Show ANSI-like output as file/text when needed."},
        "usage": ["{tr}sec <command>", "{tr}sec -a <command>"],
    },
)
async def _(event):
    if not authorized_for_sec(event.sender_id):
        return await event.edit("**This command is restricted to the T3rmx owner.**")

    cmd = (event.pattern_match.group(2) or "").strip()
    if not cmd:
        return await event.edit("**Usage:** `.sec <command>`")

    await event.edit("`Running...`")
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        out = (stdout or b"").decode(errors="ignore")
        err = (stderr or b"").decode(errors="ignore")
        text = out + ("\n" + err if err else "")
        text = text.strip() or "(no output)"
        if len(text) > 4000:
            with io.BytesIO(text.encode(errors="ignore")) as f:
                f.name = "sec-output.txt"
                await event.client.send_file(event.chat_id, f, caption=f"`$ {cmd}`", reply_to=event.id)
            await event.edit("`Output sent as file.`")
        else:
            await event.edit(f"**Command:** `{cmd}`\n**Exit:** `{proc.returncode}`\n\n```\n{text}\n```")
    except Exception as e:
        await event.edit(f"**Error:** `{e}`")


@l313l.ar_cmd(
    pattern=r"تقييد(?:\s|$)([\s\S]*)",
    command=("تقييد", plugin_category),
    info={
        "header": "Owner-only: restrict/unrestrict this userbot instance for non-owner users.",
        "usage": ["{tr}تقييد on", "{tr}تقييد off", "{tr}تقييد"],
    },
)
async def _(event):
    if not is_owner(event.sender_id):
        return await event.edit("**This command is restricted to the T3rmx owner.**")
    arg = (event.pattern_match.group(1) or "").strip().lower()
    if arg in {"on", "1", "yes", "true", "تفعيل"}:
        addgvar("blockedfrom", "yes")
        return await event.edit("**Restriction enabled for non-owner users on this instance.**")
    if arg in {"off", "0", "no", "false", "تعطيل"}:
        delgvar("blockedfrom")
        return await event.edit("**Restriction disabled.**")
    status = "enabled" if gvarstatus("blockedfrom") == "yes" else "disabled"
    await event.edit(f"**Current restriction status:** `{status}`\nUse `.تقييد on` / `.تقييد off`.")


@l313l.ar_cmd(
    pattern=r"اعادة تشغيل$",
    command=("اعادة تشغيل", plugin_category),
    info={"header": "Owner-only: restart the bot process.", "usage": ["{tr}اعادة تشغيل"]},
)
async def _(event):
    if not is_owner(event.sender_id):
        return await event.edit("**This command is restricted to the T3rmx owner.**")
    await event.edit("**Restarting T3rmx UserBot...**")
    await asyncio.sleep(1)
    executable = sys.executable.replace(" ", "\\ ")
    args = [executable, "-m", "JoKeRUB"]
    os.execle(executable, *args, os.environ)
