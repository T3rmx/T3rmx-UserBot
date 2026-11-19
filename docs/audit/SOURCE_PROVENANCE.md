# Source Provenance - T3rmx UserBot

This document records the audited upstream sources used to build this independent T3rmx repository. Upstream repositories were **not** modified or deleted; audited read-only copies are available at `/tmp/opencode/t3rmx-audit/` during migration.

## Upstream sources (audited)

| Component | Repository | Branch | Audited HEAD commit | Role in T3rmx |
|---|---|---|---|---|
| Application source | https://github.com/jepthoniq/jepthon | `master` | `becff9b70efa494d06439743d45d2476167e815e` | Primary runtime/application codebase (plugins, handlers, assistant, core, helpers, database helpers, media utilities, scripts, config logic) imported and rebranded |
| Deployment/bootstrap | https://github.com/jepthoniq/lMl10l | `lMl10l` | `9498ab580ae1bdb106d463fcd8d37ad28854dfc2` | Deployment concept/template reference (Railway/Heroku/VPS entrypoints and env model) redesigned into safe, in-repo, non-mutable deployment assets |
| Original lineage | https://github.com/TgCatUB/nekopack | `master` | `ec24a75d4b24626d013fefbf84e117c8a189a1bf` | Upstream deployment/pack lineage (CatUserBot) preserved for attribution/provenance |

## License and attribution
- The imported application lineage includes **GNU AGPL-3.0** licensing (`LICENSE` retained in repository root). All required upstream copyright/license notices must be preserved in accordance with applicable licenses.
- This repository is an independent rebranded project (**T3rmx UserBot**) owned/configured for `@vvsks` (ID `6023224495`), with T3rmx-specific runtime identity, configuration, and deployment. Upstream infrastructure, maintainer identities, and mutable runtime update/fetch mechanisms are not used.
- Branding assets from previous projects are not used. Project logo is owner-provided: `assets/branding/t3rmx-logo.jpg`.

## Import notes
- Application code imported from audited `jepthon` snapshot into repository working tree as the functional baseline to preserve features (plugins, handlers, assistant, DB helpers, media utilities, scripts).
- Legacy/insecure bootstrap behaviors from deployment repos (runtime source zip/git fetch from previous maintainers, remote script execution, silent auto-updates/auto-installs, forced joins) are removed or redesigned into explicit, controlled, in-repo mechanisms.
- Files containing previous maintainer branding/links/IDs are being rebranded to T3rmx (AR/EN) or neutralized where appropriate, while keeping required legal attribution.
