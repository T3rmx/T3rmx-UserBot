# Deploy to Railway

T3rmx UserBot includes a `railway.json` configuration and `Dockerfile` for Railway deployment from this repository.

## Deploy steps
1. Fork or use <https://github.com/T3rmx/T3rmx-UserBot>.
2. In Railway, create a new project and choose **Deploy from GitHub repo**.
3. Select the repository and branch/release to deploy.
4. Railway will build using the repository `Dockerfile` as specified in `railway.json`.
5. Add required environment variables in the service **Variables** tab (see `.env.example` / `app.json`).
6. Deploy/redeploy. The service starts with `python3 -m JoKeRUB`.

## Required variables
- `APP_ID`, `API_HASH`, `STRING_SESSION`, `TG_BOT_TOKEN`, `TG_BOT_USERNAME`
- Recommended: `TZ=Asia/Aden`, `ENV=production`, `ALIVE_NAME`
- Optional: `DATABASE_URL`, command handlers, VC variables

## Railway template publication
This repository contains complete Railway deployment configuration, but a public Railway template ID/URL cannot be invented here. To publish an external Railway template, create it from this repository in your Railway account/workspace and document the resulting template link in project communications.

## Notes
- No cron/keepalive jobs are added by default. Configure platform behavior according to your plan/needs.
- Keep secrets in Railway variables, not in committed files.
