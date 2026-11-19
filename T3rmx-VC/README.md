# T3rmx-VC

`T3rmx-VC` is the independent, modular voice-chat (VC) integration layer for **T3rmx UserBot**.

## Goals
- Preserve existing VC/music-related configuration hooks and command surfaces where possible.
- Isolate backend-specific behavior behind a stable adapter/interface.
- Avoid unsafe runtime fetching, cloning, or execution of unverified external VC sources.
- Allow optional, verified backend integrations in the future without changing the whole application.

## Current status
- **Adapter/module:** present in-repo (`t3rmx_vc/`).
- **Verified call-control backend:** not bundled in this repository.
- **Behavior:** when VC features are not backed by a verified implementation, the adapter reports a clear unavailable/not-configured status. Features that do not require a call backend (e.g. some in-repo media/download helpers) may still function if their dependencies are installed.

## Configuration (compatibility)
- `VCMODE` / `T3RMX_VC_ENABLED`: enable VC integration intent (default: disabled).
- `VC_SESSION` / `T3RMX_VC_SESSION`: VC session credential (user-provided, optional).
- `T3RMX_VC_BACKEND`: backend selector (default: `none`).

## Security policy
- No automatic download/installation of external VC repositories at runtime.
- No invented or unverified JepVc backend source included.
- Any future backend integration must be explicitly reviewed, license-compatible, pinned/vendored as appropriate, and documented.

## Integration contract (initial)
Backends should implement a minimal interface compatible with `BaseVCBackend` in `t3rmx_vc/adapter.py` and expose capability/status reporting so the userbot can degrade gracefully when unavailable.
