

import asyncio
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Optional

from JoKeRUB import l313l
from ..Config import Config
from ..core.auth import authorized_for_update
from ..core.managers import edit_delete, edit_or_reply

plugin_category = "tools"


def _current_version() -> str:
    for attr in ("T3RMX_VERSION", "__version__", "JEPVERSION"):
        try:
            import JoKeRUB
            v = getattr(JoKeRUB, attr, None)
            if v:
                return str(v)
        except Exception:
            pass
    return "unknown"


def _parse_version_tuple(value: str):
    if not value:
        return (0,)
    nums = re.findall(r"\d+", str(value).strip())
    if not nums:
        return (0,)
    return tuple(int(x) for x in nums)


def _repo() -> str:
    return (
        getattr(Config, "T3RMX_GITHUB_REPO", None)
        or getattr(Config, "UPSTREAM_REPO", None)
        or "T3rmx/T3rmx-UserBot"
    ).strip().strip("/")


def _branch() -> str:
    return (getattr(Config, "UPSTREAM_REPO_BRANCH", None) or "main").strip() or "main"


def _local_commit() -> str:
    # Prefer deployment-provided commit SHA, then local git.
    for key in (
        "RAILWAY_GIT_COMMIT_SHA",
        "SOURCE_COMMIT",
        "GIT_COMMIT_SHA",
        "COMMIT_SHA",
        "HEROKU_SLUG_COMMIT",
    ):
        val = os.environ.get(key)
        if val:
            return str(val).strip()[:12]
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).strip()
        if out:
            return out[:12]
    except Exception:
        pass
    return "unknown"


def _github_json(url: str, timeout: int = 12):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "T3rmx-UserBot-Updater",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8", errors="ignore")
        return json.loads(data), None
    except urllib.error.HTTPError as e:
        code = getattr(e, "code", "error")
        try:
            body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        detail = f"HTTP {code}"
        if body:
            detail += f": {body[:120]}"
        return None, detail
    except Exception as e:
        return None, str(e)


