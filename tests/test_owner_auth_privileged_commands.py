import asyncio
import importlib.machinery
import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "T3rmx-UserBot"
for p in [str(ROOT), str(PKG)]:
    if p not in sys.path:
        sys.path.insert(0, p)


def ensure_pkg(name, path=None):
    m = sys.modules.get(name)
    if m is None:
        m = types.ModuleType(name)
        sys.modules[name] = m
    if path is not None:
        m.__path__ = [str(path)]
        spec = importlib.machinery.ModuleSpec(name, loader=None, is_package=True)
        spec.submodule_search_locations = [str(path)]
        m.__spec__ = spec
    return m


class PM:
    def __init__(self, g):
        self.g = (None,) + tuple(g)

    def group(self, n):
        try:
            return self.g[n]
        except Exception:
            return None


class Event:
    def __init__(self, sender_id, pattern_groups=(), reply=False, text=""):
        self.sender_id = sender_id
        self.pattern_match = PM(pattern_groups)
        self.actions = []
        self.last = None
        self.id = 1
        self.chat_id = 123
        self.client = None
        self.reply_to = types.SimpleNamespace(reply_to_msg_id=1) if reply else None
        self._reply_msg = (
            types.SimpleNamespace(
                id=1,
                message="prev",
                sender_id=6023224495,
                from_id=types.SimpleNamespace(user_id=6023224495),
            )
            if reply
            else None
        )
        self.message = types.SimpleNamespace(message=text)

    async def edit(self, t, *a, **k):
        self.actions.append(("edit", t))
        self.last = t
        return self

    async def reply(self, t, *a, **k):
        self.actions.append(("reply", t))
        self.last = t
        return self

    async def delete(self, *a, **k):
        self.actions.append(("delete", None))

    async def get_reply_message(self):
        return self._reply_msg


class Client:
    uid = 6023224495

    def __init__(self):
        self.ar = []
        self.on_handlers = []
        self.disconnected = False
        self.tgbot = types.SimpleNamespace(on=lambda *a, **k: (lambda f: f))

    def ar_cmd(self, pattern=None, **k):
        def d(f):
            self.ar.append((pattern, f, k))
            return f

        return d

    def on(self, *a, **k):
        def d(f):
            self.on_handlers.append((a, k, f))
            return f

        return d

    async def send_message(self, *a, **k):
        self.sent = ("send_message", a, k)

    async def send_file(self, *a, **k):
        self.sent = ("send_file", a, k)

    async def disconnect(self):
        self.disconnected = True


