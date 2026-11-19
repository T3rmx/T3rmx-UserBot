# T3rmx UserBot — Architecture (Initial)

## Overview
T3rmx UserBot is a single, standalone repository containing the application runtime, plugin system, deployment assets, and an independent voice-chat (VC) integration module. The design preserves legacy feature compatibility while introducing centralized configuration, authorization, safer runtime behavior, and reproducible deployment.

## Logical modules (in-repo)

- **`T3rmx-UserBot/`**: Application runtime and compatibility layout.
  - `JoKeRUB/`: core package (entrypoint/bootstrap, Telethon client/session, handlers, plugin loading, helpers, SQL helpers, assistant, plugin set).
  - `ALJoker/`, `l313l/`, `bin/`: retained compatibility resources/utilities required by preserved features (legacy directory names kept for runtime compatibility).
- **`T3rmx-Plugins/`**: Logical view/mapping for plugin and assistant modules (symlinked to the runtime plugin locations for compatibility).
- **`T3rmx-VC/`**: Independent VC/music integration layer.
  - Adapter/interface, backend capability reporting, configuration hooks.
  - No unverified external VC backend is bundled or auto-installed.
- **`T3rmx-Deploy/`** (+ root platform files): Heroku, Railway, Docker, VPS/systemd, and Linux deployment assets targeting `https://github.com/T3rmx/T3rmx-UserBot`.
- **`docs/`**: Audit, architecture, deployment, development, dependency, and security documentation.
- **`tests/`**: Automated tests for critical components (config/auth/update/adapter/deploy config checks).
- **`config/`, `scripts/`, `vendor/`, `assets/`**: Examples/scripts, vetted vendored artifacts (if any, with provenance), and branding assets.

## Runtime flow (high level)
1. **Configuration load**: environment variables (backward-compatible names preserved) are normalized via centralized config (`sample_config.py` / T3rmx helpers). Defaults: `TZ=Asia/Aden`, `ENV=production`; `TG_BOT_USERNAME` accepted with/without `@` and normalized without `@`.
2. **Session/client init**: Telethon user client and assistant bot client initialized from provided credentials/session.
3. **Startup**: safe startup checks/logging; optional log-group integration only when explicitly configured; plugin and assistant modules loaded from in-repo paths.
4. **Command/handler dispatch**: legacy-compatible plugin handlers and assistant/inline handlers serve features; authorization enforced through centralized checks (owner/developer defaults to `@vvsks` / `6023224495`).
5. **Optional subsystems**: VC features routed through `T3rmx-VC` adapter; unavailable backends fail gracefully with clear status instead of unsafe runtime fetch/install.

## Security and control boundaries
- **Authorization**: centralized owner/dev/sudo policy; sensitive controls (e.g. developer sec/update actions) restricted to authorized owner.
- **Update mechanism**: read-only GitHub Releases checks for `T3rmx/T3rmx-UserBot` (current vs latest, changelog). No auto-install, no git pull/pip/heroku mutation from runtime, no arbitrary remote code execution.
- **Dependencies/runtime**: pinned/audited dependencies; no silent runtime package installs or unverified external repository cloning by default.
- **Secrets**: credentials/sessions/tokens supplied via environment/config outside source control; no hardcoded secrets.

## Compatibility strategy
- Preserve legacy env var names and major plugin/command behavior.
- Keep `JoKeRUB` package/import paths and entrypoint (`python -m JoKeRUB`) stable for existing plugins.
- Isolate non-portable or backend-dependent functionality (notably VC call-control backend) behind adapters and configuration with documented status.

## Known constraints
- Full VC call-control/music playback depends on a verified backend implementation; T3rmx provides an in-repo adapter and hooks but does not invent external backend code.
- Some legacy plugins rely on third-party APIs/services whose availability or behavior may vary; they remain configurable and should degrade gracefully.
