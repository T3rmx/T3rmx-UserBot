# T3rmx UserBot — Feature Map & Migration Mapping

This document maps legacy feature areas (audited T3rmx/JoKeRUB baseline) to the T3rmx structure and records disposition: **Preserve**, **Preserve+Refactor**, **Isolate/Guard**, or **Replace mechanism (keep feature intent)**.

## 1. Logical module mapping (target, single repo)

| Target logical module | Purpose | Legacy/source mapping | Disposition |
|---|---|---|---|
| `T3rmx-UserBot/` | Application runtime, core, handlers, assistant, DB/helpers, utilities, config | `JoKeRUB/`, `ALJoker/`, `l313l/`, `bin/`, `stringsetup.py`, `sample_config.py`, core support files | **Preserve+Refactor** (compatibility-first reorg) |
| `T3rmx-Plugins/` | Plugin collection and plugin-system organization | `JoKeRUB/plugins/*`, assistant plugin integration points | **Preserve** (all existing plugins retained; rebranded/secured) |
| `T3rmx-VC/` | Voice chat/music backend abstraction and integration layer | `VCMODE`/external `JepVc` hooks, startup external-repo install path, music/VC help & related helpers | **Preserve+Isolate/Guard** (independent adapter; backend TBD) |
| `T3rmx-Deploy/` | Deployment templates, scripts, and platform configs | legacy `Dockerfile`, `Procfile`, lMl10l/nekopack deploy concepts | **Replace mechanism** (safe, in-repo, reproducible) |
| `docs/`, `config/`, `assets/`, `vendor/`, `tests/` | Documentation, examples, branding, vendored deps, tests | scattered/legacy or new | **New/Refactor** |

## 2. Core/runtime features

| Area | Key files (legacy) | Feature intent | T3rmx mapping | Notes |
|---|---|---|---|---|
| Entrypoint & lifecycle | `JoKeRUB/__main__.py`, `core/session.py`, `core/client.py`, `utils/startup.py`, `core/logger.py` | Start user+assistant clients, load plugins/assistant, logging, web/health bind, shutdown/restart hooks | `T3rmx-UserBot/JoKeRUB/*` | Remove legacy auto-joins, external VC clone, unsafe restart/update coupling; keep startup/shutdown behavior safe and configurable |
| Configuration | `Config/roza_config.py`, `sample_config.py`, `exampleconfig.py` | Env/config loading, defaults, feature flags | Centralized config module + compatibility exports | Preserve legacy env vars; normalize `TG_BOT_USERNAME`; defaults `TZ=Asia/Aden`, `ENV=production` |
| Authorization & control | `core/client.py` (DEVJOKR/blocked checks), `core/decorators.py`, sudo/admin checks, plugin-level ID gates | Owner/sudo/admin command access, privileged actions | Centralized `security/permissions` (or equivalent) used by core/plugins | Default owner/dev `@vvsks` / `6023224495`; remove old hardcoded IDs; keep sec/control features scoped to authorized owner |
| Plugin system | `utils/pluginmanager.py`, `core/pluginManager.py`, dynamic loader | Load/unload plugins, assistant modules, external plugin paths | Preserved loader with safe behavior | Disable silent runtime pip installs/unsafe external fetch by default; keep feature loading |
| Assistant/bot UI | `assistant/*.py`, inline handlers | Inline/help/callbacks, bot-side interactions | Preserved and rebranded | Ensure owner checks and text/assets updated |
| Persistence/DB | `sql_helper/*`, helpers | Settings/state for AFK, filters, PM permit, notes, vars, etc. | Preserved | Compatibility-first; audit for safety and reliability |
| Utilities/media/scripts | `helpers/*`, `bin/*`, media tools | Download/convert/processing utilities | Preserved with dependency audit | Pin/vend deps; remove unsafe network/script patterns where not required |

## 3. Plugin/feature groups (preserve all)

| Group | Examples (non-exhaustive) | T3rmx handling |
|---|---|---|
| Admin/moderation | admin/kick/ban/mute/pin/warn, group tools | Preserve; rebrand text; ensure permission checks and safety |
| Protection/PM controls | PM permit, anti-spam/guards | Preserve; configurable defaults, owner control |
| Customization/vars/profile | alive/name/bio/pic/time/vars plugins | Preserve; adapt to centralized config and safe storage |
| Assistant/help/menus | help lists, command menus, inline buttons | Preserve; full AR/EN T3rmx rebrand |
| Media/download/tools | YouTube/song/download/convert/telegraph/ocr/etc. | Preserve; pin/vet deps (yt-dlp, ffmpeg, etc.) |
| Fun/utilities/misc | stickers, memes, games, info, search, automation helpers | Preserve where functional; isolate broken external APIs with clear docs |
| Deployment/maintenance UX | `المطور.py`, `تحديث.py`, `تنصيب.py` | **Preserve features with safe redesign** (owner-sec, GitHub Releases update, T3rmx install/deploy info) |

## 4. VC/Music feature mapping (special handling)

| Element | Current state | Depends on missing external JepVc? | T3rmx action |
|---|---|---|---|
| `VCMODE`/`VC_SESSION` config flags | Present in config/startup | Indirectly | Keep as compatibility flags; route through `T3rmx-VC` config/adapter |
| External VC repo auto-install (`T3rmx/JepVc` -> `t3rmxvc`) | Present in legacy startup/main | **Yes** | Remove unsafe auto-clone; replace with documented, optional, verified-backend hook/interface (no invented source) |
| User-facing VC/music commands/help | Referenced in help/menus (e.g. enable mode, join/leave call, play/queue/pause/skip) | **Yes (runtime backend)** | Preserve command surface/help where possible; map to adapter calls; return clear “backend not configured/available” when missing |
| In-repo music helpers | `helpers/functions/musictool.py`, `plugins/اغنية.py` (download/lyrics utilities) | No | Preserve and refactor/rebrand; integrate with adapter when available |

## 5. Deployment feature mapping

| Platform | Legacy | T3rmx deliverable |
|---|---|---|
| Heroku | Procfile/Dockerfile/heroku patterns in lineage | `app.json` (root) + Deploy button targeting `https://github.com/T3rmx/T3rmx-UserBot`, worker config, env schema |
| Railway | lMl10l-style template/env UX (example provided) | `railway.json` + complete repo-based config, preserved env names/defaults, docs for any external template publication |
| Docker | legacy upstream-cloning Dockerfiles | root `Dockerfile` + `docker-compose.yml` (and `T3rmx-Deploy/docker/` docs) using in-repo source |
| VPS/Linux | ad-hoc scripts | `T3rmx-Deploy/vps/` install/run scripts + systemd unit + direct Linux execution docs |

## 6. Known blockers / items requiring explicit documentation
- **Missing verified JepVc backend source:** full call-control/music playback in voice chats cannot be completed without a verified implementation; adapter and docs will specify integration contract and current status.
- **Unverifiable external APIs/services used by some plugins:** preserve plugins but isolate/configure and document failures or provider changes.
- **No real secrets in workspace:** runtime validation of Telegram login/session/bot connectivity and some platform deployments requires user-provided credentials outside source control.
