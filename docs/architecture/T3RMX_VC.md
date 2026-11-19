# T3rmx-VC Architecture & Status

## Summary
Voice chat/music command UX exists in the legacy feature set, but the original implementation depended on runtime installation of an external `JepVc` repository (`jepthonvc`) that is **not verified or bundled** in this migration. T3rmx replaces that unsafe mechanism with an in-repo adapter module.

## Components
- `T3rmx-VC/t3rmx_vc/adapter.py`: backend selection, status/capability reporting, and base interface.
- `T3rmx-VC/t3rmx_vc/commands.py`: graceful registration/response layer for preserved VC/music command names when no verified backend is available.
- `T3rmx-VC/README.md`: usage/status and security policy.
- Application config hooks: `VCMODE`, `VC_SESSION`, `T3RMX_VC_ENABLED`, `T3RMX_VC_BACKEND`, `T3RMX_VC_SESSION`.

## Preserved vs backend-dependent
| Capability | Status in T3rmx initial build |
|---|---|
| VC config variables and integration hooks | Preserved |
| In-repo music/download helper utilities (where present) | Preserved (dependency-dependent) |
| Call join/leave, live playback/control in voice chats | Requires verified backend; currently unavailable by default |
| Runtime auto-clone of external VC repo | Removed (unsafe) |

## Future integration path
1. Add a verified backend implementation under `T3rmx-VC/` (or as a reviewed, pinned/vendored component).
2. Register backend in `get_vc_backend()` behind explicit configuration.
3. Map existing command handlers to adapter operations with graceful fallback messages.
4. Add tests for availability reporting and command behavior.
