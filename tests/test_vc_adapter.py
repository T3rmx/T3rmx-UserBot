import os
import sys
import unittest
import asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in [str(ROOT), str(ROOT / "T3rmx-UserBot")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Ensure import path works for hyphenated directory name
if "T3rmx_VC" not in sys.modules:
    try:
        import T3rmx_VC  # noqa: F401
    except Exception:
        # fallback: add parent containing symlink/dir
        pass


class TestVCAdapter(unittest.TestCase):
    def setUp(self):
        self._backup = {k: os.environ.get(k) for k in [
            "VCMODE", "T3RMX_VC_ENABLED", "T3RMX_VC_BACKEND", "T3RMX_VC_SESSION", "VC_SESSION"
        ]}

    def tearDown(self):
        for k, v in self._backup.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_unavailable_backend_status(self):
        from T3rmx_VC.t3rmx_vc.adapter import UnavailableVCBackend
        b = UnavailableVCBackend(backend_name="none", enabled=False)
        st = b.status()
        self.assertFalse(st.enabled)
        self.assertFalse(st.available)
        self.assertFalse(st.configured)
        self.assertTrue(st.message)

        b2 = UnavailableVCBackend(backend_name="external", enabled=True)
        st2 = b2.status()
        self.assertTrue(st2.enabled)
        self.assertFalse(st2.available)
        self.assertTrue(st2.configured)
        self.assertIn("no verified", st2.message.lower())

    def test_backend_start_raises_when_unavailable(self):
        from T3rmx_VC.t3rmx_vc.adapter import UnavailableVCBackend
        b = UnavailableVCBackend(backend_name="external", enabled=True)
        with self.assertRaises(RuntimeError):
            asyncio.run(b.start())

    def test_get_vc_backend_and_status_importable(self):
        from T3rmx_VC.t3rmx_vc import get_vc_backend, get_vc_status
        backend = get_vc_backend()
        status = get_vc_status()
        self.assertIsNotNone(backend)
        self.assertIsNotNone(status)
        self.assertFalse(status.available)


if __name__ == "__main__":
    unittest.main()
