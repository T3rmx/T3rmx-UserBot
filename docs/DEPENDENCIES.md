# Dependency Audit / Inventory — T3rmx UserBot

**Date:** 2026-11-19  
**Method:** static import scan of repository Python files (excluding caches/venv) + inspection of `requirements.txt`, deployment manifests, Python 3.11 install/test/harness checks, and source inspection of lazy-import/runtime-degradation fixes applied in this workspace.  
**Status:** core runtime baseline identified and pinned in `requirements.txt`; all 104 plugins import/exec in mocked harness (104/104) after safe lazification/fallback/compat fixes, but many optional/legacy/unvetted/external-runtime dependencies remain unresolved for full feature behavior. This is a transparent inventory/evidence update, not a claim of complete resolution.

## Summary
- Third-party/non-stdlib/non-internal import modules detected (prior static inventory baseline): **57**
- Core (pinned in `requirements.txt`): **6 runtime packages (+ python-dotenv/psycopg2-binary as pinned deps in manifest context)**
- Plugins loadable in mocked harness (v4, `.venv311`): **104/104**
- Load blockers unresolved: **0** (at mocked import/exec time)
- Runtime-optional/unvetted/legacy/external-runtime modules requiring attention: **13+** documented in `docs/reports/plugin_dependency_map.json` (plus broader optional inventory below)
- Python 3.11 core dependency install in isolated venv: **successful** (prior in this env state); `uv pip check` previously passed.

## Current harness/dependency evidence (2026-11-19)
- `docs/reports/plugin_harness_results.json` / `plugin_failure_classification.json`: **104 total, 104 exec_ok, 0 failed**, `load_ok` 104.
- `docs/reports/plugin_dependency_map.json`: updated with load-time resolutions/mitigations and runtime-optional degraded modules (see “Resolved/mitigated for load” and “Runtime-optional unresolved”).
- `.venv311` spot-check (import probe, this turn): missing `youtubesearchpython`, `wget`, `urlextract`, `googletrans`, `ShazamAPI`, `ocrspace`, `colour`, `covid`, `gtts`, `selenium`, `ujson`; present `pySmartDL`, `yt_dlp`. Other previously vetted packages may or may not be present in current venv state and are not fully re-audited here.

## Core runtime dependencies (pinned in `requirements.txt`)
| Import | PyPI package | Pinned version | License (common; verify artifacts) | Purpose | Used by (sample) |
|---|---|---:|---|---|---|
| `telethon` | `Telethon` | `1.36.0` | MIT | Core Telegram MTProto client/userbot+assistant | `T3rmx-UserBot/JoKeRUB/core/*`, assistants, plugins |
| `aiohttp` | `aiohttp` | `3.9.5` | Apache-2.0 | HTTP client/server helpers | `core/route.py`, helpers, plugins |
| `requests` | `requests` | `2.32.3` | Apache-2.0 | HTTP requests | helpers/plugins |
| `sqlalchemy` | `SQLAlchemy` | `1.3.24` | MIT | DB ORM/sql helpers | `sql_helper/*` |
| `psycopg2` | `psycopg2-binary` | `2.9.9` | LGPL (with exceptions; verify) | PostgreSQL driver | DB runtime (when configured) |
| `PIL` | `Pillow` | `10.4.0` | HPND/MIT-CMU-like | Image processing | helpers/plugins |
| `yt_dlp` | `yt-dlp` | `2024.08.06` | Unlicense | Media download/extraction (preferred) | `helpers/functions/utube.py`, `plugins/يوتيوب.py` |
| `dotenv` | `python-dotenv` | `1.0.1` | BSD-3-Clause | Env loading support | config/runtime helpers |

