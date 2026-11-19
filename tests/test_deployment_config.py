import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestDeploymentConfig(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "README.md",
            "LICENSE",
            "BRANDING.md",
            "sample_config.py",
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
            "Procfile",
            "app.json",
            "railway.json",
            "T3rmx-Deploy/vps/install.sh",
            "T3rmx-Deploy/vps/t3rmx-userbot.service",
            "docs/audit/SECURITY_AUDIT.md",
            "docs/DEPENDENCIES.md",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).exists(), f"missing {rel}")

    def test_app_json_core_envs(self):
        data = json.loads((ROOT / "app.json").read_text(encoding="utf-8"))
        env = data.get("env", {})
        for key in ["APP_ID", "API_HASH", "STRING_SESSION", "TG_BOT_TOKEN", "TG_BOT_USERNAME", "ALIVE_NAME", "TZ", "ENV"]:
            self.assertIn(key, env, f"missing env var {key} in app.json")
        self.assertEqual(env.get("TZ", {}).get("value"), "Asia/Aden")

    def test_railway_json_valid(self):
        data = json.loads((ROOT / "railway.json").read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)
        text = json.dumps(data).lower()
        self.assertTrue("dockerfile" in text or "docker" in text)

    def test_procfile_entrypoint(self):
        s = (ROOT / "Procfile").read_text(encoding="utf-8")
        self.assertIn("python3 -m JoKeRUB", s)

    def test_dockerfile_entrypoint_and_no_remote_clone(self):
        s = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("CMD", s)
        self.assertIn("JoKeRUB", s)
        self.assertNotIn("git clone https://github.com/", s.lower())

    def test_vps_systemd_service(self):
        s = (ROOT / "T3rmx-Deploy/vps/t3rmx-userbot.service").read_text(encoding="utf-8")
        self.assertIn("ExecStart=", s)
        self.assertIn("JoKeRUB", s)

    def test_install_script_basic_safety(self):
        s = (ROOT / "T3rmx-Deploy/vps/install.sh").read_text(encoding="utf-8")
        self.assertNotIn("curl | sh", s.lower())
        self.assertIn("python", s.lower())


if __name__ == "__main__":
    unittest.main()
