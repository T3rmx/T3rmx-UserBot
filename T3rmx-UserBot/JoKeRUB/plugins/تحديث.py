
import asyncio
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from JoKeRUB import l313l
from ..Config import Config
from ..core.auth import authorized_for_update
from ..core.managers import edit_delete, edit_or_reply

plugin_category = "tools"

# Files that belong to this deployment and must never be replaced by an update.
_PROTECTED_NAMES = {
    "config.py",
    ".env",
    ".git",
    "session.txt",
    "aljoker_links.json",
}
_PROTECTED_SUFFIXES = (
    ".session",
    ".session-journal",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".log",
)


def _current_version() -> str:
    for attr in ("T3RMX_VERSION", "__version__", "JEPVERSION"):
        try:
            import JoKeRUB
            v = getattr(JoKeRUB, attr, None)
            if v:
                return str(v)
        except Exception:
            pass
    return "غير معروف"


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


def _repo_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _local_commit() -> str:
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
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=_repo_root(),
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        ).strip()
        if out:
            return out[:12]
    except Exception:
        pass
    return "غير معروف"


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
        code = getattr(e, "code", "خطأ")
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
    commit, err = _github_json(
        f"https://api.github.com/repos/{repo}/commits/{branch}"
    )
    if commit is None:
        return {"__error__": err or "تعذر جلب آخر تحديث"}

    info = {
        "sha": (commit.get("sha") or "")[:12],
        "message": ((commit.get("commit") or {}).get("message") or "").split("\n", 1)[0],
        "date": ((commit.get("commit") or {}).get("author") or {}).get("date")
        or ((commit.get("commit") or {}).get("committer") or {}).get("date")
        or "غير معروف",
        "url": commit.get("html_url") or f"https://github.com/{repo}/commits/{branch}",
        "branch": branch,
    }

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

    rel, _ = _github_json(f"https://api.github.com/repos/{repo}/releases/latest")
    if isinstance(rel, dict) and rel.get("tag_name"):
        info["latest_release_tag"] = rel.get("tag_name")
        info["latest_release_url"] = rel.get("html_url")

    return info


def _is_apply_request(arg: str) -> bool:
    return arg in {"تنفيذ", "الان", "الآن", "نفذ", "ثبت", "طبق"}


def _safe_extract(zip_file: zipfile.ZipFile, destination: str) -> None:
    base = os.path.realpath(destination)
    for member in zip_file.infolist():
        target = os.path.realpath(os.path.join(destination, member.filename))
        if target != base and not target.startswith(base + os.sep):
            raise RuntimeError("تم رفض ملف غير آمن داخل أرشيف التحديث")
        if member.is_dir():
            os.makedirs(target, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zip_file.open(member) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)


def _download_source(repo: str, branch: str):
    url = f"https://api.github.com/repos/{repo}/zipball/{branch}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "T3rmx-UserBot-Updater",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        payload = resp.read()

    tmp = tempfile.mkdtemp(prefix="t3rmx-update-")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        _safe_extract(archive, tmp)

    roots = [p for p in Path(tmp).iterdir() if p.is_dir()]
    if len(roots) == 1:
        return str(roots[0]), tmp
    return tmp, tmp


def _is_protected(relative_path: str) -> bool:
    parts = Path(relative_path).parts
    for part in parts:
        if part in _PROTECTED_NAMES or part.startswith(".git"):
            return True
    return relative_path.lower().endswith(_PROTECTED_SUFFIXES)


def _copy_tree(source: str, destination: str) -> int:
    copied = 0
    for root, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if not _is_protected(os.path.relpath(os.path.join(root, d), source))]
        for name in files:
            src = os.path.join(root, name)
            rel = os.path.relpath(src, source)
            if _is_protected(rel) or os.path.islink(src):
                continue
            dst = os.path.join(destination, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
    return copied


# Import name -> PyPI package name. Used to prove every required library is
# importable after pip finishes; a missing file or a failed install aborts the
# update instead of being silently skipped.
_REQUIRED_MODULES = {
    "telethon": "Telethon",
    "aiohttp": "aiohttp",
    "requests": "requests",
    "sqlalchemy": "SQLAlchemy",
    "psycopg2": "psycopg2-binary",
    "PIL": "Pillow",
    "yt_dlp": "yt-dlp",
    "dotenv": "python-dotenv",
    "bs4": "beautifulsoup4",
    "markdown": "Markdown",
    "emoji": "emoji",
    "fontTools": "fonttools",
    "lyricsgenius": "lyricsgenius",
    "user_agent": "user-agent",
}


def _find_requirements(root: str):
    for relative in ("requirements.txt", "T3rmx-UserBot/requirements.txt"):
        candidate = os.path.join(root, relative)
        if os.path.isfile(candidate):
            return candidate
    return None


def _install_requirements(root: str):
    """Install every pinned dependency. Never skip and never report false success."""
    requirements = _find_requirements(root)
    if not requirements:
        return False, "لم يتم العثور على requirements.txt في أحدث كود"

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        requirements,
        "--disable-pip-version-check",
        "--no-input",
        "--no-cache-dir",
        "--upgrade-strategy",
        "only-if-needed",
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=900,
        )
        detail = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
        if result.returncode != 0:
            return False, detail[-1500:]
        return True, detail[-600:]
    except Exception as e:
        return False, str(e)


def _verify_dependencies():
    """Check required imports in a fresh interpreter and name any missing library."""
    missing = []
    for module, package in _REQUIRED_MODULES.items():
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {module}"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                missing.append(f"{module} ← {package}")
        except Exception as e:
            missing.append(f"{module} ← {package} ({e})")
    if missing:
        return False, ", ".join(missing)
    return True, ""


def _restart():
    os.execv(sys.executable, [sys.executable, "-m", "JoKeRUB"])