## Resolved/mitigated for plugin load (this pass, without unsafe installs)
| Module / area | Status | Affected plugins/paths | Notes |
|---|---|---|---|
| `ujson` | not installed; **lazified with stdlib `json` fallback** | `helpers/functions/utube.py`, `assistant/iytdl.py`, load path for `يوتيوب.py` | Removed mocked-harness load blocker; `ujson` not vetted/installed. |
| `youtubesearchpython` | not installed; **lazified/runtime-degraded** | `helpers/functions/utube.py`, `يوتيوب.py` | Plugin loads; search unavailable without package. |
| `youtube_dl` (legacy) | not installed; **legacy fallback path only** | `plugins/يوتيوب.py` | `yt-dlp` preferred; legacy `youtube_dl` API fallback retained but unavailable without package. Full migration/E2E not verified. |
| `googletrans` | not installed/unvetted; **lazy import/guard** | `helpers/functions/functions.py`, `afk.py`, `الترجمه.py`, `ترجمة صوتية.py` | Translation features degrade at runtime. |
| `ocrspace` | not installed, package/API mapping ambiguous; **lazy/runtime guard** | `plugins/احچي.py` | OCR feature degrades; external API/key likely required. |
| `speech_recognition` / `pydub` | runtime presence not fully verified now; **lazy/runtime guards** | `plugins/احچي.py` | STT degrades without packages/backends/ffmpeg. |
| `ShazamAPI` | not installed/unvetted; **lazy/runtime guard** | `plugins/اغنية.py` | External service dependency. |
| `colour` | not installed/unvetted; **lazy/fallback logic** | `plugins/الوقتي.py` | Color parsing may degrade. |
| `pySmartDL` | installed in `.venv311`; **lazy import** | `plugins/الوقتي.py` | Optional download helper. |
| `covid` | not installed/legacy/unvetted; **lazy/runtime guard** | `plugins/فايروس كورونا.py` | Legacy external API/data risk. |
| `gtts` | not installed/unvetted; **lazy/runtime guard** | `plugins/ترجمة صوتية.py` | TTS degrades without package/service/runtime deps. |
| `selenium` | not installed; **lazy import in helper** | `helpers/google_image_download.py`, `plugins/صور.py` | Requires browser/driver runtime (external). |
| `urlextract` / `wget` | not installed/unvetted; **lazy/runtime guards** (plugin paths) | `plugins/يوتيوب.py` (`wget` also top-level in `assistant/iytdl.py`) | Download/extraction paths may degrade; assistant-side flows outside plugin harness may still require vetting/lazification. |
| Harness stub | `scripts/plugin_harness_v4.py` pool `run_in_thread` compatibility | mocked load for `يوتيوب.py`/utube | Test-harness fix only (not production runtime change). |

## Runtime-optional / unresolved / legacy modules (documented, not blindly installed)
| Import/module | Suggested PyPI package | Status (current) | Python 3.11 / notes | Affected plugins/paths |
|---|---|---|---|---|
| `googletrans` | `googletrans` (ambiguous; 4.0.0rc1/3.1.0a0/forks) | not installed, lazy-runtime-degraded, unvetted | API/fork instability risk | `afk.py`, `الترجمه.py`, `ترجمة صوتية.py`, `helpers/functions/functions.py` |
| `ShazamAPI` | `ShazamAPI` | not installed, lazy-runtime-degraded, unvetted | external service | `اغنية.py` |
| `ocrspace` | verify correct package/API mapping | not installed, lazy-runtime-degraded, ambiguous | external API/key likely required | `احچي.py` |
| `speech_recognition` | `SpeechRecognition` | not confirmed installed now, lazy-runtime-degraded | previously vetted 3.17.0 in earlier pass; runtime/audio backends unverified | `احچي.py` |
| `pydub` | `pydub` | not confirmed installed now, lazy-runtime-degraded | requires ffmpeg for conversion | `احچي.py` |
| `colour` | `colour` | not installed, lazy-runtime-degraded, unvetted | older package | `الوقتي.py` |
| `covid` | `covid` | not installed, lazy-runtime-degraded, legacy/unvetted | likely unmaintained/obsolete API risk | `فايروس كورونا.py` |
| `gtts` | `gTTS` (verify package name) | not installed, lazy-runtime-degraded, unvetted | external service/runtime behavior unverified | `ترجمة صوتية.py` |
| `selenium` | `selenium` | not installed, lazy-runtime-degraded, external runtime | requires browser/driver | `صور.py`, `helpers/google_image_download.py` |
| `urlextract` | `urlextract` | not installed, lazy-runtime-degraded, unvetted | URL extraction helper | `يوتيوب.py` |
| `wget` | `wget` | not installed, lazy-runtime-degraded/unvetted | download helper; top-level in assistant module may still affect assistant flows | `يوتيوب.py`, `assistant/iytdl.py` |
| `ujson` | `ujson` | not installed, fallback to stdlib `json` | can be vetted/installed later if needed | `helpers/functions/utube.py`, `assistant/iytdl.py` |
| `youtubesearchpython` | `youtube-search-python` / `youtubesearchpython` | not installed, lazy-runtime-degraded | search helper | `helpers/functions/utube.py`, `يوتيوب.py` |
| `youtube_dl` | `youtube-dl` (legacy) | not installed, legacy fallback only | obsolete/unmaintained; do not blindly install | `plugins/يوتيوب.py` |

