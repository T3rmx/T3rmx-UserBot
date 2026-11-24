# T3rmx UserBot — Download & Import Inventory

**Date:** 2026-11-18  
**Workspace:** `/home/riyadh/Projects/T3rmx-UserBot`  
**Read-only audited sources:** `/tmp/opencode/t3rmx-audit/` (not modified)

## 1. Audited source snapshots

| Local snapshot | Upstream | Branch/ref | HEAD commit | License | Imported/used |
|---|---|---|---|---|---|
| `/tmp/opencode/t3rmx-audit/t3rmx` | audited upstream snapshot (local copy) | `master` | `becff9b70efa494d06439743d45d2476167e815e` | AGPL-3.0 (`LICENSE`) | **Yes (primary baseline).** Application/runtime code, plugins, handlers, assistant, core, sql helpers, helpers/utils, media utilities, scripts, config/deployment logic references imported into `T3rmx-UserBot/` (compatibility layout) and reworked. `.git`/`.github` not copied. |
| `/tmp/opencode/t3rmx-audit/lMl10l` | audited upstream snapshot (local copy) | `lMl10l` | `9498ab580ae1bdb106d463fcd8d37ad28854dfc2` | License present in snapshot (audited) | **Reference only.** Deployment/template/env concepts reviewed; insecure mutable runtime bootstrap/fetch patterns explicitly not reused. |
| `/tmp/opencode/t3rmx-audit/nekopack` | https://github.com/TgCatUB/nekopack | `master` | `ec24a75d4b24626d013fefbf84e117c8a189a1bf` | (audited lineage) | **Reference/attribution only.** CatUserBot/nekopack lineage reviewed for provenance and dependency context; no direct runtime assets copied beyond attribution awareness. |

## 2. Imported application content (from T3rmx baseline)

| Area | Destination (logical) | Notes |
|---|---|---|
| Core package/runtime | `T3rmx-UserBot/JoKeRUB/` | Main application package (core, utils, sql_helper, helpers, assistant, plugins, config support). Root symlinks preserved for compatibility. |
| Plugins | `T3rmx-UserBot/JoKeRUB/plugins/` (+ `T3rmx-Plugins/plugins` mapping) | Existing plugin set preserved; to be rebranded/secured/refactored for T3rmx compatibility. |
| Assistant | `T3rmx-UserBot/JoKeRUB/assistant/` (+ `T3rmx-Plugins/assistant` mapping) | Bot/inline/assistant handlers preserved and rebranded. |
| Database helpers | `T3rmx-UserBot/JoKeRUB/sql_helper/` | State/persistence modules preserved. |
| Helpers & media utilities | `T3rmx-UserBot/JoKeRUB/helpers/`, `T3rmx-UserBot/bin/` | Utility and media-processing helpers preserved; dependency/security audit required. |
| Resources/strings | `T3rmx-UserBot/ALJoker/`, `T3rmx-UserBot/l313l/` | Localization/resources retained for feature compatibility and rebranded; media/assets reviewed for licensing/necessity (owner-provided logo added separately). |
| Config/scripts | `T3rmx-UserBot/stringsetup.py`, legacy `sample_config.py`/`exampleconfig.py`/`Dockerfile`/`Procfile`/`README.md`/`requirements.txt` | Replaced or reworked into T3rmx-safe, in-repo equivalents. |

## 3. New T3rmx-authored assets (this repository)

| Asset | Path | Notes |
|---|---|---|
| Owner-provided branding logo | `assets/branding/t3rmx-logo.jpg` | Exclusive branding image supplied by project owner; used for T3rmx branding. |
| Audit/planning docs | `docs/audit/*.md` | Source provenance, audit, feature map, dependency/license audit, security audit, migration plan, download inventory. |
| Centralized config/auth helpers | `T3rmx-UserBot/JoKeRUB/t3rmx_config.py`, `T3rmx-UserBot/JoKeRUB/core/auth.py`, updated `sample_config.py` | Backward-compatible env handling, normalization, and owner-only authorization foundation. |
| Module scaffolding | `T3rmx-UserBot/`, `T3rmx-Deploy/`, `T3rmx-VC/`, `T3rmx-Plugins/`, `deploy/`, `docs/`, `config/`, `scripts/`, `tests/`, `vendor/` | Logical single-repo structure for application, deployment, VC, and plugins. |

## 4. Exclusions / non-imported or removed behaviors

- `.git` histories and `.github` workflows from upstream snapshots were **not copied** into the new repository.
- Mutable runtime bootstrap/update/fetch mechanisms (external zip/git clone at runtime, remote script execution, unverified external VC repo auto-install, in-app git-pull/pip/heroku self-mutation flows) are **not reused**; replaced with in-repo, pinned, explicit mechanisms.
- Upstream branding assets/media/links and auto-join behaviors are removed or replaced except where legally required for attribution/license notices.
- No secrets, session strings, tokens, or credentials were imported or generated.

## 5. Verification notes

- Inventory reflects current workspace state during initial migration/rebuild; subsequent commits (when permitted) should include final file-level provenance details for any vendored third-party artifacts in `vendor/` with license records.
