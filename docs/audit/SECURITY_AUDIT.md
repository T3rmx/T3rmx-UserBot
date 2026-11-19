# Full Plugin Security Audit (static) — T3rmx UserBot

**Date:** 2026-11-19  
**Scope:** all `T3rmx-UserBot/JoKeRUB/plugins/*.py` (104 files) plus relevant core/runtime controls.  
**Method:** static pattern scan (post-remediation snapshot `/tmp/opencode/t3rmx_security_scan_after.json`), targeted manual review of critical/high-control paths, compile/import checks, and automated unit tests.  
**Severity scale:** Critical / High / Medium / Low (impact x likelihood, considering preserved userbot functionality and current gating).  
**Limitations:** static analysis only (no runtime Telegram execution with real credentials/sessions), regex-based detection has false positives/negatives, many legacy plugins are intentionally powerful (moderation/media/network automation), and not every finding was individually exploited/validated. Dependency CVEs and live infrastructure hardening are out of scope.

## Executive summary
- Repository-wide scan (all Python files, excluding caches/venv): **1639 findings** across **169 files** — Critical 0, High 37, Medium 589, Low 1013.
- Plugin-only scan: **556 findings** across **70 plugin files** — Critical 0, High 4, Medium 335, Low 217.
- **Critical code-execution findings remediated:** removed unsafe `eval(...)` in `plugins/الحاسبة.py` (restricted AST arithmetic evaluator) and in `helpers/functions/functions.py` (`eval` -> `ast.literal_eval` and safe offset handling). Post-remediation Critical count: **0**.
- **High-risk controls (preserved/mitigated):** owner-only `.sec` shell command and restart/restriction controls (`plugins/المطور.py`, `plugins/اوامر التشغيل.py`) restricted to authorized owner `6023224495`; ffmpeg/subprocess use in media plugins (feature-required, no `shell=True` where reviewed); dynamic plugin loading limited to trusted in-repo modules; runtime pip/install and external fetch interfaces disabled/guarded by default. Some static `runtime_pip_install` hits are text/config/guard references (false positives).
- **Medium findings (expected for preserved features):** bulk Telegram moderation/member operations, external network/API requests, and temp/media file writes/deletes. Blanket removal would break functionality; usage requires proper permissions and trusted deployment context.

## Authorization and safety controls (verified)
- Centralized owner/developer identity: `@vvsks` / `6023224495` (`T3rmx-UserBot/JoKeRUB/core/auth.py`); unauthorized configured IDs are ignored.
- Developer controls: `plugins/المطور.py` — `.sec` gated by `authorized_for_sec`, `.تقييد` and `.اعادة تشغيل` gated by `is_owner`.
- Restart/shutdown: `plugins/اوامر التشغيل.py` restricted to `is_owner` (hardcoded legacy dev IDs removed).
- Updates: `plugins/تحديث.py` read-only GitHub Releases check; manual guidance owner-gated; no auto git/pip/heroku mutation or arbitrary execution.
- VC: no unverified backend bundled/fetched; unavailable/unconfigured status and graceful command handling.
- Runtime safety defaults: `T3RMX_ALLOW_RUNTIME_PIP_INSTALL` off by default; external repo fetch/install interfaces guarded/disabled (`helpers/utils/extdl.py`, `utils/startup.py`, `core/pluginManager.py`) with tests.

