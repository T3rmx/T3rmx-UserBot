# T3rmx UserBot — Comprehensive Migration & Rebrand Plan

## 1. Objectives
Deliver an independent, maintainable, secure, fully rebranded **T3rmx UserBot** in a single standalone repository (`https://github.com/T3rmx/T3rmx-UserBot`) that preserves all existing application features and backward-compatible configuration, with in-repo deployment for Heroku/Railway/Docker/VPS/Linux and no first Git commit until initial implementation, documentation, and security review are complete.

## 2. Confirmed decisions (inputs)
- **Owner/dev (default, only):** `@vvsks` / `6023224495` (centralized auth; sec mechanism retained for real dev).
- **Deployment targets:** all configs target main repo; Heroku `app.json` + button, Railway `railway.json` + complete config, Dockerfile + docker-compose, VPS scripts + systemd, Linux direct execution.
- **Railway/env compatibility:** preserve `STRING_SESSION`, `TG_BOT_USERNAME`, `TZ`, `ENV`, `APP_ID`, `API_HASH`, `ALIVE_NAME`, `TG_BOT_TOKEN` (+ other legacy vars). Defaults: `TZ=Asia/Aden`, `ENV=production`; `TG_BOT_USERNAME` accepted with/without `@` and normalized internally without `@`. No unnecessary cron/keepalive.
- **T3rmx-VC:** independent modular component inside repo; no invented/unverified JepVc source; audit/preserve existing VC-related code and hooks; adapter/interface; configurable/disableable/testable; document functional vs backend-required.
- **Dependencies:** audit license/maintenance, pin to stable/immutable, vendor only when legally/technically appropriate, document purpose; no old untrusted repos.
- **Update system:** GitHub Releases for `T3rmx/T3rmx-UserBot` (current vs new, changelog), no auto-install, explicit developer-authorized action, no arbitrary downloads/exec.
- **Logical modules in single repo:** `T3rmx-UserBot/`, `T3rmx-Deploy/`, `T3rmx-VC/`, `T3rmx-Plugins/`.

## 3. Execution phases

### Phase A — Audit & planning (completed baseline)
- [x] Source/dependency/feature/security audit and provenance.
- [x] Feature-to-module mapping, licensing/compatibility risks, reuse/restructure/replace classification.
- Deliverables: `docs/audit/{SOURCE_PROVENANCE,AUDIT_REPORT,FEATURE_MAP,DEPENDENCY_LICENSE_AUDIT,SECURITY_AUDIT,MIGRATION_PLAN}.md`.

### Phase B — Repository/module structure and deployment foundation
- Establish logical module directories and compatibility-preserving layout:
  - `T3rmx-UserBot/`: application source/runtime (core app package and support modules) organized for maintainability while preserving import/runtime compatibility.
  - `T3rmx-Plugins/`: plugin collection organization mapped to runtime-loaded plugins.
  - `T3rmx-VC/`: adapter, interfaces, backend contract, config/docs, integration hooks.
  - `T3rmx-Deploy/`: Heroku/Railway/Docker/VPS assets and scripts (+ root-level platform-required files).
- Add in-repo entrypoints for Linux/VPS/Docker/Railway/Heroku (safe, no mutable external source fetch).

### Phase C — Core refactor (security, config, auth, startup)
- Centralize configuration (`T3RMX_*` + legacy keys), validation, normalization, and defaults.
- Centralize authorization/permissions (owner/dev/sudo policy), remove all legacy hardcoded developer IDs, update core checks (`client`, `decorators`, inline/assistant guards).
- Harden startup/plugin loading: no forced joins, no unverified external clones, no silent updates/installs, controlled logging, graceful behavior.
- Preserve `JoKeRUB` runtime compatibility where required for plugins and commands.

### Phase D — Feature-preserving plugin and system updates
- Rebrand all plugins/assistant/help/resources/strings (AR/EN) to T3rmx; replace old media/links with T3rmx assets/text.
- **`المطور.py`:** retain sec/control mechanism restricted to centralized owner/dev (`6023224495`), rebranded owner/project display.
- **`تحديث.py`:** implement GitHub Releases-based update check/info (current/latest/changelog) for `T3rmx/T3rmx-UserBot`; developer-only explicit actions; no auto-install, no git pull/pip/heroku mutation, no arbitrary downloads.
- **`تنصيب.py`:** rebrand to T3rmx deployment/install guidance and repo links; preserve inline/help UX.
- Audit and neutralize insecure patterns across plugins (remote exec/install/credential exposure) without removing legitimate features.

### Phase E — T3rmx-VC module
- Create `T3rmx-VC/` with: adapter interface, backend registry/config, null/unavailable backend implementation, integration points from app config/startup/commands, and tests/docs.
- Preserve existing VC-related config/strings/hooks; clearly report unavailable backend where required.

### Phase F — Dependencies and vendoring
- Produce pinned, audited dependency manifest(s) and `docs/DEPENDENCIES.md`.
- Pin git dependencies to immutable commits or replace with stable releases; vendor vetted artifacts into `vendor/` when appropriate with license/provenance records.
- Ensure Docker/VPS/Linux installs use in-repo/pinned sources only.

### Phase G — Deployment artifacts
- **Heroku:** `app.json` with required/preserved env vars, formation, build config, deploy button targeting main repo.
- **Railway:** `railway.json` and deployment config/docs preserving specified env vars/defaults; document external template publication if desired (no invented ID).
- **Docker:** production-safe `Dockerfile` + `docker-compose.yml`.
- **VPS/Linux:** install scripts, env template, systemd service, direct-run instructions.
- No unnecessary cron/keepalive.

### Phase H — Tests, documentation, security review
- Add automated tests: config normalization/validation, auth/owner checks, update release parsing/comparison, import/startup smoke (non-secret/mocked), VC adapter behavior, deployment config sanity checks.
- Complete docs: `README.md`, `BRANDING.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, architecture, deployment guides, dependency/license notes, VC status, audit reports.
- Final security/rebrand sweep: no secrets, no old hardcoded IDs/unsafe auto-behaviors, attribution preserved.

### Phase I — Release readiness (no commit yet per instruction)
- Verify local checks/tests pass as feasible without external credentials.
- Prepare clean commit structure proposal; **do not create first Git commit** until initial implementation, documentation, and security review are complete.

## 4. Risk register

| Risk | Impact | Mitigation |
|---|---|---|
| VC backend unavailable | Music/call-control partially unavailable | Adapter + clear status/docs; preserve hooks and in-repo helpers |
| Dependency/license incompatibility for vendoring | Legal/compliance risk | Verify licenses; prefer pinned external manifests; vendor only compatible artifacts |
| Plugin regressions during rebrand/refactor | Feature breakage | Compatibility-preserving edits, incremental testing, import/syntax checks |
| Telegram/platform behavior differences | Runtime/connectivity issues | Backward-compatible config/session handling; documented validation steps |
| Large legacy surface area | Incomplete cleanup | Systematic scans and audit checklists before completion |

## 5. Definition of done (initial implementation)
- All planned modules/deploy paths/docs/tests present in-repo and functional by static/runtime checks feasible without secrets.
- Full T3rmx rebrand applied; legacy insecure mechanisms removed/guarded; owner auth centralized to `6023224495`.
- Audits, dependency records, VC status, and deployment instructions documented.
- No credentials/secrets committed; no first Git commit created yet.
