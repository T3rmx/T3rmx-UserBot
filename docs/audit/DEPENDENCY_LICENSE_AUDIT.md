# T3rmx UserBot — Dependency & License Audit (Initial)

**Status:** audit/planning baseline for implementation. All dependencies must be reviewed for license, maintenance, security, and necessity; pinned to stable versions or immutable commits; vendored only when legally/technically appropriate; and documented with purpose.

## 1. Current/legacy dependency sources

### 1.1 Root `requirements.txt` (imported T3rmx baseline)
| Dependency | Spec | Notes / risk | T3rmx action |
|---|---|---|---|
| `googletrans` | `==3.1.0a0` | Alpha/unofficial API client; instability risk | Keep only if required by features; evaluate maintained alternative; pin explicitly and document |
| `yt-dlp` | `git+https://github.com/yt-dlp/yt-dlp` | **Unpinned VCS** (supply-chain/reproducibility risk) | Pin to immutable commit or vetted release; consider vendoring wheel/sdist if appropriate; document license (Unlicense) |
| `Telethon` | unpinned | Core MTProto client; API/behavior changes across versions | Pin to tested stable version; validate session/plugin compatibility |
| `ipaddress` | unpinned | Stdlib backport (Py2-era); unnecessary on modern Python | Remove if unused/obsolete |

### 1.2 lMl10l manifest (audited reference, broad runtime set)
Includes (selection): `Telethon==1.25.2`, `aiohttp`, `Flask/gunicorn`, `SQLAlchemy==1.3.23`, `psycopg2-binary`, `pymongo/motor`, `gitpython`, `heroku3`, `Pillow`, `ffmpeg/media`-adjacent tools deps, `telegraph`, etc., plus **unpinned git deps**: `buddhhu/img2html`, `alexmercerind/youtube-search-python`, `cinemagoer/cinemagoer`.

### 1.3 nekopack manifest (audited lineage reference)
Large feature set including many of the above and additional **unpinned git deps**: `Jisan09/search-engine-parser`, `Jisan09/Telethon@test`, `goldsmith/Wikipedia`, `sandy1709/py-googletrans`, `alexmercerind/youtube-search-python`, `yt-dlp/yt-dlp`.

## 2. Immutable commit pins resolved (for git-based deps if retained)

| Package/repo | URL | Pinned commit (HEAD at audit time) | License (to verify before vendoring/use) | Purpose (if used) |
|---|---|---|---|---|
| yt-dlp | https://github.com/yt-dlp/yt-dlp | `2d596f4882a2d6e6414836bccd9fd3fb1e1534a2` | Unlicense (verify) | Media download/extraction features |
| img2html | https://github.com/buddhhu/img2html.git | `3fce5bbccf3561b357714a8e4200849d6ef5a314` | Verify | Image/HTML utility features (if required) |
| youtube-search-python | https://github.com/alexmercerind/youtube-search-python | `fc12c05747f1f7bd89d71699403762b86b523da5` | Verify (MIT commonly reported) | YouTube search features (if required) |
| cinemagoer | https://github.com/cinemagoer/cinemagoer | `1c7fc546847f190f82ad72d965aef59e38785e39` | Verify (GPL-family historically) | Media/IMDb features (if required) |

> **Policy:** no unpinned `git+` dependencies in final manifests. Prefer PyPI stable releases where suitable; otherwise pin `git+<url>@<commit>`. Verify each license is compatible with project distribution/use before vendoring.

## 3. System/runtime dependencies (to document and minimize)
- **Python** (supported 3.x; target modern 3.11+ compatible runtime), **ffmpeg**, **mediainfo** (where media features used), **p7zip** (if archive features used), network access for user-initiated feature APIs/Telegram.
- **Node/npm**: present in legacy images for unused/unclear needs; remove unless a preserved feature requires it (audit during implementation).
- **Fonts/assets**: audit bundled fonts/resources in `l313l/razan/resources` for licensing and necessity.

## 4. Dependency decisions (planned)

| Decision | Rationale |
|---|---|
| Consolidate into a single, documented, pinned app dependency manifest | Reproducibility and clarity |
| Remove Heroku-specific runtime coupling where not required; keep optional only if needed | Reduce unnecessary deps (`heroku3` etc.) |
| Avoid `Telethon@test`/fork VCS deps | Stability and trust |
| Gate optional/heavy features by configuration and graceful degradation | Minimize mandatory footprint and failure impact |
| Vendor only reviewed, license-compatible artifacts when necessary | Offline reproducibility without legal risk |

## 5. Required outputs during implementation
- `T3rmx-UserBot/requirements.txt` (or canonical manifest) with pinned versions/commits and comments by purpose.
- `docs/DEPENDENCIES.md` (or equivalent) listing every external dependency, purpose, license, and source/pin.
- `vendor/` populated only with vetted artifacts (if used) plus provenance/license notes.
- Removal or replacement of unnecessary/unsafe packages (`ipaddress` backport, unneeded build-time remote scripts, unused Node toolchain, etc.) as validated.