## Per-plugin audit summary (all 104 plugins)
| Plugin | Max severity | Critical | High | Medium | Low | Key categories / notes | Safe gating / status |
|---|---:|---:|---:|---:|---:|---|---|
| `الصلاحيات.py` | MEDIUM | 0 | 0 | 60 | 5 | Bulk/member moderation operations. [bulk_telegram_ops(60), broad_exception(5)] | Preserve; requires chat permissions/operator intent |
| `اوامر الكروب.py` | MEDIUM | 0 | 0 | 45 | 12 | Bulk/member moderation operations.; External network/API requests. [bulk_telegram_ops(43), broad_exception(10), logging_print(2), network_request(2)] | Preserve; requires chat permissions/operator intent |
| `بنك.py` | MEDIUM | 0 | 0 | 30 | 0 | Bulk/member moderation operations. [bulk_telegram_ops(30)] | Preserve; requires chat permissions/operator intent |
| `اوامر الادمن الوقتية.py` | MEDIUM | 0 | 0 | 17 | 3 | Bulk/member moderation operations. [bulk_telegram_ops(17), broad_exception(3)] | Preserve; requires chat permissions/operator intent |
| `الادمن.py` | MEDIUM | 0 | 0 | 15 | 5 | Bulk/member moderation operations. [bulk_telegram_ops(15), broad_exception(5)] | Preserve; requires chat permissions/operator intent |
| `كشف.py` | MEDIUM | 0 | 0 | 12 | 6 | Bulk/member moderation operations.; File writes/deletes (temp/media/state). [bulk_telegram_ops(11), broad_exception(6), destructive_fs(1)] | Preserve; requires chat permissions/operator intent |
| `التخصيص.py` | MEDIUM | 0 | 0 | 12 | 4 | External network/API requests.; File writes/deletes (temp/media/state). [destructive_fs(8), network_request(4), broad_exception(4)] | Preserve with existing checks; review before privileged use |
| `معلومات الكروب.py` | MEDIUM | 0 | 0 | 7 | 10 | Bulk/member moderation operations. [broad_exception(10), bulk_telegram_ops(7)] | Preserve; requires chat permissions/operator intent |
| `تسلية7.py` | MEDIUM | 0 | 0 | 12 | 0 | File writes/deletes (temp/media/state). [destructive_fs(12)] | Preserve with existing checks; review before privileged use |
| `الصيغ.py` | HIGH | 0 | 1 | 7 | 7 | ffmpeg/asyncio subprocess for media conversion (feature-required).; External network/API requests.; File writes/deletes (temp/media/state). [broad_exception(6), destructive_fs(6), logging_print(1), asyncio_subprocess_exec(1), network_request(1)] | Preserve; feature-required subprocess, no shell=True |
| `التجميع.py` | MEDIUM | 0 | 0 | 1 | 20 | External network/API requests. [broad_exception(19), network_request(1), hardcoded_sensitive_lookup(1)] | Preserve with existing checks; review before privileged use |
| `__init__.py` | MEDIUM | 0 | 0 | 3 | 13 | External network/API requests.; File writes/deletes (temp/media/state). [broad_exception(9), hardcoded_sensitive_lookup(4), file_write_ops(2), network_request(1)] | Preserve with existing checks; review before privileged use |
| `الكتم.py` | MEDIUM | 0 | 0 | 6 | 5 | Bulk/member moderation operations. [bulk_telegram_ops(6), broad_exception(5)] | Preserve; requires chat permissions/operator intent |
| `الملصقات.py` | MEDIUM | 0 | 0 | 7 | 1 | External network/API requests.; File writes/deletes (temp/media/state). [destructive_fs(4), network_request(3), broad_exception(1)] | Preserve with existing checks; review before privileged use |
| `اشراف عام.py` | MEDIUM | 0 | 0 | 4 | 7 | Bulk/member moderation operations. [broad_exception(7), bulk_telegram_ops(4)] | Preserve; requires chat permissions/operator intent |
| `ضع تكرار.py` | MEDIUM | 0 | 0 | 6 | 2 | Bulk/member moderation operations. [bulk_telegram_ops(6), broad_exception(2)] | Preserve; requires chat permissions/operator intent |
| `التثبيت.py` | MEDIUM | 0 | 0 | 6 | 2 | Bulk/member moderation operations. [bulk_telegram_ops(6), broad_exception(2)] | Preserve; requires chat permissions/operator intent |
| `كوكل.py` | MEDIUM | 0 | 0 | 5 | 2 | External network/API requests.; File writes/deletes (temp/media/state). [network_request(4), broad_exception(2), destructive_fs(1)] | Preserve with existing checks; review before privileged use |
| `فلم.py` | MEDIUM | 0 | 0 | 6 | 0 | External network/API requests. [network_request(6)] | Preserve with existing checks; review before privileged use |
| `تيكتوك.py` | MEDIUM | 0 | 0 | 5 | 2 | External network/API requests.; File writes/deletes (temp/media/state). [network_request(3), logging_print(1), file_write_ops(1), broad_exception(1), destructive_fs(1)] | Preserve with existing checks; review before privileged use |
| `تسلية6.py` | MEDIUM | 0 | 0 | 6 | 0 | Bulk/member moderation operations.; File writes/deletes (temp/media/state). [destructive_fs(5), bulk_telegram_ops(1)] | Preserve; requires chat permissions/operator intent |
| `الوهمي.py` | MEDIUM | 0 | 0 | 6 | 0 | Bulk/member moderation operations. [bulk_telegram_ops(6)] | Preserve; requires chat permissions/operator intent |
| `الحماية.py` | LOW | 0 | 0 | 0 | 12 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(12)] | No additional gating required from static scan |
| `ياعلي.py` | MEDIUM | 0 | 0 | 5 | 1 | Bulk/member moderation operations.; External network/API requests. [bulk_telegram_ops(4), hardcoded_sensitive_lookup(1), network_request(1)] | Preserve; requires chat permissions/operator intent |
| `تحديث.py` | HIGH | 0 | 1 | 3 | 2 | Read-only release check/manual guidance (static `runtime_pip_install` mention is non-executing).; External network/API requests. [network_request(3), broad_exception(2), runtime_pip_install(1)] | Read-only + owner-gated guidance |
| `يوتيوب.py` | MEDIUM | 0 | 0 | 4 | 2 | File writes/deletes (temp/media/state). [destructive_fs(4), broad_exception(2)] | Preserve with existing checks; review before privileged use |
| `الفارات.py` | MEDIUM | 0 | 0 | 3 | 4 | External network/API requests.; File writes/deletes (temp/media/state). [broad_exception(4), network_request(1), file_write_ops(1), destructive_fs(1)] | Preserve with existing checks; review before privileged use |
| `البروفايل.py` | MEDIUM | 0 | 0 | 2 | 6 | File writes/deletes (temp/media/state). [broad_exception(6), destructive_fs(2)] | Preserve with existing checks; review before privileged use |
| `اوامر التشغيل.py` | LOW | 0 | 0 | 0 | 10 | Restart/shutdown controls, owner-only. [broad_exception(10)] | Owner-only enforced |
| `التكرار.py` | LOW | 0 | 0 | 0 | 10 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(8), logging_print(2)] | No additional gating required from static scan |
| `تحذير.py` | MEDIUM | 0 | 0 | 4 | 1 | Bulk/member moderation operations. [bulk_telegram_ops(4), broad_exception(1)] | Preserve; requires chat permissions/operator intent |
| `اضافة.py` | MEDIUM | 0 | 0 | 3 | 3 | Bulk/member moderation operations. [bulk_telegram_ops(3), broad_exception(3)] | Preserve; requires chat permissions/operator intent |
| `ترجمة صوتية.py` | HIGH | 0 | 1 | 2 | 2 | ffmpeg/asyncio subprocess for media conversion (feature-required).; File writes/deletes (temp/media/state). [broad_exception(2), destructive_fs(2), subprocess_exec(1)] | Preserve; feature-required subprocess, no shell=True |
| `سي ام دي.py` | MEDIUM | 0 | 0 | 3 | 2 | File writes/deletes (temp/media/state). [destructive_fs(3), broad_exception(2)] | Preserve with existing checks; review before privileged use |
| `المطور.py` | HIGH | 0 | 1 | 0 | 5 | Owner-only shell/restart/restriction controls (intentional high-privilege). [broad_exception(5), asyncio_subprocess_shell(1)] | Owner-only enforced; residual host risk documented |
| `تلكراف.py` | MEDIUM | 0 | 0 | 3 | 1 | File writes/deletes (temp/media/state). [destructive_fs(3), broad_exception(1)] | Preserve with existing checks; review before privileged use |
| `اغنية.py` | MEDIUM | 0 | 0 | 2 | 3 | File writes/deletes (temp/media/state). [broad_exception(3), destructive_fs(2)] | Preserve with existing checks; review before privileged use |
| `احچي.py` | MEDIUM | 0 | 0 | 3 | 1 | File writes/deletes (temp/media/state). [destructive_fs(3), broad_exception(1)] | Preserve with existing checks; review before privileged use |
| `ميمز.py` | MEDIUM | 0 | 0 | 3 | 0 | File writes/deletes (temp/media/state). [file_write_ops(3)] | Preserve with existing checks; review before privileged use |
| `ملفات السورس.py` | MEDIUM | 0 | 0 | 2 | 1 | External network/API requests.; File writes/deletes (temp/media/state). [broad_exception(1), network_request(1), destructive_fs(1)] | Preserve with existing checks; review before privileged use |
| `الوقتي.py` | MEDIUM | 0 | 0 | 2 | 1 | File writes/deletes (temp/media/state). [destructive_fs(2), broad_exception(1)] | Preserve with existing checks; review before privileged use |
| `ملكية.py` | LOW | 0 | 0 | 0 | 5 | No Critical/High/Medium static hits (Low-only/none). [hardcoded_sensitive_lookup(4), broad_exception(1)] | No additional gating required from static scan |
| `طقس.py` | MEDIUM | 0 | 0 | 1 | 2 | External network/API requests. [hardcoded_sensitive_lookup(2), network_request(1)] | Preserve with existing checks; review before privileged use |
| `تشكيل.py` | MEDIUM | 0 | 0 | 2 | 0 | Bulk/member moderation operations. [bulk_telegram_ops(2)] | Preserve; requires chat permissions/operator intent |
| `ادوات_الروابط.py` | MEDIUM | 0 | 0 | 2 | 0 | External network/API requests. [network_request(2)] | Preserve with existing checks; review before privileged use |
| `منشن.py` | LOW | 0 | 0 | 0 | 4 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(3), logging_print(1)] | No additional gating required from static scan |
| `التقليد.py` | LOW | 0 | 0 | 0 | 4 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(4)] | No additional gating required from static scan |
| `صور.py` | MEDIUM | 0 | 0 | 1 | 1 | File writes/deletes (temp/media/state). [broad_exception(1), destructive_fs(1)] | Preserve with existing checks; review before privileged use |
| `تطبيق.py` | MEDIUM | 0 | 0 | 1 | 1 | External network/API requests. [network_request(1), broad_exception(1)] | Preserve with existing checks; review before privileged use |
| `ملخص معلومات.py` | LOW | 0 | 0 | 0 | 3 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(3)] | No additional gating required from static scan |
| `معلومات الحساب.py` | LOW | 0 | 0 | 0 | 3 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(3)] | No additional gating required from static scan |
| `تنصيب.py` | LOW | 0 | 0 | 0 | 3 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(2), hardcoded_sensitive_lookup(1)] | No additional gating required from static scan |
| `الترجمه.py` | LOW | 0 | 0 | 0 | 3 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(2), logging_print(1)] | No additional gating required from static scan |
| `التخزين.py` | LOW | 0 | 0 | 0 | 3 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(2), logging_print(1)] | No additional gating required from static scan |
| `نشر تلقائي.py` | MEDIUM | 0 | 0 | 1 | 0 | Bulk/member moderation operations. [bulk_telegram_ops(1)] | Preserve; requires chat permissions/operator intent |
| `فحص.py` | MEDIUM | 0 | 0 | 1 | 0 | File writes/deletes (temp/media/state). [file_write_ops(1)] | Preserve with existing checks; review before privileged use |
| `تسلية8.py` | MEDIUM | 0 | 0 | 1 | 0 | File writes/deletes (temp/media/state). [destructive_fs(1)] | Preserve with existing checks; review before privileged use |
| `تسلية1.py` | MEDIUM | 0 | 0 | 1 | 0 | Bulk/member moderation operations. [bulk_telegram_ops(1)] | Preserve; requires chat permissions/operator intent |
| `الوقت.py` | MEDIUM | 0 | 0 | 1 | 0 | File writes/deletes (temp/media/state). [destructive_fs(1)] | Preserve with existing checks; review before privileged use |
| `الصلاة.py` | MEDIUM | 0 | 0 | 1 | 0 | External network/API requests. [network_request(1)] | Preserve with existing checks; review before privileged use |
| `منوع.py` | LOW | 0 | 0 | 0 | 2 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(2)] | No additional gating required from static scan |
| `afk.py` | LOW | 0 | 0 | 0 | 2 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(2)] | No additional gating required from static scan |
| `نوم.py` | LOW | 0 | 0 | 0 | 1 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(1)] | No additional gating required from static scan |
| `ملفات خارجيه.py` | LOW | 0 | 0 | 0 | 1 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(1)] | No additional gating required from static scan |
| `سرعة النت.py` | LOW | 0 | 0 | 0 | 1 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(1)] | No additional gating required from static scan |
| `تهكير.py` | LOW | 0 | 0 | 0 | 1 | No Critical/High/Medium static hits (Low-only/none). [hardcoded_sensitive_lookup(1)] | No additional gating required from static scan |
| `اوامر المنع.py` | LOW | 0 | 0 | 0 | 1 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(1)] | No additional gating required from static scan |
| `الصورة.py` | LOW | 0 | 0 | 0 | 1 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(1)] | No additional gating required from static scan |
| `الاوامر.py` | LOW | 0 | 0 | 0 | 1 | No Critical/High/Medium static hits (Low-only/none). [hardcoded_sensitive_lookup(1)] | No additional gating required from static scan |
| `الانتحال.py` | LOW | 0 | 0 | 0 | 1 | No Critical/High/Medium static hits (Low-only/none). [broad_exception(1)] | No additional gating required from static scan |

