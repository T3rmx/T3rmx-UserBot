import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in [str(ROOT), str(ROOT / "T3rmx-UserBot")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Ensure import path for T3rmx-VC
try:
    import T3rmx_VC  # noqa
except Exception:
    pass


class TestVCCommands(unittest.TestCase):
    def test_status_message_contains_unavailable_info(self):
        from T3rmx_VC.t3rmx_vc.commands import _status_message
        msg = _status_message()
        self.assertIn("T3rmx-VC", msg)
        self.assertIn("backend", msg.lower())

    def test_register_vc_commands_no_client(self):
        from T3rmx_VC.t3rmx_vc.commands import register_vc_commands
        self.assertEqual(register_vc_commands(None), 0)


if __name__ == "__main__":
    unittest.main()
