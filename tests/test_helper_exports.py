import ast
import importlib
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


def _read(path):
    return Path(path).read_text(encoding="utf-8")


class TestHelperExports(unittest.TestCase):
    def test_progress_exports_exist(self):
        # source-level contract
        src = _read(PKG_ROOT / "JoKeRUB/helpers/progress.py")
        for name in ("readable_time", "time_formatter", "humanbytes"):
            self.assertRegex(src, rf"def\s+{name}\b", name)

    def test_tools_exports_exist(self):
        src = _read(PKG_ROOT / "JoKeRUB/helpers/tools.py")
        for name in ("media_type", "meme_type", "fileinfo", "post_to_telegraph"):
            self.assertIn(name, src)

    def test_utils_events_exports_exist(self):
        src = _read(PKG_ROOT / "JoKeRUB/helpers/utils/events.py")
        self.assertRegex(src, r"def\s+reply_id\b")
        self.assertRegex(src, r"def\s+get_user_from_event\b")

    def test_functions_exports_exist(self):
        utube = _read(PKG_ROOT / "JoKeRUB/helpers/functions/utube.py")
        nekos = _read(PKG_ROOT / "JoKeRUB/helpers/functions/nekos.py")
        for name in ("name_dl", "song_dl", "video_dl", "thumb_dl", "yt_search"):
            self.assertIn(name, utube)
        self.assertRegex(nekos, r"def\s+changemymind\b")

    def test_helpers_init_has_compat_exports(self):
        src = _read(PKG_ROOT / "JoKeRUB/helpers/__init__.py")
        for token in ("media_type", "readable_time", "get_readable_time", "time_formatter", "reply_id", "thumb_from_audio"):
            self.assertIn(token, src)

    def test_assistant_botcontrols_importable_syntax_and_handlers(self):
        src = _read(PKG_ROOT / "JoKeRUB/assistant/botcontrols.py")
        ast.parse(src)
        # basic handler/command markers
        self.assertIn("bot_broadcast", src)
        self.assertIn("ban_botpms", src)
        self.assertIn("ban_antiflood", src)
        self.assertIn("@l313l.bot_cmd", src)
        self.assertIn("اذاعة", src)

    def test_runtime_imports_where_safe(self):
        # direct module imports that should not require Telegram session/network.
        # Some modules import JoKeRUB package paths that trigger lightweight init in this codebase;
        # stub session client to avoid hard dependency on valid credentials during import-time checks.
        try:
            import JoKeRUB.core.session as sess
            sess.l313l = types.SimpleNamespace(version=None, tgbot=types.SimpleNamespace(version=None))
        except Exception:
            pass

        mod = importlib.import_module("JoKeRUB.helpers.progress")
        self.assertTrue(callable(mod.readable_time))
        self.assertTrue(callable(mod.time_formatter))
        self.assertEqual(mod.readable_time(0), "00:00:00")

        mod_tools = importlib.import_module("JoKeRUB.helpers.tools")
        self.assertTrue(callable(mod_tools.media_type))

        mod_events = importlib.import_module("JoKeRUB.helpers.utils.events")
        self.assertTrue(callable(mod_events.reply_id))

        mod_utube = importlib.import_module("JoKeRUB.helpers.functions.utube")
        self.assertTrue(hasattr(mod_utube, "name_dl"))

        mod_nekos = importlib.import_module("JoKeRUB.helpers.functions.nekos")
        self.assertTrue(callable(getattr(mod_nekos, "changemymind")))


if __name__ == "__main__":
    unittest.main()
