
import asyncio
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
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
    "t3rmx_commit_id.txt",
    "t3rmx_commit_id.txt.bak",
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
    # The container uses a top-level JoKeRUB symlink (COPY . /app), so __file__
    #can point through that link. Resolve it first; otherwise updates would be
    #written to the filesystem root while Python keeps importing the old code.
    return os.path.abspath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "..")
    )


def _commit_state_path() -> str:
    return os.path.join(_repo_root(), "t3rmx_commit_id.txt")


def _saved_commit() -> str:
    try:
        with open(_commit_state_path(), "r", encoding="utf-8") as fh:
            value = fh.read().strip()
        if value:
            return value[:12]
    except Exception:
        pass
    return ""


def _save_commit(sha: str) -> None:
    try:
        with open(_commit_state_path(), "w", encoding="utf-8") as fh:
            fh.write(str(sha or "").strip()[:40])
    except Exception:
        pass


def _local_commit(tree=None, remote_sha: str = "") -> str:
    saved = _saved_commit()
    if saved:
        return saved
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
    inferred = _commit_from_tree(tree, remote_sha, _repo_root())
    if inferred:
        return inferred
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


def _fetch_tree(repo: str, sha: str):
    if not sha:
        return [], "لا يوجد كوميت للمقارنة"
    data, err = _github_json(
        f"https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1"
    )
    if isinstance(data, dict) and isinstance(data.get("tree"), list):
        if data.get("truncated"):
            return [], "قائمة الملفات في الكوميت غير كاملة"
        return data["tree"], None
    return [], err or "تعذر جلب قائمة ملفات الكوميت"


def _git_blob_sha(payload: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode("ascii") + b"\x00" + payload
    ).hexdigest()


def _local_blob_hashes(tree, root: str):
    hashes = {}
    for entry in tree or []:
        if not isinstance(entry, dict) or entry.get("type") != "blob":
            continue
        path = str(entry.get("path") or "")
        if not path or _is_protected(path) or path.startswith("docs/reports/"):
            continue
        candidates = [os.path.join(root, *path.split("/"))]
        # Deployed images can be flattened: GitHub keeps files under the
        # T3rmx-UserBot/ prefix while the container imports from its root.
        if path.startswith("T3rmx-UserBot/"):
            candidates.append(os.path.join(root, *path.split("/")[1:]))
        local_path = next((p for p in candidates if os.path.lexists(p)), None)
        if not local_path:
            continue
        git_link = str(entry.get("mode") or "") == "120000"
        local_link = os.path.islink(local_path)
        # Deployment snapshots may dereference or rewrite symlinks. A type
        # mismatch is not a source change, so leave that path out.
        if git_link != local_link:
            continue
        try:
            # Git stores symlinks as the link target bytes, not the target
            # file's contents. Follow that rule so fresh deployments match.
            payload = (
                os.readlink(local_path).encode("utf-8")
                if local_link
                else Path(local_path).read_bytes()
            )
        except Exception:
            continue
        blob_hash = _git_blob_sha(payload)
        if git_link and blob_hash.lower() != str(entry.get("sha") or "").lower():
            continue
        hashes[path] = blob_hash
    return hashes


def _fingerprint_stats(tree, root: str):
    """Return (matched, mismatched, sample paths) for update diagnostics."""
    hashes = _local_blob_hashes(tree, root)
    matched = 0
    mismatched = []
    for entry in tree or []:
        if not isinstance(entry, dict) or entry.get("type") != "blob":
            continue
        path = str(entry.get("path") or "")
        if path not in hashes:
            continue
        if str(entry.get("sha") or "").lower() == hashes[path].lower():
            matched += 1
        else:
            mismatched.append(path)
    return matched, mismatched


