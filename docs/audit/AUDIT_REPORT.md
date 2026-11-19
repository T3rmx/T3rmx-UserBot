# T3rmx UserBot — Source Audit Report (Initial)

**Date:** 2026-11-18  
**Workspace:** `/home/riyadh/Projects/T3rmx-UserBot` (single standalone repository, fresh reset, no commits yet)  
**Audited read-only sources:** `/tmp/opencode/t3rmx-audit/{jepthon,lMl10l,nekopack}` (untouched)

## 1. Scope and method
- Inventoried repository structure, runtime/bootstrap/deployment files, dependency manifests, plugins/assistant/helpers/database modules, and feature surfaces.
- Static analysis across active imported tree for: old branding/identity, hardcoded developer IDs, auto-join/forced channel behavior, remote code fetch/exec/update paths, unpinned/VCS dependencies, privileged controls, VC/music integration points, and secrets handling.
- Commands/evidence (representative): `find`, `grep`, `wc -l`, file inspections of core startup/config/session/client, key plugins (`المطور.py`, `تحديث.py`, `تنصيب.py`), deployment manifests, and dependency files.

## 2. Source provenance (baseline)
| Component | Upstream | Branch | Audited HEAD | Notes |
|---|---|---|---|---|
| Application (primary) | https://github.com/jepthoniq/jepthon | master | `becff9b70efa494d06439743d45d2476167e815e` | Imported as functional baseline (features/code). AGPL-3.0 license retained (`LICENSE`). |
| Deployment/bootstrap | https://github.com/jepthoniq/lMl10l | lMl10l | `9498ab580ae1bdb106d463fcd8d37ad28854dfc2` | Template/bootstrap reference; insecure mutable runtime fetch patterns identified and must not be reused. |
| Original lineage | https://github.com/TgCatUB/nekopack | master | `ec24a75d4b24626d013fefbf84e117c8a189a1bf` | Lineage/attribution reference (CatUserBot pack). |

## 3. Baseline inventory (imported)
- **Python files:** ~223 total (`JoKeRUB/plugins`: 104, `JoKeRUB/assistant`: 12, `JoKeRUB/sql_helper`: 36, `JoKeRUB/helpers`: 62, plus core/utils/config/strings/resources and top-level scripts).
- **Major functional areas:** Telethon userbot + assistant bot, large command/plugin surface (admin/moderation, utilities, media/download/convert, spam/automation, customization/vars, fun, music/help text), SQL helpers/persistence, inline/assistant handlers, media helpers (`bin/`, helpers), localization/resources (`ALJoker/strings`, `l313l/razan/resources`).
- **Entry/runtime (legacy):** `python3 -m JoKeRUB` (`JoKeRUB/__main__.py`, `JoKeRUB/utils/startup.py`, `JoKeRUB/core/session.py`, `JoKeRUB/core/client.py`).

## 4. Critical findings

### 4.1 Supply-chain and unsafe runtime behavior (HIGH/CRITICAL)
- **Mutable runtime bootstrap (lMl10l lineage):** `start` resolved/downloaded application zip from previous maintainer repos (base64-obfuscated defaults), performed git fetch/checkout at runtime, and ran requirement-diff pip installs — **not to be used**.
- **Remote code/script execution in build/runtime patterns:** legacy Dockerfiles cloned upstream repos and used `curl -sL https://deb.nodesource.com/setup_16.x | bash -`; updater flows executed `pip install`/`git pull`/force resets in-app.
- **External plugin/VC fetch:** `JoKeRUB/__main__.py` + `utils/startup.py` auto-cloned `https://github.com/jepthoniq/JepVc` (`jepvc`) into `jepthonvc` when `VCMODE` enabled (`install_externalrepo`), enabling mutable third-party code execution at runtime.
- **Runtime dependency mutation:** `install_pip`/module-not-found auto-install behavior and dynamic pip installs in helpers/plugins/core paths; updater plugin performed git/heroku operations and `pip install -r --upgrade --force-reinstall`.
- **Unpinned/VCS dependencies:** `requirements.txt` included unpinned `git+https://github.com/yt-dlp/yt-dlp`; audited upstream manifests included additional unpinned `git+` deps (e.g. img2html, youtube-search-python, cinemagoer, search-engine-parser, Telethon@test, etc.). Risk: supply-chain drift/compromise and non-reproducible builds.
- **Auto-join / forced infrastructure coupling:** startup saved/auto-joined legacy channels (`@jepthon`, `@jepthonsupport`), contacted legacy bot/endpoints, created/logged to hardcoded group identities/media URLs, and used legacy support/update links.

