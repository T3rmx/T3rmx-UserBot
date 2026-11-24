# T3rmx UserBot — Feature Inventory (Imported Baseline)

**Source:** audited `T3rmx` application baseline (`becff9b70efa494d06439743d45d2476167e815e`)
**Inventory date:** 2026-11-18  
**Status:** comprehensive baseline inventory for preservation during T3rmx migration/rebrand. All listed feature areas are in-scope to preserve unless unsafe mechanics require redesign (with equivalent functionality/behavior where feasible).

## 1. Runtime & platform
- Telethon-based userbot client with string-session authentication.
- Assistant/bot client (BotFather bot token) for inline/help/callback and PM/management features.
- Async event/command handling with custom client wrappers, decorators, sudo/owner checks, and plugin command registration.
- Plugin loader for core `plugins/` and `assistant/` modules; dynamic module loading/unloading support.
- Startup/bootstrap flow, logger/chat integration hooks, local web server bind (for platform health/port binding where configured).
- SQL-backed persistence helpers (`sql_helper`) for settings/state across many features.
- Localization/resources (`ALJoker/strings`, Arabic-first command/help surfaces) and bundled media/resources.

## 2. Core command & control
- Configurable command handlers/prefixes (`.`, `،` and legacy/customizable handlers).
- Help/inline command menus, command info/metadata, plugin categorization.
- Alive/ping/status/info commands and customizable templates/media.
- AFK, profile/name/bio/pic/time automation/customization, vars management.
- Sudo/admin permission model (to be centralized and secured under T3rmx ownership).
- Owner/developer controls (sec/restricted operations) — preserved in intent, restricted to configured T3rmx owner.

## 3. Administration & moderation (user/group management)
- Group/user administration utilities (ban/kick/mute/unmute/restrict/promote/demote/pin/purge/delete/etc., as provided by plugins).
- Welcome/goodbye, filters/replies/notes, blacklist/whitelist/antiflood/spam controls (plugin-dependent).
- PM permit/PM logging/assistant PM management and forwarding flows.
- Chat/user info, member tools, invite/join helper commands (user-initiated feature context).

## 4. Media, download, and processing
- YouTube/media download/search and audio/video handling helpers (`yt-dlp`-based and related utilities).
- File upload/download helpers, telegraph/media conversion utilities, stickers/GIF/image tools.
- FFmpeg/mediainfo-dependent processing paths (where installed/configured).
- Lyrics, metadata, thumbnail and inline media interactions.

## 5. Assistant & inline features
- Inline query handlers for help, utilities, and interactive UI elements.
- Bot-side admin/PM/broadcast/user-management commands for the assistant bot (owner-scoped).
- Callback/button-driven menus and helper flows.

## 6. Voice chat / music (partially backend-dependent)
- Configuration flags and user-facing command/help surfaces for VC/music mode (enable/disable, join/leave/play/queue/control concepts in legacy UX).
- In-repo music helper utilities (download/lyrics/search helpers) present.
- **External runtime VC backend dependency in legacy (`JepVc`/`t3rmxvc`) not verified/bundled:** call-control/playback in voice chats requires a verified backend; preserved via T3rmx-VC adapter interface and graceful status reporting.

## 7. Utilities & miscellaneous plugin surface
Large plugin collection (104 plugin files, 12 assistant modules) covering (representative, non-exhaustive):
- Search/info/tools, automation helpers, text/formatting, fun/entertainment, games, quotes, fake actions, and miscellaneous Telegram utilities.
- External API integrations for optional features (weather, OCR, translation, search, etc.) where API keys/services are configured and available.
- Telegraph/templating/inline content generation.

## 8. Deployment & maintenance (legacy, to be redesigned safely)
- Heroku/Docker/VPS-oriented legacy artifacts and scripts (some unsafe/mutable in upstream lineage).
- Self-update/deploy/install plugins and flows (`المطور`, `تحديث`, `تنصيب`) — **redesigned in T3rmx** for centralized owner auth, safe GitHub Releases checks, and in-repo deployment guidance.

## 9. Preservation notes
- Feature behavior and command compatibility are preserved where technically and safely possible.
- Unsafe mechanisms (runtime mutable code fetch/exec, silent auto-updates/installs, forced project joins, hardcoded third-party identities/credentials) are removed or gated with safe alternatives.
- Arabic and English user-facing surfaces are rebranded to T3rmx during migration.