def _commit_from_tree(tree, remote_sha: str, root: str) -> str:
    """Infer the deployed commit from byte-for-byte source matches.

    Fresh Railway deployments have no git metadata and no saved commit file.
    Matching local source blobs against the GitHub tree gives a reliable answer
    without trusting any environment variable value.
    """
    if not tree or not remote_sha:
        return ""
    hashes = _local_blob_hashes(tree, root)
    if len(hashes) < 3:
        return ""
    matched = 0
    mismatched = 0
    for entry in tree:
        if not isinstance(entry, dict) or entry.get("type") != "blob":
            continue
        path = str(entry.get("path") or "")
        if path not in hashes:
            continue
        if str(entry.get("sha") or "").lower() == hashes[path].lower():
            matched += 1
        else:
            mismatched += 1
    if mismatched or matched < 3:
        return ""
    return str(remote_sha)[:12]


def _fetch_latest_code(repo: str, branch: str):
    commit, err = _github_json(
        f"https://api.github.com/repos/{repo}/commits/{branch}"
    )
    if commit is None:
        return {"__error__": err or "تعذر جلب آخر تحديث"}

    full_sha = str(commit.get("sha") or "")
    info = {
        "sha": full_sha[:12],
        "full_sha": full_sha,
        "message": ((commit.get("commit") or {}).get("message") or "").split("\n", 1)[0],
        "date": ((commit.get("commit") or {}).get("author") or {}).get("date")
        or ((commit.get("commit") or {}).get("committer") or {}).get("date")
        or "غير معروف",
        "url": commit.get("html_url") or f"https://github.com/{repo}/commits/{branch}",
        "branch": branch,
    }

    tree, _tree_err = _fetch_tree(repo, full_sha)
    if tree:
        info["tree"] = tree

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
        lowered = part.lower()
        if lowered in _PROTECTED_NAMES or lowered.startswith(".git"):
            return True
        # `.env`, `.env.local`, `.env.production` and friends are deployment
        # secrets; Config.py is the live case-sensitive config file.
        if lowered.startswith(".env"):
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
    return _install_requirements_file(requirements)


def _install_requirements_file(requirements: str):
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


def _clean_relative_path(value: str):
    value = str(value or "").strip().strip("`").replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    if not value or value.startswith("/") or "\x00" in value:
        return None
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        return None
    return "/".join(parts)


def _resolve_selective_target(kind: str, value: str, tree):
    """Resolve `.تحديث ملف/بلجن` to exactly one repository blob path."""
    paths = {
        str(entry.get("path") or "")
        for entry in (tree or [])
        if isinstance(entry, dict) and entry.get("type") == "blob"
    }
    value = str(value or "").strip().strip("`")
    candidates = []

    if kind == "بلجن":
        name = value[:-3] if value.lower().endswith(".py") else value
        if not name or not re.fullmatch(r"[\w\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\- ]+", name, re.UNICODE):
            return None, "اسم البلجن غير صالح."
        candidates = [
            f"T3rmx-UserBot/JoKeRUB/plugins/{name}.py",
            f"JoKeRUB/plugins/{name}.py",
        ]
    elif kind == "ملف":
        cleaned = _clean_relative_path(value)
        if not cleaned:
            return None, "المسار غير صالح. استخدم مساراً نسبياً داخل المستودع."
        candidates = [cleaned]
        if cleaned == "requirements.txt":
            candidates.append("T3rmx-UserBot/requirements.txt")
        elif cleaned.startswith("JoKeRUB/"):
            candidates.append("T3rmx-UserBot/" + cleaned)
        elif cleaned.endswith(".py") and "/" not in cleaned:
            candidates.append("T3rmx-UserBot/JoKeRUB/plugins/" + cleaned)
    else:
        return None, "نوع التحديث غير معروف."

    matches = []
    seen = set()
    for candidate in candidates:
        candidate = _clean_relative_path(candidate)
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if candidate in paths:
            matches.append(candidate)
    if not matches:
        return None, f"الملف المطلوب غير موجود في أحدث كوميت: `{value}`"
    if len(matches) > 1:
        return None, "المسار متعدد المعاني، اكتب المسار الكامل من جذر المستودع."
    target = matches[0]
    if _is_protected(target):
        return None, f"الملف `{target}` محمي ولا يمكن تحديثه جزئياً."
    return target, None


def _local_path_for_blob(relative_path: str, root: str):
    root_real = os.path.realpath(root)
    candidate = os.path.realpath(os.path.join(root_real, *relative_path.split("/")))
    if candidate != root_real and not candidate.startswith(root_real + os.sep):
        raise RuntimeError("تم رفض مسار خارج المستودع")
    return candidate


