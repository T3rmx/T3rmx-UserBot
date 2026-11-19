import asyncio
import importlib.machinery
import importlib.util
import os
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_ROOT = ROOT / "T3rmx-UserBot"
for p in [str(ROOT), str(PKG_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)


def _ensure_pkg(name: str, path: Path):
    mod = sys.modules.get(name)
    if mod is None:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
    mod.__path__ = [str(path)]
    spec = importlib.machinery.ModuleSpec(name, loader=None, is_package=True)
    spec.submodule_search_locations = [str(path)]
    mod.__spec__ = spec
    return mod


def _load_package_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = name.rpartition(".")[0]
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestRuntimeSafetyFlags(unittest.TestCase):
    def setUp(self):
        self._backup = {
            k: os.environ.get(k)
            for k in [
                "T3RMX_ALLOW_RUNTIME_PIP_INSTALL",
                "T3RMX_ALLOW_EXTERNAL_REPOS",
            ]
        }

    def tearDown(self):
        for k, v in self._backup.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_extdl_install_pip_blocked_by_default(self):
        os.environ.pop("T3RMX_ALLOW_RUNTIME_PIP_INSTALL", None)

        # Package chain for relative imports in helpers.utils.extdl
        _ensure_pkg("JoKeRUB", PKG_ROOT / "JoKeRUB")
        helpers_pkg = _ensure_pkg("JoKeRUB.helpers", PKG_ROOT / "JoKeRUB" / "helpers")
        _ensure_pkg("JoKeRUB.helpers.utils", PKG_ROOT / "JoKeRUB" / "helpers" / "utils")
        _ensure_pkg("JoKeRUB.core", PKG_ROOT / "JoKeRUB" / "core")
        _ensure_pkg("JoKeRUB.Config", PKG_ROOT / "JoKeRUB" / "Config")

        # extdl imports Config from the core package (.. -> JoKeRUB.helpers is wrong; ... -> JoKeRUB.Config)
        core_cfg_mod = types.ModuleType("JoKeRUB.Config")
        core_cfg_mod.Config = type("Config", (), {"T3RMX_ALLOW_RUNTIME_PIP_INSTALL": False})
        sys.modules["JoKeRUB.Config"] = core_cfg_mod
        # Backward-compat shim for older import paths if present
        helpers_cfg_mod = types.ModuleType("JoKeRUB.helpers.Config")
        helpers_cfg_mod.Config = core_cfg_mod.Config
        sys.modules["JoKeRUB.helpers.Config"] = helpers_cfg_mod
        setattr(helpers_pkg, "Config", helpers_cfg_mod)

        # extdl does: from ...core.logger import logging => JoKeRUB.core.logger
        logger_mod = types.ModuleType("JoKeRUB.core.logger")

        class _L:
            def info(self, *a, **k):
                pass

            def warning(self, *a, **k):
                pass

            def debug(self, *a, **k):
                pass

            def error(self, *a, **k):
                pass

        logger_mod.logging = types.SimpleNamespace(getLogger=lambda *a, **k: _L())
        sys.modules["JoKeRUB.core.logger"] = logger_mod

        mod = _load_package_module(
            "JoKeRUB.helpers.utils.extdl",
            PKG_ROOT / "JoKeRUB" / "helpers" / "utils" / "extdl.py",
        )
        out = mod.install_pip("somefakepackage")
        self.assertEqual(out, b"")

    def test_startup_external_repo_interface_and_guarded_behavior(self):
        os.environ.pop("T3RMX_ALLOW_EXTERNAL_REPOS", None)

        # Package chain and required imports for utils.startup
        joker_pkg = _ensure_pkg("JoKeRUB", PKG_ROOT / "JoKeRUB")
        _ensure_pkg("JoKeRUB.core", PKG_ROOT / "JoKeRUB" / "core")
        _ensure_pkg("JoKeRUB.utils", PKG_ROOT / "JoKeRUB" / "utils")
        _ensure_pkg("JoKeRUB.sql_helper", PKG_ROOT / "JoKeRUB" / "sql_helper")
        _ensure_pkg("JoKeRUB.Config", PKG_ROOT / "JoKeRUB" / "Config")

        joker_pkg.BOTLOG = False
        joker_pkg.BOTLOG_CHATID = None
        joker_pkg.PM_LOGGER_GROUP_ID = None

        cfg_mod = types.ModuleType("JoKeRUB.Config")
        cfg_mod.Config = type(
            "Config",
            (),
            {
                "T3RMX_ALLOW_EXTERNAL_REPOS": False,
                "BOTLOG": False,
                "BOTLOG_CHATID": None,
                "COMMAND_HAND_LER": ".",
                "PORT": None,
            },
        )
        sys.modules["JoKeRUB.Config"] = cfg_mod

        core_logger = types.ModuleType("JoKeRUB.core.logger")

        class _L:
            def info(self, *a, **k):
                pass

            def warning(self, *a, **k):
                pass

            def debug(self, *a, **k):
                pass

            def error(self, *a, **k):
                pass

            def setLevel(self, *a, **k):
                pass

        core_logger.logging = types.SimpleNamespace(
            getLogger=lambda *a, **k: _L(),
            WARNING=30,
            INFO=20,
            ERROR=40,
            DEBUG=10,
        )
        sys.modules["JoKeRUB.core.logger"] = core_logger

        core_session = types.ModuleType("JoKeRUB.core.session")
        core_session.l313l = object()
        sys.modules["JoKeRUB.core.session"] = core_session

        web_server_mod = types.ModuleType("JoKeRUB.core.web_server")

        async def web_server():
            return None

        web_server_mod.web_server = web_server
        sys.modules["JoKeRUB.core.web_server"] = web_server_mod

        for name in [
            "aiohttp",
            "requests",
            "telethon",
            "telethon.tl",
            "telethon.tl.functions",
            "telethon.tl.types",
            "JoKeRUB.sql_helper.global_collection",
            "JoKeRUB.sql_helper.globals",
            "JoKeRUB.utils.pluginmanager",
            "JoKeRUB.utils.tools",
        ]:
            if name not in sys.modules:
                sys.modules[name] = types.ModuleType(name)

        aiohttp_web = types.ModuleType("aiohttp.web")

        class _Runner:
            async def setup(self):
                return None

        aiohttp_web.AppRunner = lambda *a, **k: _Runner()

        class _Site:
            async def start(self):
                return None

        aiohttp_web.TCPSite = lambda *a, **k: _Site()
        sys.modules["aiohttp"].web = aiohttp_web
        sys.modules["aiohttp.web"] = aiohttp_web

        sys.modules["telethon"].Button = object
        sys.modules["telethon"].functions = object
        sys.modules["telethon"].types = types.SimpleNamespace(User=object)
        sys.modules["telethon"].utils = types.SimpleNamespace(get_peer_id=lambda x: 0)

        sys.modules["JoKeRUB.sql_helper.global_collection"].del_keyword_collectionlist = lambda *a, **k: None
        sys.modules["JoKeRUB.sql_helper.global_collection"].get_item_collectionlist = lambda *a, **k: []
        sys.modules["JoKeRUB.sql_helper.globals"].addgvar = lambda *a, **k: None
        sys.modules["JoKeRUB.sql_helper.globals"].delgvar = lambda *a, **k: None
        sys.modules["JoKeRUB.sql_helper.globals"].gvarstatus = lambda *a, **k: None
        sys.modules["JoKeRUB.utils.pluginmanager"].load_module = lambda *a, **k: None
        sys.modules["JoKeRUB.utils.tools"].create_supergroup = lambda *a, **k: (None, None)

        st = _load_package_module(
            "JoKeRUB.utils.startup",
            PKG_ROOT / "JoKeRUB" / "utils" / "startup.py",
        )
        self.assertTrue(hasattr(st, "install_externalrepo"))
        res = asyncio.run(st.install_externalrepo("x", "y", "z"))
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main()