class TestOwnerPrivilegedCommands(unittest.TestCase):
    def setUp(self):
        self._saved = {k: sys.modules.get(k) for k in list(sys.modules.keys())}
        for k in list(sys.modules.keys()):
            if k == "JoKeRUB" or k.startswith("JoKeRUB."):
                sys.modules.pop(k, None)
        os.environ.setdefault("DB_URI", "sqlite:///:memory:")
        self._build_env()

    def tearDown(self):
        for k in list(sys.modules.keys()):
            if k == "JoKeRUB" or k.startswith("JoKeRUB."):
                sys.modules.pop(k, None)
        sys.modules.update({k: v for k, v in self._saved.items() if v is not None})

    def _build_env(self):
        ensure_pkg("JoKeRUB", PKG / "JoKeRUB")
        ensure_pkg("JoKeRUB.core", PKG / "JoKeRUB/core")
        ensure_pkg("JoKeRUB.plugins", PKG / "JoKeRUB/plugins")
        ensure_pkg("JoKeRUB.helpers", PKG / "JoKeRUB/helpers")
        ensure_pkg("JoKeRUB.helpers.functions", PKG / "JoKeRUB/helpers/functions")
        ensure_pkg("JoKeRUB.helpers.utils", PKG / "JoKeRUB/helpers/utils")
        ensure_pkg("JoKeRUB.sql_helper", PKG / "JoKeRUB/sql_helper")
        ensure_pkg("JoKeRUB.utils", PKG / "JoKeRUB/utils")
        ensure_pkg("JoKeRUB.Config", PKG / "JoKeRUB/Config")

        core_logger = types.ModuleType("JoKeRUB.core.logger")
        class _L:
            def __getattr__(self, n): return lambda *a, **k: None
        core_logger.logging = types.SimpleNamespace(getLogger=lambda *a, **k: _L(), INFO=20, WARNING=30, ERROR=40, DEBUG=10, basicConfig=lambda *a, **k: None)
        sys.modules["JoKeRUB.core.logger"] = core_logger

        cfg_mod = types.ModuleType("JoKeRUB.Config")
        class Config:
            APP_ID = 1; API_HASH = "x"; STRING_SESSION = ""; TG_BOT_TOKEN = ""; TG_BOT_USERNAME = "t3rmx_official_bot"
            TZ = "Asia/Aden"; ENV = "production"; ALIVE_NAME = "T3rmx UserBot"
            COMMAND_HAND_LER = "."; SUDO_COMMAND_HAND_LER = "،"
            T3RMX_OWNER_ID = 6023224495; T3RMX_OWNER_USERNAME = "vvsks"; OWNER_ID = 6023224495
            T3RMX_DISPLAY_NAME = "T3rmx UserBot"; T3RMX_REPOSITORY = "https://github.com/T3rmx/T3rmx-UserBot"
            T3RMX_UPDATES_CHANNEL = ""; T3RMX_SUPPORT_GROUP = ""; T3RMX_SUPPORT_CHANNEL = ""
            T3RMX_LOGO = "assets/branding/t3rmx-logo.jpg"; T3RMX_GITHUB_REPO = "T3rmx/T3rmx-UserBot"; T3RMX_VERSION = "1.0.0"
            BOTLOG = False; BOTLOG_CHATID = None; HEROKU_APP = None; SUDO_USERS = set()
            def __getattr__(self, name): return None
        cfg_mod.Config = Config
        sys.modules["JoKeRUB.Config"] = cfg_mod

        self.store = {}
        sg = types.ModuleType("JoKeRUB.sql_helper.globals")
        sg.addgvar = lambda k, v: self.store.__setitem__(k, str(v))
        sg.delgvar = lambda k: self.store.pop(k, None)
        sg.gvarstatus = lambda k: self.store.get(k)
        sys.modules["JoKeRUB.sql_helper.globals"] = sg
        for name in ["JoKeRUB.sql_helper", "JoKeRUB.sql_helper.global_collection"]:
            sys.modules[name] = types.ModuleType(name)
        sys.modules["JoKeRUB.sql_helper.global_collection"].add_to_collectionlist = lambda *a, **k: None
        sys.modules["JoKeRUB.sql_helper.global_collection"].del_keyword_collectionlist = lambda *a, **k: None
        sys.modules["JoKeRUB.sql_helper.global_collection"].get_collectionlist_items = lambda: []

        cm = types.ModuleType("JoKeRUB.core.managers")
        async def edit_or_reply(e, t=None, *a, **k): e.actions.append(("eor", t)); e.last = t; return e
        async def edit_delete(e, t=None, *a, **k): e.actions.append(("edel", t)); e.last = t; return e
        cm.edit_or_reply = edit_or_reply
        cm.edit_delete = edit_delete
        sys.modules["JoKeRUB.core.managers"] = cm

        hf = types.ModuleType("JoKeRUB.helpers.functions")
        async def ok(*a, **k): return "ok"
        hf.catalive = ok; hf.check_data_base_heal_th = ok; hf.get_readable_time = lambda *a, **k: "0s"
        sys.modules["JoKeRUB.helpers.functions"] = hf
        hu = types.ModuleType("JoKeRUB.helpers.utils")
        async def reply_id(e): return 1
        hu.reply_id = reply_id
        sys.modules["JoKeRUB.helpers.utils"] = hu

        spec = importlib.util.spec_from_file_location("JoKeRUB.core.auth", str(PKG / "JoKeRUB/core/auth.py"))
        m = importlib.util.module_from_spec(spec)
        sys.modules["JoKeRUB.core.auth"] = m
        spec.loader.exec_module(m)

        jp = sys.modules["JoKeRUB"]
        jp.Config = Config; jp.StartTime = 0; jp.mention = "me"; jp.BOTLOG = False; jp.BOTLOG_CHATID = None; jp.HEROKU_APP = None
        pp = sys.modules["JoKeRUB.plugins"]
        pp.mention = "me"; pp.BOTLOG = False; pp.BOTLOG_CHATID = None; pp.HEROKU_APP = None

        self.client = Client()
        jp.l313l = self.client
        self._load("alm", PKG / "JoKeRUB/plugins/المطور.py")
        self._load("ops", PKG / "JoKeRUB/plugins/اوامر التشغيل.py")
        self._load("upd", PKG / "JoKeRUB/plugins/تحديث.py")

    def _load(self, name, path):
        spec = importlib.util.spec_from_file_location(f"JoKeRUB.plugins.{name}", str(path))
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = "JoKeRUB.plugins"
        sys.modules[f"JoKeRUB.plugins.{name}"] = mod
        spec.loader.exec_module(mod)
        return mod

    def _find_ar(self, pattern, module_suffix=None):
        for pat, f, k in self.client.ar:
            if pat == pattern and (module_suffix is None or getattr(f, "__module__", "").endswith(module_suffix)):
                return f
        for pat, f, k in self.client.ar:
            if pat and pattern in pat and (module_suffix is None or getattr(f, "__module__", "").endswith(module_suffix)):
                return f
        raise AssertionError(f"handler not found: {pattern}")

    def _find_on(self, fname):
        for a, k, f in self.client.on_handlers:
            if getattr(f, "__name__", "") == fname:
                return f
        raise AssertionError(f"on handler not found: {fname}")

    def test_sec_owner_only(self):
        f = self._find_ar("sec", "alm")
        orig = asyncio.create_subprocess_shell
        class P:
            returncode = 0
            async def communicate(self): return (b"ok\n", b"")
        async def fake(*a, **k): return P()
        asyncio.create_subprocess_shell = fake
        try:
            e = Event(27356743, (None, "echo hi")); e.client = self.client
            asyncio.run(f(e))
            self.assertTrue(any("restricted" in str(x[1]).lower() or "مالك" in str(x[1]) for x in e.actions))
            e2 = Event(6023224495, (None, "echo hi")); e2.client = self.client
            asyncio.run(f(e2))
            self.assertTrue(any("Command" in str(x[1]) or "Stdout" in str(x[1]) for x in e2.actions))
        finally:
            asyncio.create_subprocess_shell = orig

    def test_restriction_toggle_owner_only(self):
        f = self._find_ar("تقييد", "alm")
        e = Event(27356743, ("on",)); e.client = self.client
        asyncio.run(f(e))
        self.assertTrue(any("restricted" in str(x[1]).lower() or "مالك" in str(x[1]) for x in e.actions))
        e2 = Event(6023224495, ("on",)); e2.client = self.client
        asyncio.run(f(e2))
        self.assertEqual(self.store.get("blockedfrom"), "yes")
        e3 = Event(6023224495, ("off",)); e3.client = self.client
        asyncio.run(f(e3))
        self.assertIsNone(self.store.get("blockedfrom"))

    def test_restart_and_shutdown_ops_owner_only(self):
        restart = self._find_ar("اعادة تشغيل$", "ops")
        shutdown = self._find_ar("اطفاء$", "ops")
        orig_exec = os.execle
        orig_exit = sys.exit
        called = {"exec": False, "exit": False}
        def fake_exec(*a, **k): called["exec"] = True; raise SystemExit("exec")
        def fake_exit(code=0): called["exit"] = True; raise SystemExit(code)
        os.execle = fake_exec
        sys.exit = fake_exit
        try:
            e = Event(27356743, ()); e.client = self.client
            try: asyncio.run(restart(e))
            except SystemExit: pass
            self.assertFalse(called["exec"])
            self.assertTrue(any("مالك" in str(x[1]) for x in e.actions))
            called["exec"] = False
            e2 = Event(6023224495, ()); e2.client = self.client
            try: asyncio.run(restart(e2))
            except SystemExit: pass
            self.assertTrue(any(x[0] == "edit" or x[0] == "eor" for x in e2.actions))

            called["exit"] = False
            e3 = Event(27356743, ()); e3.client = self.client
            try: asyncio.run(shutdown(e3))
            except SystemExit: pass
            self.assertFalse(called["exit"])
            self.assertTrue(any("مالك" in str(x[1]) for x in e3.actions))
            e4 = Event(6023224495, ()); e4.client = self.client
            try: asyncio.run(shutdown(e4))
            except SystemExit: pass
            self.assertTrue(called["exit"])
        finally:
            os.execle = orig_exec
            sys.exit = orig_exit

    def test_remote_reply_handlers_owner_only(self):
        rr = self._find_on("_owner_remote_restart")
        rs = self._find_on("_owner_remote_shutdown")
        orig_exec = os.execle
        orig_exit = sys.exit
        called = {"exec": False, "exit": False}
        def fake_exec(*a, **k): called["exec"] = True; raise SystemExit("exec")
        def fake_exit(code=0): called["exit"] = True; raise SystemExit(code)
        os.execle = fake_exec
        sys.exit = fake_exit
        try:
            e = Event(27356743, (), reply=True, text="اعادة تشغيل"); e.client = self.client
            try: asyncio.run(rr(e))
            except SystemExit: pass
            self.assertFalse(called["exec"])
            called["exec"] = False
            e2 = Event(6023224495, (), reply=True, text="اعادة تشغيل"); e2.client = self.client
            try: asyncio.run(rr(e2))
            except SystemExit: pass
            self.assertTrue(called["exec"] or any("اعادة" in str(x[1]) for x in e2.actions))

            e3 = Event(27356743, (), reply=True, text="اطفاء"); e3.client = self.client
            try: asyncio.run(rs(e3))
            except SystemExit: pass
            self.assertFalse(called["exit"])
            e4 = Event(6023224495, (), reply=True, text="اطفاء"); e4.client = self.client
            try: asyncio.run(rs(e4))
            except SystemExit: pass
            self.assertTrue(called["exit"])
        finally:
            os.execle = orig_exec
            sys.exit = orig_exit

    def test_update_execute_owner_gate(self):
        upd = None
        for pat, f, k in self.client.ar:
            if pat == r"تحديث(?:\s+(.*))?$" and getattr(f, "__module__", "").endswith("upd"):
                upd = f; break
        self.assertIsNotNone(upd)
        import urllib.request
        class R:
            def __enter__(self): return self
            def __exit__(self, *a): pass
            def read(self): return b'{"tag_name":"v9.9.9","name":"v9.9.9","html_url":"https://example/release","body":"x","published_at":"now"}'
        orig = urllib.request.urlopen
        urllib.request.urlopen = lambda *a, **k: R()
        try:
            e = Event(27356743, ("تنفيذ",)); e.client = self.client
            asyncio.run(upd(e))
            self.assertTrue(any("Execution request denied" in str(x[1]) for x in e.actions))
            e2 = Event(6023224495, ("تنفيذ",)); e2.client = self.client
            asyncio.run(upd(e2))
            self.assertTrue(any("Owner action" in str(x[1]) or "manual/safe" in str(x[1]).lower() for x in e2.actions))
        finally:
            urllib.request.urlopen = orig


if __name__ == "__main__":
    unittest.main()