**Plugins with no static findings (34):** `الاذاعه.py`, `الاذكار.py`, `التحكم.py`, `الترحيب.py`, `الترحيب2.py`, `التمبلر.py`, `التنظيف.py`, `الثكيل.py`, `الحاسبة.py`, `الخطوط.py`, `الردود.py`, `الموقع.py`, `امونغ اس.py`, `اوامري.py`, `تاريخ اسماء.py`, `تحشيش .py`, `تحشيش.py`, `تسلية2.py`, `تسلية3.py`, `تسلية4.py`, `تسلية5.py`, `تفرعات الاوامر.py`, `ذاتية.py`, `رسالة موقوته.py`, `رسالة.py`, `زغرفة.py`, `فايروس كورونا.py`, `لستة.py`, `متحركات ساد.py`, `متحركات كيوت.py`, `ميم.py`, `نص.py`, `همسه.py`, `ييبنك.py`

## Detailed High-severity findings (repo-wide, static)
### asyncio_subprocess_exec (3)
- `T3rmx-UserBot/JoKeRUB/core/pluginManager.py:28` — cmd = await asyncio.create_subprocess_exec(
- `T3rmx-UserBot/JoKeRUB/plugins/الصيغ.py:324` — process = await asyncio.create_subprocess_exec(
- `T3rmx-UserBot/JoKeRUB/helpers/utils/utils.py:13` — process = await asyncio.create_subprocess_exec(

### asyncio_subprocess_shell (1)
- `T3rmx-UserBot/JoKeRUB/plugins/المطور.py:108` — proc = await asyncio.create_subprocess_shell(

### dynamic_import (10)
- `tests/test_config_and_auth.py:14` — spec = importlib.util.spec_from_file_location(name, str(path))
- `tests/test_config_and_auth.py:18` — spec.loader.exec_module(mod)
- `tests/test_runtime_safety_flags.py:30` — spec = importlib.util.spec_from_file_location(name, str(path))
- `tests/test_runtime_safety_flags.py:35` — spec.loader.exec_module(mod)
- `tests/test_plugin_loading_safety.py:9` — spec = importlib.util.spec_from_file_location(path.stem + "_testmod", str(path))
- `T3rmx-UserBot/JoKeRUB/core/auth.py:39` — mod = __import__(mod_name, fromlist=[attr])
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:26` — spec = importlib.util.spec_from_file_location(name, path)
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:28` — spec.loader.exec_module(mod)
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:38` — spec = importlib.util.spec_from_file_location(name, path)
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:63` — spec.loader.exec_module(mod)

### external_download_exec (2)
- `tests/test_deployment_config.py:50` — self.assertNotIn("git clone https://github.com/", s.lower())
- `tests/test_deployment_config.py:59` — self.assertNotIn("curl | sh", s.lower())

### runtime_pip_install (20)
- `sample_config.py:111` — T3RMX_ALLOW_RUNTIME_PIP_INSTALL = _get_bool("T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False)
- `tests/test_runtime_safety_flags.py:44` — "T3RMX_ALLOW_RUNTIME_PIP_INSTALL",
- `tests/test_runtime_safety_flags.py:57` — os.environ.pop("T3RMX_ALLOW_RUNTIME_PIP_INSTALL", None)
- `tests/test_runtime_safety_flags.py:68` — helpers_cfg_mod.Config = type("Config", (), {"T3RMX_ALLOW_RUNTIME_PIP_INSTALL": False})
- `tests/test_runtime_safety_flags.py:95` — out = mod.install_pip("somefakepackage")
- `T3rmx-UserBot/JoKeRUB/core/pluginManager.py:23` — if not getattr(Config, "T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False):
- `T3rmx-UserBot/JoKeRUB/core/pluginManager.py:24` — LOGS.warning("Blocked runtime pip package installation request (disabled by default).")
- `T3rmx-UserBot/JoKeRUB/core/pluginManager.py:37` — LOGS.error(f"Runtime pip install failed: {e}")
- `T3rmx-UserBot/JoKeRUB/helpers/__init__.py:7` — # should not trigger runtime pip installs.
- `T3rmx-UserBot/JoKeRUB/plugins/تحديث.py:139` — "No git pull, pip install, or arbitrary code execution is performed by this command._"
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:56` — mod.install_pip = install_pip
- `T3rmx-UserBot/JoKeRUB/utils/startup.py:228` — if getattr(Config, "T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False):
- `T3rmx-UserBot/JoKeRUB/utils/startup.py:231` — install_pip(e.name)
- `T3rmx-UserBot/JoKeRUB/utils/startup.py:352` — # Even when enabled, require explicit branch and avoid auto pip installs by default.
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:7` — def install_pip(pipfile):
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:8` — """Runtime pip install is disabled by default for security/reproducibility.
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:11` — Enable only explicitly via T3RMX_ALLOW_RUNTIME_PIP_INSTALL.
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:13` — if not getattr(Config, "T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False):
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:15` — f"Blocked runtime pip install request for '{pipfile}'. "
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:27` — LOGS.error(f"Runtime pip install failed for {pipfile}: {e}")

### subprocess_exec (1)
- `T3rmx-UserBot/JoKeRUB/plugins/ترجمة صوتية.py:89` — t_response = subprocess.check_output(

## Detailed High-severity findings (repo-wide, static)
### asyncio_subprocess_exec (3)
- `T3rmx-UserBot/JoKeRUB/core/pluginManager.py:28` — `cmd = await asyncio.create_subprocess_exec(`
- `T3rmx-UserBot/JoKeRUB/plugins/الصيغ.py:324` — `process = await asyncio.create_subprocess_exec(`
- `T3rmx-UserBot/JoKeRUB/helpers/utils/utils.py:13` — `process = await asyncio.create_subprocess_exec(`

### asyncio_subprocess_shell (1)
- `T3rmx-UserBot/JoKeRUB/plugins/المطور.py:108` — `proc = await asyncio.create_subprocess_shell(`

### dynamic_import (10)
- `tests/test_config_and_auth.py:14` — `spec = importlib.util.spec_from_file_location(name, str(path))`
- `tests/test_config_and_auth.py:18` — `spec.loader.exec_module(mod)`
- `tests/test_runtime_safety_flags.py:30` — `spec = importlib.util.spec_from_file_location(name, str(path))`
- `tests/test_runtime_safety_flags.py:35` — `spec.loader.exec_module(mod)`
- `tests/test_plugin_loading_safety.py:9` — `spec = importlib.util.spec_from_file_location(path.stem + "_testmod", str(path))`
- `T3rmx-UserBot/JoKeRUB/core/auth.py:39` — `mod = __import__(mod_name, fromlist=[attr])`
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:26` — `spec = importlib.util.spec_from_file_location(name, path)`
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:28` — `spec.loader.exec_module(mod)`
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:38` — `spec = importlib.util.spec_from_file_location(name, path)`
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:63` — `spec.loader.exec_module(mod)`

### external_download_exec (2)
- `tests/test_deployment_config.py:50` — `self.assertNotIn("git clone https://github.com/", s.lower())`
- `tests/test_deployment_config.py:59` — `self.assertNotIn("curl | sh", s.lower())`

### runtime_pip_install (20)
- `sample_config.py:111` — `T3RMX_ALLOW_RUNTIME_PIP_INSTALL = _get_bool("T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False)`
- `tests/test_runtime_safety_flags.py:44` — `"T3RMX_ALLOW_RUNTIME_PIP_INSTALL",`
- `tests/test_runtime_safety_flags.py:57` — `os.environ.pop("T3RMX_ALLOW_RUNTIME_PIP_INSTALL", None)`
- `tests/test_runtime_safety_flags.py:68` — `helpers_cfg_mod.Config = type("Config", (), {"T3RMX_ALLOW_RUNTIME_PIP_INSTALL": False})`
- `tests/test_runtime_safety_flags.py:95` — `out = mod.install_pip("somefakepackage")`
- `T3rmx-UserBot/JoKeRUB/core/pluginManager.py:23` — `if not getattr(Config, "T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False):`
- `T3rmx-UserBot/JoKeRUB/core/pluginManager.py:24` — `LOGS.warning("Blocked runtime pip package installation request (disabled by default).")`
- `T3rmx-UserBot/JoKeRUB/core/pluginManager.py:37` — `LOGS.error(f"Runtime pip install failed: {e}")`
- `T3rmx-UserBot/JoKeRUB/helpers/__init__.py:7` — `# should not trigger runtime pip installs.`
- `T3rmx-UserBot/JoKeRUB/plugins/تحديث.py:139` — `"No git pull, pip install, or arbitrary code execution is performed by this command._"`
- `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:56` — `mod.install_pip = install_pip`
- `T3rmx-UserBot/JoKeRUB/utils/startup.py:228` — `if getattr(Config, "T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False):`
- `T3rmx-UserBot/JoKeRUB/utils/startup.py:231` — `install_pip(e.name)`
- `T3rmx-UserBot/JoKeRUB/utils/startup.py:352` — `# Even when enabled, require explicit branch and avoid auto pip installs by default.`
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:7` — `def install_pip(pipfile):`
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:8` — `"""Runtime pip install is disabled by default for security/reproducibility.`
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:11` — `Enable only explicitly via T3RMX_ALLOW_RUNTIME_PIP_INSTALL.`
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:13` — `if not getattr(Config, "T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False):`
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:15` — `f"Blocked runtime pip install request for '{pipfile}'. "`
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py:27` — `LOGS.error(f"Runtime pip install failed for {pipfile}: {e}")`

### subprocess_exec (1)
- `T3rmx-UserBot/JoKeRUB/plugins/ترجمة صوتية.py:89` — `t_response = subprocess.check_output(`

## Individual High-severity finding review (post-remediation)

| Category | Finding(s) | Exploitability / code path | Attacker privileges | Status | Residual risk / justification |
|---|---|---|---|---|---|
| `asyncio_subprocess_shell` | `T3rmx-UserBot/JoKeRUB/plugins/المطور.py:108` (`.sec` handler executes shell command) | High impact if invoked: arbitrary host command execution in bot process context. | **Owner-only** (`authorized_for_sec` / configured owner `6023224495`); unauthorized users denied. | Mitigated by strict auth gating; **not removed** (preserved owner/developer mechanism). | Accepted residual risk for owner-compromised account/session or host compromise; keep least-privilege deployment and session security. |
| `asyncio_subprocess_exec` | `T3rmx-UserBot/JoKeRUB/plugins/الصيغ.py:324` (ffmpeg media conversion), `T3rmx-UserBot/JoKeRUB/helpers/utils/utils.py:13` (`runcmd`), `T3rmx-UserBot/JoKeRUB/core/pluginManager.py:28` (pip install helper) | Subprocess execution with argument arrays (`exec`, no `shell=True` in reviewed paths). `runcmd` splits command string; callers must be trusted/internal. `pluginManager` pip install is feature-helper but runtime install is blocked by default in guards. | Depends on caller: media commands by users with access to bot features; internal utility usage; pip install path guarded by config/disabled defaults. | Preserved feature-required behavior; no `shell=True` introduced; runtime auto-install guarded/blocked by default. | Residual risk from untrusted media/tool inputs or misuse of internal `runcmd` callers; monitor and constrain inputs where feasible. |
| `subprocess_exec` | `T3rmx-UserBot/JoKeRUB/plugins/ترجمة صوتية.py:89` (ffmpeg/tts pipeline) | Local ffmpeg/subprocess invocation for audio conversion; argument list, no shell. | User-triggered feature in permitted contexts. | Preserved feature-required behavior. | Residual risk limited to local tool/input handling; ensure ffmpeg/deps are trusted and patched in deployment. |
| `dynamic_import` | `tests/*` spec loading (5 hits), `T3rmx-UserBot/JoKeRUB/core/auth.py:39`, `T3rmx-UserBot/JoKeRUB/utils/pluginmanager.py:26,28,38,63` | Dynamic module loading/exec for tests and plugin/auth resolution. Plugin manager loads modules from in-repo plugin paths; not shown to fetch arbitrary remote code at runtime. | Test/runtime internal paths; plugin loading affects bot runtime features. | Preserved architecture; external repo/runtime fetch mechanisms separately guarded/disabled by default. | Accepted residual risk if untrusted code is placed into plugin paths or repository is compromised; rely on trusted codebase and file permissions. |
| `runtime_pip_install` | 20 hits across config, tests, core/plugin manager, startup helpers, update-plugin text | Most hits are config flags, guard checks, warnings, blocked helper implementations, tests asserting blocking, or user-facing/read-only text stating no pip install is performed. No unconditional runtime auto-install path identified as enabled by default. | N/A when blocked; would require explicit opt-in/config changes if supported in specific paths. | Mitigated/false-positive-dominant in static terms; default behavior remains **blocked/disabled**. | Residual risk only if operator explicitly enables unsafe flags in future/unreviewed paths; keep defaults off and manifests pinned. |
| `external_download_exec` | `tests/test_deployment_config.py:50,59` | Test assertions checking absence of unsafe patterns (`git clone https://github.com/`, `curl | sh`). | Test-only. | Not a vulnerability; static scanner false positive. | No runtime residual risk from these lines. |

**Review outcome:** all 37 High findings were reviewed by category/file-path context. No additional code fixes were applied in this pass beyond previously remediated Critical `eval` issues because remaining actionable runtime High items are either **owner-gated intentional controls**, **feature-required subprocess/dynamic-loading behavior without shell injection in reviewed paths**, or **guard/test/text false positives**. Further reduction requires feature redesign/removal or stronger sandboxing (out of scope without breaking preserved behavior).

## Residual risk assessment
- **No unresolved Critical findings** in post-remediation static scan.
- **High findings** remain documented and risk-accepted/mitigated as above (not silently exposed). Static audit does not prove runtime safety, dependency-CVE safety, or safe operation under malicious inputs, compromised Telegram sessions, or untrusted deployments.

## Addendum — 2026-11-19 (post-audit hardening & mocked/harness evidence)

**Scope of addendum:** code hardening, mocked runtime verification, automated tests, and harness artifacts produced after the static scan documented above. This is **not** a new repo-wide static scan and does not change the reported post-remediation scan totals (Critical 0, High 37, Medium 589, Low 1013 repo-wide) unless separately rescanned.

### Additional hardening applied (owner-gating / correctness, behavior-preserving intent)
- `T3rmx-UserBot/JoKeRUB/plugins/اوامر التشغيل.py`: `التحديثات (تشغيل|ايقاف)` handler now enforces `is_owner` (previously missing explicit owner check in handler body); missing `edit_delete` import fixed.
- `T3rmx-UserBot/JoKeRUB/plugins/سي ام دي.py`: external plugin install (`تنصيب`) and uninstall (`الغاء التنصيب`) handlers now enforce `is_owner` and include safer downloaded-file cleanup on failure (reduces risk from untrusted users triggering file write/load/remove operations in bot plugin directory).
- `T3rmx-UserBot/JoKeRUB/plugins/ملفات السورس.py`: `فاراتي` (environment variable dump to saved messages) now enforces `is_owner` (reduces sensitive-information exposure risk).
- `T3rmx-UserBot/JoKeRUB/helpers/utils/extdl.py`: corrected Config import (`from ..Config` -> `from ...Config`) with `tests/test_runtime_safety_flags.py` updated to match guarded runtime-install interface expectations.

### Mocked runtime owner-auth verification (harnessed handler execution)
- Artifact: `docs/reports/owner_auth_runtime_verification.json` (all checked keys `ok: true`).
- **Verified (mocked/stubbed execution paths, not full Telethon event pipeline/E2E):** `.sec` (`plugins/المطور.py`), developer restriction toggle `تقييد` (`plugins/المطور.py`), restart (`plugins/المطور.py`), restart (`plugins/اوامر التشغيل.py`), shutdown/stop (`plugins/اوامر التشغيل.py`), remote reply restart/shutdown handlers (`plugins/اوامر التشغيل.py`), `تحديث تنفيذ` owner gate (`plugins/تحديث.py`), and auth helpers. Unauthorized identity `27356743` denied; authorized owner `6023224495` allowed in applicable cases.
- **Code-reviewed/static, not fully DB-backed Telethon E2E simulated:** `blockedfrom` core guard behavior in `T3rmx-UserBot/JoKeRUB/core/client.py` and `T3rmx-UserBot/JoKeRUB/core/events.py` (`docs/reports/owner_auth_runtime_verification.json` key `blockedfrom_core_guard_review`).

### Automated test evidence (Python 3.11.18, `.venv311`)
- Command: `.venv311/bin/python -m unittest discover -s tests -p 'test_*.py'`
- Result: **31 tests run, 30 passed, 0 failed, 0 errors, 1 skipped** (~18.4s). DB/session-limited warnings expected.
- Additions/updates: `tests/test_owner_auth_privileged_commands.py` (mocked privileged handler execution), `tests/test_sql_helper_db.py` (missing `DB_URI` import safety and bad-connection handling passed; isolated SQLite init/CRUD/rollback/close skipped due SQLAlchemy 1.3/Config binding behavior in that harness with separate passing evidence in `docs/reports/db_harness_results.json`), `tests/test_runtime_safety_flags.py` updated for `extdl` Config import fix.

### Plugin load/registration harness (mocked, all 104 plugins)
- Artifact: `docs/reports/plugin_harness_results.json` (harness v3, import/exec with stubs; no real Telegram/DB/network/production data).
- Summary: **104 total, exec_ok 41, failed 63, with_ar_cmd 36, with_bot_cmd 0, with_on 15**. Classifications: `load_ok` 41, `load_error` 37, `missing_optional_dependency` 26.
- External missing modules observed (26 instances / 19 distinct): `html_telegraph_poster` (4), `bs4` (3), `pytz` (2), `telegraph` (2), `ShazamAPI`, `cloudscraper`, `covid`, `cryptography`, `emoji`, `geopy`, `gtts`, `pkg_resources`, `prettytable`, `pyfiglet`, `selenium`, `speech_recognition`, `speedtest`, `validators`, `webcolors` (1 each). `load_error` cases require per-plugin triage (harness/compatibility export/stub gaps vs real defects); no silent skips.

### Isolated DB harness
- Artifact: `docs/reports/db_harness_results.json`.
- Results: `sql_helper_missing_db_uri_import` ok (safe/controlled), `sql_helper_sqlite_crud` ok (init/CRUD/rollback/close checks), `sql_helper_connection_failure` ok (`OperationalError`), `postgres_infra_available` false (`psql` unavailable). No production data used.

### Residual gaps (security/runtime)
- No new static scan executed for this addendum; additional hardening should be reflected in any future scan.
- Mocked owner-auth verification covers sampled privileged handlers/paths only; **not all privileged commands** and **not full real Telethon pipeline/E2E**. DB-backed `blockedfrom` and broader core guard enforcement remain unproven at runtime E2E.
- Many plugins/features depend on optional/legacy modules not installed in core `.venv311`; missing-dependency and harness-stub failures limit confidence in full runtime plugin behavior and error handling.
- Deployment/runtime security remains dependent on trusted operators, secure credential/session handling, least-privilege host/container config, and vetted dependency installation (no external CVE/license/transitive/SBOM verification in this environment). No production deployment success is claimed.
