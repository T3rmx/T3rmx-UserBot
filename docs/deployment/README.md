# Deployment

T3rmx UserBot is designed to run from a single standalone repository: <https://github.com/T3rmx/T3rmx-UserBot>.

## Supported targets
- **Heroku**: container deploy using `app.json` and `Dockerfile` (see [HEROKU.md](HEROKU.md))
- **Railway**: Dockerfile-based deploy using `railway.json` (see [RAILWAY.md](RAILWAY.md))
- **Docker / Docker Compose**: local or server container runtime (see [DOCKER.md](DOCKER.md))
- **VPS / Linux (systemd)**: recommended for persistent self-hosted operation (see [VPS_LINUX.md](VPS_LINUX.md))
- **Direct Linux execution**: for development/manual runs (see [VPS_LINUX.md](VPS_LINUX.md#direct-linux-execution))

## Common requirements
- Telegram `APP_ID` and `API_HASH` from <https://my.telegram.org>
- User `STRING_SESSION` (Telethon)
- Assistant bot `TG_BOT_TOKEN` and `TG_BOT_USERNAME` (from @BotFather)
- `ALIVE_NAME` (optional), `TZ=Asia/Aden` (default), `ENV=production` (default)

`TG_BOT_USERNAME` may be provided with or without `@`; it is normalized internally.

## Notes
- All deployment assets are maintained in-repo; no runtime cloning of external repositories is required or enabled by default.
- Voice chat/music call-control features depend on a verified `T3rmx-VC` backend (adapter present, backend not bundled by default). See [../architecture/T3RMX_VC.md](../architecture/T3RMX_VC.md).
- Keep credentials/session strings out of source control. Use environment variables or platform secret stores.
