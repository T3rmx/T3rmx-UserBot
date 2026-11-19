# Deploy to Heroku

T3rmx UserBot supports Heroku deployment from this repository using the container stack.

## Prerequisites
- Heroku account and Heroku CLI (optional)
- This repository/fork: <https://github.com/T3rmx/T3rmx-UserBot>
- Required Telegram credentials (`APP_ID`, `API_HASH`, `STRING_SESSION`, `TG_BOT_TOKEN`, `TG_BOT_USERNAME`)

## Option A: Deploy from GitHub (Dashboard)
1. Fork or use the repository.
2. In Heroku, create a new app.
3. Connect the app to the GitHub repository and select the desired branch/tag/release.
4. Ensure the stack is **container** (the repo includes `heroku.yml`/container config via `app.json` stack settings as applicable).
5. Set config vars in **Settings → Config Vars** (see `app.json` / `.env.example`).
6. Deploy the branch and enable the `worker` dyno.

## Option B: Heroku CLI
```bash
git clone https://github.com/T3rmx/T3rmx-UserBot.git
cd T3rmx-UserBot
heroku create <app-name>
heroku stack:set container -a <app-name>
heroku config:set \
  APP_ID=... API_HASH=... STRING_SESSION=... \
  TG_BOT_TOKEN=... TG_BOT_USERNAME=... \
  ALIVE_NAME="T3rmx UserBot" TZ=Asia/Aden ENV=production \
  -a <app-name>
# optionally: heroku addons:create heroku-postgresql:mini -a <app-name>
git push heroku main  # or your branch
heroku ps:scale worker=1 -a <app-name>
```

## Environment variables
- Required: `APP_ID`, `API_HASH`, `STRING_SESSION`, `TG_BOT_TOKEN`, `TG_BOT_USERNAME`
- Common: `ALIVE_NAME`, `TZ` (default `Asia/Aden`), `ENV` (default `production`), `DATABASE_URL`
- Optional: `COMMAND_HAND_LER`, `SUDO_COMMAND_HAND_LER`, VC vars (`VCMODE`, `VC_SESSION`) as documented

## Notes
- In-app Heroku self-mutation/restart-via-API features from legacy forks are not part of the secure T3rmx runtime. Manage deploys/restarts via Heroku.
- Logs: `heroku logs --tail -a <app-name>`