def _fetch_latest_code(repo: str, branch: str):
    # Updates come from repository code (commits), not GitHub releases.
    commit, err = _github_json(
        f"https://api.github.com/repos/{repo}/commits/{branch}"
    )
    if commit is None:
        return {"__error__": err or "Could not fetch latest commit"}

    info = {
        "sha": (commit.get("sha") or "")[:12],
        "message": ((commit.get("commit") or {}).get("message") or "").split("\n", 1)[0],
        "date": ((commit.get("commit") or {}).get("author") or {}).get("date")
        or ((commit.get("commit") or {}).get("committer") or {}).get("date")
        or "unknown",
        "url": commit.get("html_url") or f"https://github.com/{repo}/commits/{branch}",
        "branch": branch,
    }

    # Optional: read T3RMX_VERSION from repo code to show code version.
    raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/T3rmx-UserBot/JoKeRUB/t3rmx_config.py"
    req = urllib.request.Request(raw_url, headers={"User-Agent": "T3rmx-UserBot-Updater"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        m = re.search(r'T3RMX_VERSION\s*=\s*(?:get_str\([^,]+,\s*)?"([^"]+)"', raw)
        if not m:
            m = re.search(r'__version__\s*=\s*"([^"]+)"', raw)
        if m:
            info["remote_version"] = m.group(1).strip()
    except Exception:
        pass

    # Also check releases presence for informational context (not source of truth).
    rel, _ = _github_json(f"https://api.github.com/repos/{repo}/releases/latest")
    if isinstance(rel, dict) and rel.get("tag_name"):
        info["latest_release_tag"] = rel.get("tag_name")
        info["latest_release_url"] = rel.get("html_url")

    return info


def _is_apply_request(arg: str) -> bool:
    return arg in {
        "تنفيذ",
        "الان",
        "الآن",
        "نفذ",
        "apply",
        "install",
        "now",
        "update",
        "upgrade",
    }


@l313l.ar_cmd(
    pattern=r"تحديث(?:\s+(.*))?$",
    command=("تحديث", plugin_category),
    info={
        "header": "Check for T3rmx UserBot updates from repository code (GitHub commits, safe).",
        "description": "Shows current vs latest code on the configured branch. Updates are tracked in code, not releases.",
        "options": {
            "تنفيذ/الان": "Owner-only: apply code update when a git checkout is available, otherwise show safe redeploy instructions."
        },
        "usage": ["{tr}تحديث", "{tr}تحديث الان", "{tr}تحديث تنفيذ"],
    },
)
async def check_updates(event):
    arg = (event.pattern_match.group(1) or "").strip().lower()
    msg = await edit_or_reply(event, "**Checking T3rmx UserBot code updates...**")

    repo = _repo()
    branch = _branch()
    current_version = _current_version()
    local_commit = _local_commit()

    latest = await asyncio.to_thread(_fetch_latest_code, repo, branch)
    if not latest:
        return await edit_delete(msg, "**Could not check updates (no response).**", 20)

    if latest.get("__error__"):
        return await edit_delete(
            msg,
            f"**Update check failed:** `{latest.get('__error__')}`\n"
            f"Repository: `{repo}` (branch `{branch}`)",
            25,
        )

    remote_commit = latest.get("sha") or "unknown"
    remote_version = latest.get("remote_version")
    commit_url = latest.get("url") or f"https://github.com/{repo}/commits/{branch}"

    if local_commit != "unknown" and remote_commit != "unknown":
        if local_commit.lower().startswith(remote_commit.lower()) or remote_commit.lower().startswith(local_commit.lower()):
            status = "Up to date (code)"
        else:
            status = "Update available in code"
    elif remote_version and _parse_version_tuple(remote_version) > _parse_version_tuple(current_version):
        status = "Update available in code"
    elif remote_version and _parse_version_tuple(remote_version) == _parse_version_tuple(current_version):
        status = "Likely up to date (version match)"
    else:
        status = "Code update status checked"

    lines = [
        f"**{getattr(Config, 'T3RMX_DISPLAY_NAME', 'T3rmx UserBot')} Update Check**",
        "",
        f"• Repository: `{repo}`",
        f"• Branch: `{branch}`",
        f"• Current version: `{current_version}`",
        f"• Current commit: `{local_commit}`",
        f"• Latest code commit: `{remote_commit}`",
        f"• Commit date: `{latest.get('date', 'unknown')}`",
        f"• Status: **{status}**",
        f"• Latest commit: {commit_url}",
    ]
    if remote_version:
        lines.append(f"• Latest code version: `{remote_version}`")
    if latest.get("message"):
        lines.append(f"• Latest change: `{latest.get('message')}`")
    if latest.get("latest_release_tag"):
        lines.append(
            f"• Latest release (info only): `{latest.get('latest_release_tag')}` {latest.get('latest_release_url', '')}".rstrip()
        )
    else:
        lines.append("• Releases: _not used as update source; updates come from code commits_")

    lines.extend(
        [
            "",
            "_Security note: checks read repository metadata only. No pip install or arbitrary code execution is performed._",
        ]
    )

    if _is_apply_request(arg):
        if not authorized_for_update(event.sender_id):
            lines.append("\n**Execution request denied:** only the configured owner can request update actions.")
        else:
            lines.append("\n**Owner action (apply update):**")
            applied = False
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            git_dir = os.path.join(repo_root, ".git")
            if os.path.isdir(git_dir):
                try:
                    # Safe, reviewed-source code update for git-based deployments only.
                    pull = await asyncio.to_thread(
                        subprocess.run,
                        ["git", "pull", "--ff-only", "origin", branch],
                        cwd=repo_root,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    out = (pull.stdout or "").strip()
                    err = (pull.stderr or "").strip()
                    detail = (out + ("\n" + err if err else "")).strip() or "git pull completed"
                    if pull.returncode == 0:
                        lines.append(f"• Git code update: success (`{branch}`)\n```\n{detail[:1200]}\n```")
                        lines.append("• Restarting to apply updated code...")
                        await msg.edit("\n".join(lines), link_preview=False)
                        await asyncio.sleep(2)
                        executable = sys.executable.replace(" ", "\\ ")
                        args = [executable, "-m", "JoKeRUB"]
                        os.execle(executable, *args, os.environ)
                        return
                    else:
                        lines.append(f"• Git code update failed (no automatic changes applied):\n```\n{detail[:1200]}\n```")
                        applied = True  # attempted; provide guidance below
                except Exception as e:
                    lines.append(f"• Git code update attempt failed safely: `{e}`")
                    applied = True

            if not applied:
                # Railway/container deployments usually have no .git checkout; redeploy from latest code.
                lines.extend(
                    [
                        "• This deployment does not expose a writable git checkout; apply update by redeploying from latest repository code:",
                        "  - Railway: redeploy/rebuild the app service from the latest `main` commit of the configured repository.",
                        "  - Docker/VPS (git): `git pull --ff-only origin " + branch + "` in the reviewed source, then restart the service.",
                        "  - Docker image: rebuild from latest source/tag and recreate the container.",
                        "• Ensure dependencies come from pinned manifests in the repository, then restart/redeploy.",
                    ]
                )

    await msg.edit("\n".join(lines), link_preview=False)