@l313l.ar_cmd(
    pattern=r"تحديث(?:\s+(.*))?$",
    command=("تحديث", plugin_category),
    info={
        "header": "فحص تحديثات السورس وتثبيت تحديث كامل من مستودع GitHub.",
        "description": "يعرض الفرق بين النسخة الحالية وأحدث كود على الفرع المحدد. التحديث من الكود وليس من الإصدارات.",
        "options": {
            "تنفيذ/الان": "خاص بالمالك فقط: تنزيل أحدث الملفات وتثبيتها وتحديث المتطلبات ثم إعادة التشغيل."
        },
        "usage": ["{tr}تحديث", "{tr}تحديث الان", "{tr}تحديث تنفيذ"],
    },
)
async def check_updates(event):
    arg = (event.pattern_match.group(1) or "").strip().lower()
    apply = _is_apply_request(arg)
    msg = await edit_or_reply(event, "**جاري فحص التحديثات...**")

    repo = _repo()
    branch = _branch()
    current_version = _current_version()
    local_commit = _local_commit()

    latest = await asyncio.to_thread(_fetch_latest_code, repo, branch)
    if not latest:
        return await edit_delete(msg, "**تعذر فحص التحديثات (لا يوجد رد).**", 20)

    if latest.get("__error__"):
        return await edit_delete(
            msg,
            f"**فشل فحص التحديثات:** `{latest.get('__error__')}`\n"
            f"المستودع: `{repo}` (الفرع `{branch}`)",
            25,
        )

    remote_commit = latest.get("sha") or "غير معروف"
    remote_version = latest.get("remote_version")
    commit_url = latest.get("url") or f"https://github.com/{repo}/commits/{branch}"

    if local_commit != "غير معروف" and remote_commit != "غير معروف":
        if local_commit.lower().startswith(remote_commit.lower()) or remote_commit.lower().startswith(local_commit.lower()):
            status = "السورس محدث"
        else:
            status = "يوجد تحديث جديد"
    elif remote_version and _parse_version_tuple(remote_version) > _parse_version_tuple(current_version):
        status = "يوجد تحديث جديد"
    elif remote_version and _parse_version_tuple(remote_version) == _parse_version_tuple(current_version):
        status = "على الأرجح محدث (النسخة متطابقة)"
    else:
        status = "تم فحص حالة التحديث"

    lines = [
        f"**{getattr(Config, 'T3RMX_DISPLAY_NAME', 'T3rmx UserBot')} - فحص التحديث**",
        "",
        f"• المستودع: `{repo}`",
        f"• الفرع: `{branch}`",
        f"• النسخة الحالية: `{current_version}`",
        f"• الكوميت الحالي: `{local_commit}`",
        f"• أحدث كوميت: `{remote_commit}`",
        f"• تاريخ الكوميت: `{latest.get('date', 'غير معروف')}`",
        f"• الحالة: **{status}**",
        f"• رابط التحديث: {commit_url}",
    ]
    if remote_version:
        lines.append(f"• نسخة السورس: `{remote_version}`")
    if latest.get("message"):
        lines.append(f"• آخر تغيير: `{latest.get('message')}`")
    if latest.get("latest_release_tag"):
        lines.append(
            f"• آخر إصدار (للعلم فقط): `{latest.get('latest_release_tag')}` {latest.get('latest_release_url', '')}".rstrip()
        )

    lines.extend(
        [
            "",
            "_ملاحظة: التحديث يتم من كود المستودع وليس من الإصدارات._",
        ]
    )

    if apply:
        if not authorized_for_update(event.sender_id):
            lines.append("\n**تم رفض طلب التنفيذ:** المالك فقط هو من يستطيع تثبيت التحديثات.")
        else:
            lines.append("\n**تنفيذ التحديث (خاص بالمالك):**")
            tmp_dir = None
            try:
                await msg.edit("**جاري تنزيل أحدث ملفات السورس...**", link_preview=False)
                source_dir, tmp_dir = await asyncio.to_thread(_download_source, repo, branch)

                await msg.edit("**جاري تثبيت جميع المكتبات المطلوبة...**", link_preview=False)
                ok, detail = await asyncio.to_thread(_install_requirements, source_dir)
                if not ok:
                    lines.append(f"• فشل تثبيت المتطلبات، لم يتم تغيير أي ملف ولن يتم إعادة التشغيل:\n```\n{detail[:1200]}\n```")
                    await msg.edit("\n".join(lines), link_preview=False)
                    return

                await msg.edit("**جاري التحقق من جميع المكتبات...**", link_preview=False)
                ok, missing = await asyncio.to_thread(_verify_dependencies)
                if not ok:
                    lines.append(f"• مكتبات مفقودة بعد التثبيت: `{missing}`. لم يتم تغيير أي ملف ولن يتم إعادة التشغيل.")
                    await msg.edit("\n".join(lines), link_preview=False)
                    return

                lines.append(f"• تم تثبيت والتحقق من {len(_REQUIRED_MODULES)} مكتبة مطلوبة بنجاح.")

                await msg.edit("**جاري استبدال ملفات السورس...**", link_preview=False)
                count = await asyncio.to_thread(_copy_tree, source_dir, _repo_root())
                lines.append(f"• تم تحديث `{count}` ملفاً.")

                lines.append("• سيتم إعادة تشغيل البوت لتفعيل التحديث...")
                await msg.edit("\n".join(lines), link_preview=False)
                await asyncio.sleep(2)
                _restart()
                return
            except Exception as e:
                lines.append(f"• فشل التحديث ولم يتم إكماله: `{e}`")
            finally:
                if tmp_dir:
                    shutil.rmtree(tmp_dir, ignore_errors=True)

    await msg.edit("\n".join(lines), link_preview=False)
