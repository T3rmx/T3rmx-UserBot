import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in [str(ROOT), str(ROOT / "T3rmx-UserBot")]:
    if p not in sys.path:
        sys.path.insert(0, p)


class TestStaticAndPluginLoading(unittest.TestCase):
    def test_key_files_compile(self):
        files = [
            ROOT / "sample_config.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/core/auth.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/core/client.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/core/decorators.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/core/session.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/utils/startup.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/plugins/المطور.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/plugins/تحديث.py",
            ROOT / "T3rmx-UserBot/JoKeRUB/plugins/تنصيب.py",
            ROOT / "T3rmx-VC/t3rmx_vc/adapter.py",
        ]
        for f in files:
            self.assertTrue(f.exists(), f"missing {f}")
            src = f.read_text(encoding="utf-8")
            compile(src, str(f), "exec")

    def test_plugin_and_assistant_directories_present(self):
        plugins = ROOT / "T3rmx-UserBot/JoKeRUB/plugins"
        assistant = ROOT / "T3rmx-UserBot/JoKeRUB/assistant"
        self.assertTrue(plugins.is_dir())
        self.assertTrue(assistant.is_dir())
        self.assertGreater(len(list(plugins.glob('*.py'))), 50)
        self.assertGreater(len(list(assistant.glob('*.py'))), 5)

    def test_sample_files_have_no_real_session_tokens(self):
        # basic guard: templates should not contain obvious Telegram bot token format or long session blobs
        for rel in ["sample_config.py", ".env.example", "app.json"]:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("1AAg", text)  # common session prefix heuristic, not perfect
            # bot tokens look like digits:AA...
            import re
            self.assertIsNone(re.search(r"\b\d{8,}:[A-Za-z0-9_-]{30,}\b", text), f"possible token in {rel}")


if __name__ == "__main__":
    unittest.main()