def _fetch_remote_file(repo: str, sha: str, path: str):
    quoted = urllib.parse.quote(path, safe="/")
    url = f"https://raw.githubusercontent.com/{repo}/{sha}/{quoted}"
    req = urllib.request.Request(url, headers={"User-Agent": "T3rmx-UserBot-Updater"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read(), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {getattr(e, 'code', 'خطأ')}"
    except Exception as e:
        return None, str(e)


def _syntax_error(relative_path: str, payload: bytes):
    if not relative_path.lower().endswith(".py"):
        return ""
    try:
        compile(payload.decode("utf-8"), relative_path, "exec")
    except (UnicodeDecodeError, SyntaxError) as e:
        return str(e)
    return ""


def _atomic_write(path: str, payload: bytes) -> None:
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".t3rmx-update-", dir=directory)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def _is_requirements_path(relative_path: str) -> bool:
    return os.path.basename(relative_path).lower() == "requirements.txt"


async def _apply_selective(event, msg, kind: str, value: str, latest: dict, repo: str):
    if not authorized_for_update(event.sender_id):
        return await edit_delete(
            msg, "**تم رفض الطلب:** التحديث الجزئي مخصص لمالك البوت فقط.", 20
        )

    tree = latest.get("tree") or []
    if not tree:
        return await edit_delete(msg, "**تعذر جلب قائمة ملفات الكوميت.**", 20)

    target, error = _resolve_selective_target(kind, value, tree)
    if error:
        return await edit_delete(msg, f"**فشل التحديث الجزئي:** {error}", 25)

    sha = latest.get("full_sha") or latest.get("sha") or ""
    if not sha:
        return await edit_delete(msg, "**تعذر تحديد كوميت المصدر.**", 20)

    await msg.edit(f"**جاري جلب `{target}` من الكوميت `{sha[:12]}`...**", link_preview=False)
    payload, error = await asyncio.to_thread(_fetch_remote_file, repo, sha, target)
    if error:
        return await edit_delete(msg, f"**فشل جلب الملف:** `{error}`", 25)

    syntax_error = _syntax_error(target, payload)
    if syntax_error:
        return await edit_delete(
            msg,
            f"**لم يتم تعديل أي ملف:** الملف الذي وصل به خطأ صياغة:\n`{syntax_error[:500]}`",
            30,
        )

    lines = [
        f"**{getattr(Config, 'T3RMX_DISPLAY_NAME', 'T3rmx UserBot')} - تحديث جزئي**",
        "",
        f"• الملف: `{target}`",
        f"• الكوميت: `{sha[:12]}`",
    ]

    if _is_requirements_path(target):
        await msg.edit("**جاري تثبيت المتطلبات من الملف الجديد...**", link_preview=False)
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(prefix="t3rmx-req-", suffix=".txt")
            with os.fdopen(fd, "wb") as fh:
                fh.write(payload)
            ok, detail = await asyncio.to_thread(_install_requirements_file, tmp_path)
            if not ok:
                lines.append(
                    f"• فشل تثبيت المتطلبات، لم يتم تغيير أي ملف:\n```\n{detail[:1200]}\n```"
                )
                return await msg.edit("\n".join(lines), link_preview=False)
            ok, missing = await asyncio.to_thread(_verify_dependencies)
            if not ok:
                lines.append(
                    f"• مكتبات مفقودة بعد التثبيت: `{missing}`. لم يتم تغيير أي ملف."
                )
                return await msg.edit("\n".join(lines), link_preview=False)
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
        lines.append("• تم تثبيت والتحقق من المتطلبات بنجاح.")

    local_path = _local_path_for_blob(target, _repo_root())
    await asyncio.to_thread(_atomic_write, local_path, payload)
    lines.append("• تم استبدال الملف بنجاح.")
    lines.append("• لم يتم حفظ كوميت عام لأن هذا تحديث جزئي.")
    lines.append("• أعد تشغيل البوت لتفعيل التغيير: `.اعادة تشغيل كاملة`.")
    return await msg.edit("\n".join(lines), link_preview=False)


def _restart():
    os.execv(sys.executable, [sys.executable, "-m", "JoKeRUB"])


@l313l.ar_cmd(
    pattern=r"تحديث(?:\s+(.*))?$",
    command=("تحديث", plugin_category),
    info={
        "header": "فحص تحديثات السورس وتثبيت تحديث كامل من مستودع GitHub.",
        "description": "يقارن الكوميت المحفوظ أو بصمات الملفات المحلية بالكوميت الحالي في المستودع. يدعم التحديث الكامل والتحديث الجزئي لملف أو بلجن واحد.",
        "options": {
            "تنفيذ/الان": "خاص بالمالك فقط: تنزيل أحدث الملفات وتثبيتها وتحديث المتطلبات ثم إعادة التشغيل.",
            "ملف <path>": "خاص بالمالك فقط: تحديث ملف واحد من جذر المستودع.",
            "بلجن <name>": "خاص بالمالك فقط: تحديث ملف بلجن واحد بالاسم.",
        },
        "usage": [
            "{tr}تحديث",
            "{tr}تحديث الان",
            "{tr}تحديث تنفيذ",
            "{tr}تحديث ملف T3rmx-UserBot/JoKeRUB/plugins/السجلات.py",
            "{tr}تحديث بلجن السجلات",
        ],
    },
)
async def check_updates(event):
    arg = (event.pattern_match.group(1) or "").strip()
    parts = arg.split(maxsplit=1)
    selective_kind = parts[0] if parts else ""
    selective_value = parts[1].strip() if len(parts) > 1 else ""
    is_selective = selective_kind in {"ملف", "بلجن"}
    apply = _is_apply_request(arg.lower())

    if is_selective and not selective_value:
        return await edit_delete(
            event,
            "**الاستخدام:** `.تحديث ملف <مسار من جذر المستودع>` أو `.تحديث بلجن <اسم الملف>`.",
            25,
        )
    if arg and not apply and not is_selective:
        return await edit_delete(
            event,
            "**أمر غير صالح.** الاستخدام: `.تحديث` أو `.تحديث تنفيذ` أو `.تحديث ملف <path>` أو `.تحديث بلجن <name>`.",
            25,
        )

    msg = await edit_or_reply(event, "**جاري فحص التحديثات...**")

    repo = _repo()
    branch = _branch()
    current_version = _current_version()

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

    if is_selective:
        return await _apply_selective(
            event, msg, selective_kind, selective_value, latest, repo
        )

    local_commit = _local_commit(latest.get("tree") or [], latest.get("full_sha") or "")
    remote_commit = latest.get("sha") or "غير معروف"
    remote_version = latest.get("remote_version")
    commit_url = latest.get("url") or f"https://github.com/{repo}/commits/{branch}"

    if local_commit != "غير معروف" and remote_commit != "غير معروف":
        if local_commit.lower() == remote_commit.lower():
            status = "السورس محدث (نفس الكوميت)"
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
    if local_commit == "غير معروف":
        source_root = _repo_root()
        matched, mismatched = await asyncio.to_thread(
            _fingerprint_stats, latest.get("tree") or [], source_root
        )
        if mismatched:
            lines.append(
                f"• تشخيص المصدر: `{source_root}`، تطابق {matched}، "
                f"اختلاف {len(mismatched)} (أول ملف: `{mismatched[0]}`)"
            )
        else:
            lines.append(
                f"• تشخيص المصدر: `{source_root}`، تطابق {matched}، لا اختلافات"
            )
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
            if (
                local_commit != "غير معروف"
                and remote_commit != "غير معروف"
                and local_commit.lower() == remote_commit.lower()
            ):
                lines.append(
                    "\n**لا يوجد تحديث جديد:** الكوميت المحفوظ مطابق لكوميت المستودع، "
                    "لم يتم تنزيل أو تغيير أو إعادة تشغيل أي شيء."
                )
                await msg.edit("\n".join(lines), link_preview=False)
                return
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

                _save_commit(remote_commit)
                lines.append(f"• تم حفظ الكوميت المثبّت: `{remote_commit}`")

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