## Previously vetted/installed optional deps (earlier passes; re-verify in current env before relying)
`beautifulsoup4==4.15.0`, `pytz==2026.6`, `validators==0.36.0`, `emoji==2.16.0`, `prettytable==3.19.0`, `pyfiglet==1.0.4`, `webcolors==25.10.0`, `geopy==2.5.0`, `telegraph==2.2.0`, `cryptography==50.0.2`, `html-telegraph-poster==0.5.0` + `lxml-html-clean==0.4.6`, `SpeechRecognition==3.17.0`, `speedtest-cli==2.1.3`, `cloudscraper==1.2.71`, `setuptools==84.2.1`, `pydub==0.25.1`, `pySmartDL==1.3.4` (present now), `search-engine-parser==0.6.8`. Some may be absent in the current `.venv311` state; runtime/feature validation remains incomplete.

## `requirements.txt` (current core manifest)
```text
# T3rmx UserBot - core runtime dependencies (pinned)
# See docs/DEPENDENCIES.md for purpose, licensing notes, and extension guidance.

telethon==1.36.0
aiohttp==3.9.5
requests==2.32.3
SQLAlchemy==1.3.24
psycopg2-binary==2.9.9
Pillow==10.4.0
yt-dlp==2024.08.06
python-dotenv==1.0.1
```

## Validation performed
- **Python 3.11.18 isolated venv (`.venv311`)**: core deps installed from `requirements.txt`; compile checks passed for modified files in this turn; unit tests **31 ran, 31 passed, 0 failed, 0 errors, 0 skipped**.
- **Mocked plugin harness v4:** 104/104 plugins `exec_ok` (import/exec+registration), 0 load failures.
- **No external CVE/license/transitive/SBOM verification performed.**

## Gaps and required follow-up
- Complete per-feature runtime validation for plugins depending on optional/legacy/unvetted deps and external runtimes/services (translation, OCR/STT/TTS, media search/download, image scraping/browser, etc.).
- Vet correct PyPI packages/versions and Python 3.11 compatibility for unresolved modules (especially `googletrans`, `ocrspace`, `gtts`, `ShazamAPI`, `colour`, `covid`, `urlextract`, `wget`, `selenium`, `youtubesearchpython`, `ujson`) and install/test only feasible vetted groups; keep graceful degradation.
- Resolve/replace legacy/ambiguous imports and Py2-era utilities (`HTMLParser`, `urllib2`, `imp`, `pkg_resources`/setuptools API behavior, `config` collisions, `bin/cmrudl.py`, assistant top-level `wget` dependency, legacy `youtube_dl` paths) in compatibility-safe passes where appropriate.
- Complete license verification (including transitive/copyleft obligations) and produce SBOM/CVE/vulnerability review for pinned and transitive dependencies.
- Keep runtime auto-install/external fetch disabled; perform updates only through audited, reproducible changes.
