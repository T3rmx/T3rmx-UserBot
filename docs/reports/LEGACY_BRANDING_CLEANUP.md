# Legacy Branding Cleanup Report (reconciled status)

**Date:** 2026-11-19  
**Scope:** current uncommitted working tree (`/home/riyadh/Projects/T3rmx-UserBot`). Baseline inventory: `docs/audit/LEGACY_BRANDING_REPORT.md`, `docs/audit/LEGACY_BRANDING_REPORT.json` (provenance records; not modified). This is a current reconciliation with repo-wide pattern evidence, **not** a claim that every historical/internal identifier in the entire legacy-derived tree has been renamed.

## Evidence (repo-wide scans, excluding `.git`, `.venv311`, `__pycache__`; baseline legacy audit reports excluded where noted)
- **User-facing legacy source-brand strings removed from runtime/app surfaces:** no matches for `سورس الجوكر`, `قائمة اوامر الجوكر`, `T3rmx`, `T3rmx`, `@t3rmx_official`, `t3rmxsupport`, `t.me/t3rmx_official`, `T3rmx/T3rmx` under `T3rmx-UserBot/JoKeRUB`, `T3rmx-UserBot/ALJoker`, `T3rmx-UserBot/l313l`, `T3rmx-UserBot/sample_config.py`, `T3rmx-UserBot/stringsetup.py`, `T3rmx-VC`, root runtime/deployment files, or non-audit docs except intentional attribution/provenance/compatibility records listed below.
- **Arabic `الجوكر` in runtime/app code (`T3rmx-UserBot/JoKeRUB|ALJoker|l313l`, excluding caches):** 7 matches, all intentional **backward-compatibility aliases/help labels** preserving existing command/input behavior while primary UI shows T3rmx:
  - `T3rmx-UserBot/JoKeRUB/plugins/التجميع.py`: accepts legacy triggers `تجميع الجوكر/تجميع جوكر` alongside `تجميع تيرمكس/T3rmx`.
  - `T3rmx-UserBot/JoKeRUB/plugins/بنك.py`: accepts legacy bank name `الجوكر الاسلامي` alongside `تيرمكس/T3rmx الاسلامي`; help text marks legacy as compatible.
  - `T3rmx-UserBot/JoKeRUB/plugins/تفرعات الاوامر.py`: help lists T3rmx command and explicitly marks legacy alias `(متوافق: .تجميع الجوكر)`.
- **English `Joker` in runtime/app code:** none in scanned runtime/app paths after cleanup (`plugins/الاذاعه.py` comment and `plugins/ميمز.py` variable renamed to neutral/internal-safe forms).
- **`HuRe*` identifiers:** present as compatibility/internal code identifiers in core/plugins (e.g. `HuReClient`, internal variable names) — **not primary user-facing branding** in modified surfaces; broad rename deferred to avoid behavior regressions across legacy plugin set.
- **Old T3rmx/Joker branding links/names outside runtime app:** remain only in **attribution/provenance, legal, compatibility, and historical audit/report records** (see retained table). No user-facing runtime promotion/link to old T3rmx channels/repos found in modified runtime surfaces.
- **Assets:** `assets/branding/t3rmx-logo.jpg` is the designated branding logo (used by reviewed T3rmx surfaces such as `plugins/تنصيب.py` via `Config.T3RMX_LOGO`). Legacy image files remain in `T3rmx-UserBot/l313l/razan/resources/start/T3rmx.JPEG` and `T3rmx2.JPEG`; repo scans in this pass found no runtime code references to these filenames, but full runtime/media resource usage and user-facing presentation audit remains pending.

## Removed / cleaned in targeted passes (examples)
| Category | Action | Examples / notes |
|---|---|---|
| Runtime/plugin user-facing Arabic branding text | Rebranded to T3rmx / T3rmx UserBot | `core/inlinebot.py`, help/status/menu strings in `plugins/اوامري.py`, `plugins/تفرعات الاوامر.py` (except explicit compatibility labels), `plugins/الحاسبة.py`, `plugins/تنصيب.py`, `plugins/تحديث.py`, developer/info surfaces, multiple plugin messages/comments cleaned in prior and current passes. |
| User-facing examples/messages containing legacy name | Rebranded | `plugins/تفرعات الاوامر.py` timer example changed from `الجوكر` to `T3rmx`. |
| Runtime/plugin comments and cache text | Rebranded | `JoKeRUB/cache/readme.md`, `plugins/اضافة.py`, `plugins/البروفايل.py`, `plugins/التكرار.py`, `plugins/الثكيل.py`, `plugins/الحماية.py`, `plugins/الصلاة.py`, `plugins/الصورة.py`, `plugins/منوع.py`, etc. |
| Error reporting / status strings | Rebranded | `JoKeRUB/utils/decorators.py` traceback/report text changed from T3rmx wording to `T3rmx UserBot` / support link. |
| English legacy branding artifacts in runtime code | Removed/neutralized | `plugins/الاذاعه.py` comment, `plugins/ميمز.py` variable name (`Joker` -> `reply_to`) in current pass. |
| TTS/user-visible status variable text | Rebranded (prior pass) | `plugins/ترجمة صوتية.py` uses neutral `status_event`/T3rmx-appropriate flow in modified code path. |
| VC/update/developer surfaces | Rebranded and safety-gated | Read-only update checker, owner-only developer controls, unavailable-backend VC messaging aligned to T3rmx identity. |

