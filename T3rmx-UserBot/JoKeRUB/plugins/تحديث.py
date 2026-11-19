# T3rmx UserBot - Safe update checker (GitHub Releases)
# No auto-install, no git pull/pip/heroku mutation, no arbitrary downloads/execution.

import asyncio
import json
import re
import urllib.request
from typing import Optional

from JoKeRUB import l313l
from ..Config import Config
from ..core.auth import authorized_for_update, is_owner
from ..core.managers import edit_delete, edit_or_reply

plugin_category = "tools"


def _current_version() -> str:
    # Prefer explicit T3rmx version; fall back to legacy attributes
    for attr in ("T3RMX_VERSION", "__version__", "JEPVERSION"):
        try:
            import JoKeRUB
            v = getattr(JoKeRUB, attr, None)
            if v:
                return str(v)
        except Exception:
            pass
    return "unknown"


def _parse_tag(tag: str):
    # Extract numeric parts for simple comparison; keep original for display
    if not tag:
        return (0,)
    s = str(tag).strip()
    nums = re.findall(r"\d+", s)
    if not nums:
        return (0,)
    return tuple(int(x) for x in nums)


def _fetch_latest_release(repo: str, timeout: int = 10) -> Optional[dict]:
    # repo format: owner/name
    repo = (repo or "T3rmx/T3rmx-UserBot").strip().strip("/")
    api = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        api,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "T3rmx-UserBot-Updater",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8", errors="ignore")
        return json.loads(data)
    except urllib.error.HTTPError as e:
        # 404 typically means no releases yet
        if getattr(e, "code", None) == 404:
            return {"__no_releases__": True}
        return {"__error__": f"HTTP {getattr(e, 'code', 'error')}"}
    except Exception as e:
        return {"__error__": str(e)}


def _format_changelog(body: str, limit: int = 1500) -> str:
    body = (body or "").strip()
    if not body:
        return "_No changelog provided._"
    if len(body) > limit:
        return body[: limit - 20].rstrip() + "\n\n… (truncated)"
    return body


@l313l.ar_cmd(
    pattern=r"تحديث(?:\s+(.*))?$",
    command=("تحديث", plugin_category),
    info={
        "header": "Check for T3rmx UserBot updates via GitHub Releases (safe, read-only).",
        "description": "Shows current vs latest release and changelog. No automatic installation.",
        "options": {
            "تنفيذ": "Owner-only: show manual, safe update instructions for your deployment method."
        },
        "usage": ["{tr}تحديث", "{tr}تحديث تنفيذ"],
    },
)
async def check_updates(event):
    arg = (event.pattern_match.group(1) or "").strip().lower()
    msg = await edit_or_reply(event, "**Checking T3rmx UserBot releases...**")

    repo = getattr(Config, "T3RMX_GITHUB_REPO", "T3rmx/T3rmx-UserBot")
    current = _current_version()

    latest = await asyncio.to_thread(_fetch_latest_release, repo)
    if not latest:
        return await edit_delete(msg, "**Could not check updates (no response).**", 20)

    if latest.get("__no_releases__"):
        text = (
            f"**{getattr(Config, 'T3RMX_DISPLAY_NAME', 'T3rmx UserBot')} Update Check**\n\n"
            f"• Repository: `{repo}`\n"
            f"• Current version: `{current}`\n"
            f"• Latest release: `No releases published yet`\n\n"
            "No GitHub Release was found for this repository yet. "
            "When releases are published, you can check them here safely."
        )
        return await msg.edit(text)

    if latest.get("__error__"):
        return await edit_delete(msg, f"**Update check failed:** `{latest.get('__error__')}`", 20)

    tag = latest.get("tag_name") or latest.get("name") or "unknown"
    name = latest.get("name") or tag
    url = latest.get("html_url") or f"https://github.com/{repo}/releases"
    body = _format_changelog(latest.get("body") or "")
    published = latest.get("published_at") or latest.get("created_at") or "unknown"

    is_newer = _parse_tag(tag) > _parse_tag(current) and _parse_tag(tag) != (0,)
    is_same = str(tag).strip() == str(current).strip() or (
        _parse_tag(tag) == _parse_tag(current) and _parse_tag(tag) != (0,)
    )
    if is_same:
        status = "Up to date"
    elif is_newer:
        status = "Update available"
    else:
        status = "Release information available"

    text = (
        f"**{getattr(Config, 'T3RMX_DISPLAY_NAME', 'T3rmx UserBot')} Update Check**\n\n"
        f"• Repository: `{repo}`\n"
        f"• Current version: `{current}`\n"
        f"• Latest release: `{tag}` ({name})\n"
        f"• Published: `{published}`\n"
        f"• Status: **{status}**\n"
        f"• Release: {url}\n\n"
        f"**Changelog**\n{body}\n\n"
        "_Security note: updates are not installed automatically. "
        "No git pull, pip install, or arbitrary code execution is performed by this command._"
    )

    if arg in {"تنفيذ", "apply", "install", "now"}:
        if not authorized_for_update(event.sender_id):
            text += "\n\n**Execution request denied:** only the configured owner can request update actions."
        else:
            text += (
                "\n\n**Owner action (manual/safe):**\n"
                "1. Review the release and changelog.\n"
                "2. Update using your deployment method with the in-repo project files only:\n"
                "   - VPS/systemd or Linux: `git fetch --tags` (if using git) then checkout the reviewed release/tag and restart the service, or redeploy from the reviewed source.\n"
                "   - Docker: rebuild the image from the reviewed source/tag and recreate the container.\n"
                "   - Railway/Heroku: redeploy from the reviewed repository state/release.\n"
                "3. Ensure dependencies come from pinned manifests in the repository.\n"
                "4. Restart the bot after updating.\n\n"
                "Automatic in-place self-mutation is intentionally disabled."
            )

    await msg.edit(text, link_preview=False)
