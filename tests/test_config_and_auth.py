import importlib.util
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in [str(ROOT), str(ROOT / "T3rmx-UserBot")]:
    if p not in sys.path:
        sys.path.insert(0, p)


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestConfigAndAuth(unittest.TestCase):
    def setUp(self):
        self._env_backup = {}
        self._keys = [
            "TZ", "ENV", "APP_ID", "API_HASH", "STRING_SESSION", "TG_BOT_TOKEN",
            "TG_BOT_USERNAME", "ALIVE_NAME", "T3RMX_OWNER_ID", "T3RMX_OWNER_USERNAME",
            "OWNER_ID", "VCMODE", "T3RMX_VC_ENABLED", "SUDO_USERS",
        ]
        for k in self._keys:
            self._env_backup[k] = os.environ.get(k)

    def tearDown(self):
        for k, v in self._env_backup.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_normalize_bot_username(self):
        import importlib
        import sample_config as sc
        importlib.reload(sc)
        self.assertEqual(sc._normalize_bot_username("@t3rmx_official_bot"), "t3rmx_official_bot")
        self.assertEqual(sc._normalize_bot_username("t3rmx_official_bot"), "t3rmx_official_bot")
        self.assertEqual(sc._normalize_bot_username("  @Bot  "), "Bot")
        self.assertIsNone(sc._normalize_bot_username(""))
        self.assertIsNone(sc._normalize_bot_username(None))

    def test_sample_config_core_defaults(self):
        for k in ["TZ", "ENV", "T3RMX_OWNER_ID", "T3RMX_OWNER_USERNAME"]:
            os.environ.pop(k, None)
        import importlib
        import sample_config as sc
        importlib.reload(sc)
        cfg = sc.Config
        self.assertEqual(cfg.TZ, "Asia/Aden")
        self.assertEqual(int(getattr(cfg, "T3RMX_OWNER_ID", 0)), 6023224495)
        self.assertEqual(getattr(cfg, "T3RMX_OWNER_USERNAME", ""), "vvsks")
        self.assertEqual(getattr(cfg, "T3RMX_DISPLAY_NAME", ""), "T3rmx UserBot")
        self.assertTrue(bool(getattr(cfg, "ENV", False)))

    def test_owner_authorization(self):
        # Explicit config to authorized owner should grant privileges.
        os.environ["OWNER_ID"] = "6023224495"
        os.environ["T3RMX_OWNER_ID"] = "6023224495"
        os.environ["SUDO_USERS"] = "111,222"
        auth = _load_module_from_path(
            "t3rmx_test_auth_explicit",
            ROOT / "T3rmx-UserBot" / "JoKeRUB" / "core" / "auth.py",
        )
        self.assertTrue(auth.is_owner(6023224495))
        self.assertTrue(auth.is_owner("6023224495"))
        self.assertFalse(auth.is_owner(123456))
        # Explicit requirement: previous/incorrect owner ID must not be authorized.
        self.assertFalse(auth.is_owner(27356743))
        self.assertFalse(auth.authorized_for_sec(27356743))
        self.assertFalse(auth.is_developer(27356743))
        self.assertTrue(auth.is_developer(6023224495))
        self.assertTrue(auth.authorized_for_sec(6023224495))
        self.assertFalse(auth.authorized_for_sec(1))
        self.assertIn(111, auth.sudo_users())
        self.assertTrue(auth.is_sudo(111))
        self.assertTrue(auth.is_sudo(6023224495))

    def test_owner_defaults_to_repository_default_identity(self):
        # With no owner env overrides, defaults must resolve to repository default owner.
        os.environ.pop("OWNER_ID", None)
        os.environ.pop("T3RMX_OWNER_ID", None)
        auth = _load_module_from_path(
            "t3rmx_test_auth_default",
            ROOT / "T3rmx-UserBot" / "JoKeRUB" / "core" / "auth.py",
        )
        self.assertEqual(auth.owner_id(), 6023224495)
        self.assertTrue(auth.is_owner(6023224495))
        self.assertTrue(auth.is_developer(6023224495))
        self.assertTrue(auth.authorized_for_sec(6023224495))
        self.assertFalse(auth.is_owner(27356743))
        self.assertFalse(auth.authorized_for_sec(27356743))
        self.assertFalse(auth.is_developer(27356743))

    def test_configured_owner_env_is_respected_for_deployments(self):
        # Public/template deployments must be able to configure their own owner ID.
        for key in ("OWNER_ID", "T3RMX_OWNER_ID"):
            os.environ[key] = "27356743"
        auth = _load_module_from_path(
            "t3rmx_test_auth_configured_owner",
            ROOT / "T3rmx-UserBot" / "JoKeRUB" / "core" / "auth.py",
        )
        self.assertEqual(auth.owner_id(), 27356743)
        self.assertTrue(auth.is_owner(27356743))
        self.assertTrue(auth.is_developer(27356743))
        self.assertTrue(auth.authorized_for_sec(27356743))
        self.assertFalse(auth.is_owner(6023224495))

    def test_t3rmx_config_helpers(self):
        tc = _load_module_from_path(
            "t3rmx_test_t3rmx_config",
            ROOT / "T3rmx-UserBot" / "JoKeRUB" / "t3rmx_config.py",
        )
        self.assertEqual(tc.normalize_bot_username("@TestBot"), "TestBot")
        self.assertEqual(tc.normalize_bot_username("TestBot"), "TestBot")
        self.assertIsNone(tc.normalize_bot_username(""))


if __name__ == "__main__":
    unittest.main()
    unittest.main()