## Retained intentionally (compatibility / attribution / legal / audit provenance)
| Item | Classification | Reason / constraint |
|---|---|---|
| `JoKeRUB` package/module layout, imports, entrypoint, compatibility symlinks | Compatibility (technical) | Deeply embedded across runtime/tests/deployment; renaming risks breaking preserved functionality. |
| `l313l`, `ALJoker`, `HuReClient` and many legacy internal symbol names | Compatibility (technical/internal) | Legacy plugin/core coupling; not presented as T3rmx brand in reviewed user-facing surfaces. |
| Legacy command/input aliases containing `الجوكر` in `التجميع.py`, `بنك.py`, and explicit compatibility label in `تفرعات الاوامر.py` | Backward compatibility (user-facing alias) | Preserves existing user workflows/commands; primary naming shows T3rmx. |
| `sample_config.py` `PMPERMIT_TEXT_T3rmx` and similar legacy config/key names | Compatibility (config/API surface) | May be required by existing user configs; changing can break deployments. |
| `README.md`, `BRANDING.md` upstream lineage references/URLs (T3rmx/CatUserBot/lMl10l provenance) | Attribution/provenance (intentional) | Honest derivation, source provenance, and licensing context; AGPL/compliance transparency. |
| `docs/architecture/T3RMX_VC.md` historical note about legacy external `t3rmxvc` backend | Technical documentation (intentional) | Explains why no unverified backend is bundled/fabricated. |
| `docs/audit/*` baseline/provenance reports and inventories | Audit/provenance records | Historical evidence and traceability; may contain legacy names/links by necessity. |
| `docs/reports/*` historical statements describing removed legacy branding/links | Reporting evidence | Records what was found/removed/retained. |
| `LICENSE` and legally required notices | Legally required attribution | Must be preserved. |
| Legacy resource files `T3rmx-UserBot/l313l/razan/resources/start/T3rmx.JPEG` and `T3rmx2.JPEG` | Legacy resources (traced in this pass, retained pending exhaustive audit) | Files exist; repo-wide filename/reference scans in this pass found **no runtime code references** to these filenames in reviewed workspace surfaces. Reviewed install/inline branding path (`plugins/تنصيب.py`) uses `Config.T3RMX_LOGO` / `assets/branding/t3rmx-logo.jpg`. Retained for compatibility; not removed/replaced pending exhaustive runtime/media/user-facing verification. |

## Unresolved / pending reconciliation
- **Exhaustive manual/runtime verification** of all user-facing outputs across 100+ plugins, assistant/inline handlers, callbacks, media captions, stickers, errors, and localized strings (static scan cannot prove every runtime message).
- **Legacy media/resource audit** (images/GIFs/stickers/text assets) to confirm no old branding is presented to users in unreviewed flows; decide retain-for-compat vs replace/remove with attribution-safe alternatives.
- **Internal identifier renames (`HuRe*`, `JoKeRUB`, `l313l`, `ALJoker`, etc.)** only with compatibility shims and regression tests; not required for user-facing rebrand but may remain in code.
- **Config/env compatibility keys** (e.g. `PMPERMIT_TEXT_T3rmx`) should be mapped to T3rmx-native aliases in a future pass while preserving backward compatibility.

## Conclusion
Critical user-facing legacy source branding/links targeted for removal are not present in scanned runtime/app surfaces outside intentional compatibility aliases and retained attribution/provenance/legal records. Legacy start-resource filenames (`T3rmx.JPEG`, `T3rmx2.JPEG`) were traced in this pass with no runtime code references found in scans and are retained pending exhaustive runtime/media/user-facing verification. Due to the size and legacy nature of the codebase, **full exhaustive user-facing/runtime branding reconciliation is not yet complete** and requires additional manual verification and possible resource/alias follow-up.
