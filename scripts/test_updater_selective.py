"""Deterministic checks for the owner-only selective updater.

Run with: python3 scripts/test_updater_selective.py
No network, credentials, or running Telegram client is needed.
"""

import asyncio
import hashlib
import importlib.util
import os
import sys
import tempfile
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATER = ROOT / "T3rmx-UserBot" / "JoKeRUB" / "plugins" / "تحديث.py"


def install_stubs():
    client = types.SimpleNamespace(
        ar_cmd=lambda *a, **k: (lambda func: func),
    )
    config = types.SimpleNamespace(T3RMX_DISPLAY_NAME="T3rmx UserBot")

    for name, package in (
        ("JoKeRUB", True),
        ("JoKeRUB.plugins", True),
        ("JoKeRUB.core", True),
        ("JoKeRUB.Config", True),
    ):
        module = types.ModuleType(name)
        if package:
            module.__path__ = []
        sys.modules[name] = module

    auth = types.ModuleType("JoKeRUB.core.auth")
    auth.authorized_for_update = lambda uid: uid == 6023224495
    sys.modules["JoKeRUB.core.auth"] = auth

    async def edit_none(*a, **k):
        return None

    managers = types.ModuleType("JoKeRUB.core.managers")
    managers.edit_delete = edit_none
    managers.edit_or_reply = edit_none
    sys.modules["JoKeRUB.core.managers"] = managers

    sys.modules["JoKeRUB"].l313l = client
    sys.modules["JoKeRUB"].Config = config
    sys.modules["JoKeRUB.Config"].Config = config
    sys.modules["JoKeRUB.plugins"].l313l = client
    sys.modules["JoKeRUB.core"].auth = auth
    sys.modules["JoKeRUB.core"].managers = managers


def load_updater():
    install_stubs()
    spec = importlib.util.spec_from_file_location(
        "JoKeRUB.plugins._updater_selective_test", str(UPDATER)
    )
    module = importlib.util.module_from_spec(spec)
    module.__package__ = "JoKeRUB.plugins"
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check(condition, message):
    if not condition:
        raise AssertionError(message)


class DummyMessage:
    def __init__(self):
        self.edits = []

    async def edit(self, text, *a, **k):
        self.edits.append(str(text))
        return self


class DummyEvent:
    def __init__(self, sender_id=6023224495):
        self.sender_id = sender_id


def make_tree():
    return [
        {
            "type": "blob",
            "path": "T3rmx-UserBot/JoKeRUB/plugins/السجلات.py",
            "sha": "a" * 40,
        },
        {
            "type": "blob",
            "path": "T3rmx-UserBot/JoKeRUB/Config.py",
            "sha": "b" * 40,
        },
        {"type": "blob", "path": "requirements.txt", "sha": "c" * 40},
    ]


async def exercise_apply(module, kind, value, payload=b"print('ok')\n"):
    writes = []
    calls = {"requirements": 0, "verify": 0, "saved": 0}

    module._fetch_remote_file = lambda repo, sha, path: (payload, None)
    module._atomic_write = lambda path, data: writes.append((path, data))
    module._repo_root = lambda: str(ROOT)
    module._install_requirements_file = lambda path: (
        calls.__setitem__("requirements", calls["requirements"] + 1),
        (True, ""),
    )[1]
    module._verify_dependencies = lambda: (
        calls.__setitem__("verify", calls["verify"] + 1),
        (True, ""),
    )[1]
    module._save_commit = lambda sha: calls.__setitem__(
        "saved", calls["saved"] + 1
    )

    msg = DummyMessage()
    await module._apply_selective(
        DummyEvent(), msg, kind, value,
        {"full_sha": "f" * 40, "sha": "f" * 12, "tree": make_tree()},
        "T3rmx/T3rmx-UserBot",
    )
    return writes, calls, msg


def main():
    module = load_updater()

    payload = b"hello"
    expected = hashlib.sha1(b"blob 5\x00" + payload).hexdigest()
    check(
        module._git_blob_sha(payload) == expected,
        "git blob SHA calculation is wrong",
    )

    tree = make_tree()
    target, error = module._resolve_selective_target(
        "بلجن", "السجلات", tree
    )
    check(error is None, f"plugin resolution failed: {error}")
    check(
        target == "T3rmx-UserBot/JoKeRUB/plugins/السجلات.py",
        f"unexpected plugin target: {target}",
    )

    target, error = module._resolve_selective_target(
        "ملف", "JoKeRUB/plugins/السجلات.py", tree
    )
    check(error is None and target.endswith("السجلات.py"), "path alias failed")

    target, error = module._resolve_selective_target(
        "ملف", "requirements.txt", tree
    )
    check(error is None and target == "requirements.txt", "requirements resolution failed")

    for bad in ("../../etc/passwd", "/etc/passwd", "a/../b.py"):
        _, error = module._resolve_selective_target("ملف", bad, tree)
        check(error, f"unsafe path was accepted: {bad}")

    _, error = module._resolve_selective_target(
        "ملف", "T3rmx-UserBot/JoKeRUB/Config.py", tree
    )
    check(error, "protected Config.py was accepted")

    check(
        module._syntax_error("x.py", b"def broken(:\n") != "",
        "syntax check did not reject broken Python",
    )
    check(
        module._syntax_error("x.py", b"def ok():\n    pass\n") == "",
        "syntax check rejected valid Python",
    )

    original_hashes = module._local_blob_hashes
    module._local_blob_hashes = lambda tree_arg, root: {
        "a.py": "h1",
        "b.py": "h2",
        "c.py": "h3",
    }
    clean_tree = [
        {"type": "blob", "path": "a.py", "sha": "h1"},
        {"type": "blob", "path": "b.py", "sha": "h2"},
        {"type": "blob", "path": "c.py", "sha": "h3"},
    ]
    check(
        module._commit_from_tree(clean_tree, "abcdef123456", "/tmp") == "abcdef123456",
        "commit fingerprint did not infer a clean match",
    )
    clean_tree[1]["sha"] = "different"
    check(
        module._commit_from_tree(clean_tree, "abcdef123456", "/tmp") == "",
        "commit fingerprint accepted a mismatched source tree",
    )
    module._local_blob_hashes = original_hashes

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "x.py")
        module._atomic_write(path, b"ok\n")
        check(Path(path).read_bytes() == b"ok\n", "atomic write failed")

    writes, calls, msg = asyncio.run(
        exercise_apply(module, "بلجن", "السجلات")
    )
    check(len(writes) == 1, "plugin update did not write exactly one file")
    check(
        calls["requirements"] == 0 and calls["verify"] == 0,
        "plugin update touched requirements unnecessarily",
    )
    check(calls["saved"] == 0, "partial update saved a global commit")
    check(any("تحديث جزئي" in line for line in msg.edits), "missing Arabic status message")

    writes, calls, _ = asyncio.run(
        exercise_apply(module, "ملف", "requirements.txt")
    )
    check(len(writes) == 1, "requirements update did not write exactly one file")
    check(
        calls["requirements"] == 1 and calls["verify"] == 1,
        "requirements update skipped strict dependency handling",
    )
    check(calls["saved"] == 0, "requirements update saved a global commit")

    print("selective updater checks: OK")


if __name__ == "__main__":
    main()
