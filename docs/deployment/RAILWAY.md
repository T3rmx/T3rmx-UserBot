# Deploy to Railway

This repository includes Railway deployment configuration (`railway.json`, `Dockerfile`, `app.json`) for deploying **your own independent** T3rmx UserBot instance.

> **Public template status:** A real, published Railway Marketplace template URL/ID is not included here unless it has been actually created, published, and verified. Do not fabricate template links.

## Deployment model (template-ready)

A correct public/template deployment must provide:

- **Application service** built from this repository (`main`), using the included `Dockerfile`
- **Separate PostgreSQL service per deployment** (not shared, not reused from any other deployment)
- **Deployer-provided credentials/identity** (`STRING_SESSION`, `APP_ID`/`API_HASH`, `TG_BOT_TOKEN`, `TG_BOT_USERNAME`, `T3RMX_OWNER_ID`)
- **`DATABASE_URL` reference** pointing to that deployment's own PostgreSQL service
- Public networking and a passing healthcheck on **`/health`**

## Application service

- **Source:** <https://github.com/T3rmx/T3rmx-UserBot> (branch: `main`)
- **Builder:** Dockerfile (`railway.json` / `Dockerfile`)
- **Start command:** `python3 -m JoKeRUB`
- **Healthcheck path:** `/health` (also serves `/`)
- **Port:** Railway-provided `PORT` is supported by the app's web/health server bind
- **Restart policy:** `ON_FAILURE` (configured in `railway.json`)

## PostgreSQL service

- Provision a **new PostgreSQL service for every deployment** (e.g. Railway PostgreSQL template/image).
- Attach persistent storage/volume as provided by the PostgreSQL service.
- Connect the app using a **Railway reference variable** to the deployment's own Postgres URL (do not hardcode credentials).
- Verify actual variable names in the target Railway environment before wiring references.
- Database initialization/tables are created on startup; `postgres://` URLs are normalized to `postgresql://` for compatibility.

**Important:** hosted/Railway production deployments must use PostgreSQL. The application is configured to reject ephemeral SQLite fallback in hosted environments to prevent data loss.

## Required variables

| Variable | Required | Description |
|---|:---:|---|
| `STRING_SESSION` | Yes | User's Telethon string session |
| `APP_ID` | Yes | Telegram API ID (`API_ID` alias supported) |
| `API_HASH` | Yes | Telegram API hash |
| `TG_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `TG_BOT_USERNAME` | Yes | Assistant bot username (with or without `@`) |
| `T3RMX_OWNER_ID` | Yes | Telegram numeric ID of the deployer/owner |
| `DATABASE_URL` | Yes (hosted/Railway) | PostgreSQL URL/reference for this deployment's own database |

## Optional variables

| Variable | Default | Description |
|---|---|---|
| `ALIVE_NAME` | `T3rmx UserBot` | Display name |
| `TZ` | `UTC` | Timezone |
| `ENV` | `production` | Runtime environment |
| `COMMAND_HAND_LER` | `.` | Primary command prefix |
| `SUDO_COMMAND_HAND_LER` | `،` | Sudo command prefix |
| `VCMODE` | `false` | VC integration intent (backend-dependent) |
| `VC_SESSION` | empty | Optional VC session |
| `API_ID` | — | Backward-compatible alias for `APP_ID` |
| `OWNER_ID` | — | Backward-compatible alias for `T3RMX_OWNER_ID` |

## Security requirements

- Never include or copy production/personal secrets into a template or repository.
- Each deployer must provide their own Telegram credentials/session/token and `T3RMX_OWNER_ID`.
- Each deployment must get its own PostgreSQL database and data.
- Do not expose secrets in logs, docs, screenshots, or commits.

## First-time deploy steps (manual/from repo)

1. Create a Railway project and deploy from <https://github.com/T3rmx/T3rmx-UserBot> (`main`).
2. Add a PostgreSQL service in the same project/environment.
3. Set required variables on the app service; set `DATABASE_URL` as a reference to the Postgres service URL for this deployment.
4. Deploy/redeploy and verify build/startup logs.
5. Verify `GET /` and `GET /health` return `200`.
6. Verify Telegram startup and that privileged commands are restricted to `T3RMX_OWNER_ID`.

## Publishing a real public template (maintainer workflow)

To publish a genuine Railway template (not just repo instructions):

1. Create a **clean** project/config with no personal credentials or production data.
2. Ensure app service source is this repo (`main`) and a separate PostgreSQL service is included with correct reference variables.
3. Generate a template draft (`railway templates create --project <clean-project-id> --environment <env> --json`) and configure/verify template variables and metadata in Railway.
4. Publish with accurate metadata and overview (`railway templates publish ...` or dashboard), then obtain the real public template code/URL.
5. Run **at least two fresh, independent deployments** from the published template URL and verify build, startup, healthchecks, DB init/CRUD/persistence across restart, and isolation (no inherited data/credentials).
6. Only after verification, update `README.md` with the real Deploy on Railway button/URL.

## Evidence checklist (for a valid published template)

- Public template URL and deploy button
- Independent deploy test #1 and #2 results
- Healthcheck evidence (`/`, `/health` = 200)
- Database persistence/CRUD evidence
- Confirmation that no production credentials/data were reused

See [README.md](../../README.md) and [`.env.example`](../../.env.example).