### 4.2 Identity, branding, and hardcoded privilege (HIGH)
- **Old branding footprint:** ~391 matches across ~81 files for `jepthon/jepthoniq/lMl10l/HuRe*` and related identities; ~27 matches across ~16 files for legacy Telegram links (`t.me/jepthon`, `jepthonsupport`, `lMl10l`) in code/plugins/resources/docs/help strings.
- **Hardcoded developer/privileged IDs:** ~73 occurrences across ~18 files (e.g. `705475246, 1374312239, 393120911, 5564802580, 1895219306`) including core (`core/client.py` `DEVJOKR`), many plugins, and remote-control-like handlers (e.g. `المطور.py` “حظر/الغاء الحظر من السورس”, scattered special-case checks). **Must be removed and replaced with centralized authorization (default owner/dev: @vvsks / 6023224495).**
- **Self-update/deploy/install plugins bound to old repos/flows:** `تحديث.py` implemented git pull/reset + pip install + Heroku deploy/restart against legacy upstream; `تنصيب.py` linked to old Heroku/Replit/BotFather/maintainer resources and telegraph media.

### 4.3 VC/Music integration (MEDIUM/HIGH – functional dependency)
- Help/UX strings reference VC/music commands (e.g. enable music mode, join/leave call, play/queue/skip/pause/resume) but implementation was **externally sourced** via runtime clone of `jepthoniq/JepVc` into `jepthonvc` when `VCMODE` (no verified standalone JepVc source in audited copies). In-repo music helpers exist for download/lyrics (`helpers/functions/musictool.py`, plugins like `اغنية.py`) but full call-control backend depends on missing external module set. **Requires independent T3rmx-VC adapter/interface, preserved hooks/config, and clear documentation of functional vs backend-dependent capabilities.**

### 4.4 Configuration, security, and maintainability
- **Config:** legacy defaults/keys and Heroku-oriented vars mixed in; `TG_BOT_USERNAME` handling, timezone/env defaults, and validation inconsistent; `exampleconfig.py` contained sample credentials/values patterns that must be sanitized.
- **Secrets/session safety:** session/token handling present in runtime; risk of leakage via logs/commands/plugins if not controlled; updater/vars plugins historically powerful (Heroku/git). Centralized secure handling and non-logging required.
- **Architecture:** monolithic package name/import coupling (`JoKeRUB`), duplicated/legacy patterns, limited automated tests, and plugin-driven dynamic loading.

## 5. Licensing and attribution constraints
- Preserve AGPL-3.0 `LICENSE` and all legally required upstream copyright/attribution notices (jepthon/lMl10l lineage; CatUserBot/nekopack lineage as applicable in derived content).
- Do not copy/vend unreviewed third-party code/assets; verify license compatibility before vendoring. Do not reuse previous maintainers’ branding/media except where legally required for attribution.
- Owner-provided branding asset: `assets/branding/t3rmx-logo.jpg`.

## 6. Compatibility risks (to manage during implementation)
- **Telegram/MTProto:** Telethon version changes can affect session/auth/API behavior; keep backward-compatible env vars and session handling.
- **Database:** SQLAlchemy usage spans legacy patterns; upgrades must preserve data behavior where possible.
- **Plugins:** broad dynamic plugin surface and Arabic command/help text; rebrand/refactor must avoid breaking command routing, handlers, and assistant callbacks.
- **VC backend absence:** full voice-chat playback/control features cannot be guaranteed without a verified backend; must remain configurable, non-fatal, and documented.

## 7. Required remediation/rebuild actions (summary)
1. Centralize config/logging/permissions/error handling; enforce owner `@vvsks` / `6023224495`; normalize `TG_BOT_USERNAME` (accept with/without `@`, store normalized), defaults `TZ=Asia/Aden`, `ENV=production`; preserve backward-compatible env vars.
2. Remove insecure runtime behaviors (mutable fetch/clone/update, remote script exec, silent installs/auto-joins/legacy endpoints) and replace with safe, explicit, in-repo mechanisms.
3. Complete AR/EN rebrand (code/plugins/help/assistant/resources/deploy/docs/metadata) to T3rmx and repo `https://github.com/T3rmx/T3rmx-UserBot`; remove old media/links/ads/auto-joins not legally required.
4. Implement safe update system via GitHub Releases (check/list current vs latest, show changelog, no auto-install, developer-authorized explicit action only, no arbitrary downloads/exec).
5. Rebuild deployment: Heroku `app.json` + deploy button, Railway `railway.json` + full config, Dockerfile + docker-compose, VPS scripts + systemd, Linux direct execution; all targeting main repo and preserving required env vars.
6. Create independent modular `T3rmx-VC/` with adapter/interface, config flags, preserved hooks, and documentation of dependency on future verified backend.
7. Audit/pin/vendor dependencies with license/maintenance review and documentation; produce reproducible manifests.
8. Add automated tests for critical components and complete documentation/security review before first commit.
