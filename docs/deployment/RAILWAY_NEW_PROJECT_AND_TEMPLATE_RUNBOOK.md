# Railway — New Project + New Template Runbook

Purpose: reusable plan for creating a **new Railway project** and a **new public template** for
T3rmx UserBot, after backing up the current production project's variables.

Prepared: 2026-11-23. Status: **plan only — not executed**.

> Note: this was written before an upcoming userbot update. Re-check the repository branch,
> commit, and health after that update before running any step below.

---

## 0. Verified starting state (2026-11-23)

| Item | Value |
|---|---|
| Railway auth | `Riyadh Radwan (rera1999.rera@gmail.com)` |
| Workspace | `Riyadh Radwan's Projects` |
| Existing project | `T3rmx-UserBot` — `8eb5383c-d557-4f99-84f2-5bf2f5780f1d` |
| Environment | `production` — `cde60f2a-12d6-40d6-afd9-9ecdb079cc47` |
| App service | `b1bf414e-08c6-483f-a12f-a26324c06655` |
| Postgres service | `c0bc91b3-3e7d-4d7b-94d6-13adb39c0792` |
| Public URL | `https://t3rmx-userbot-production.up.railway.app/` |
| Last checked deployment | `64d211db-fade-45b1-9417-0714c67580e0` — SUCCESS, `/health` 200, logs clean |
| Existing template | `t3rmx-sours-1` — id `f44507cb-9748-463a-9adf-a02469ece2a3` — **UNPUBLISHED** |
| Existing template deploy page | `https://railway.com/deploy/t3rmx-sours-1` |
| GitHub | `T3rmx/T3rmx-UserBot`, branch `main` |

Only one project exists in the workspace. The local checkout is currently linked to the
production project above.

---

## 1. Hard rules — do not violate

1. **Never print variable values.** `railway variable list --json` returns **raw values**.
   A previous `railway variables` call accidentally exposed secrets in tool output. Do not
   repeat, copy, paste, or document any value.
2. **Never put secrets in the repo, docs, commits, logs, or chat.** That includes
   `STRING_SESSION`, `API_HASH`, `TG_BOT_TOKEN`, `DATABASE_URL`, and owner IDs.
3. **Sealed variables cannot be backed up.** Railway lists sealed variables by name only
   (`null` in JSON / `<sealed>` in table). They are already set and cannot be read back —
   do not try to recreate them.
4. **Do not run two deployments on the same `STRING_SESSION`.** Telegram will kill both
   sessions with `AuthKeyDuplicated`. The old project was already taken down once this way.
   Either use a **fresh session** for the new project, or **stop the old deployment first**.
5. **A public template must be clean:** no personal session, bot token, API hash, owner ID,
   DB URL, or production data. Use variable *prompts/requirements*, not copied values.
6. **Do not delete or stop the old protected project** without explicit approval.
7. The old deployment runs code from `main`; the new project should deploy from `main` too.

---

## 2. Decisions required before executing

- [ ] **Backup destination** — where do the exported variables go?
      Suggested: `~/.railway-backups/t3rmx-old-<DATE>.json`, `chmod 600`, outside git.
      Alternative: your password manager / another secure store you control.
- [ ] **Session strategy** — fresh `STRING_SESSION` for the new project, or stop the old bot?
      Recommended: **fresh session**.
- [ ] **New project name** — required for `railway init --name <NAME>`.
- [ ] **Template visibility** — public clean template (recommended) or private?
- [ ] **Old project disposition** — keep running (recommended) or intentionally stop?

---

## 3. Execution plan

### Step 1 — Back up old-project variables (no values displayed)

```bash
# Work from the repo root; stay linked to the OLD project for this step.
cd /home/riyadh/Projects/T3rmx-UserBot
railway status   # confirm: T3rmx-UserBot / production

mkdir -p ~/.railway-backups
umask 077
railway variable list \
  --service b1bf414e-08c6-483f-a12f-a26324c06655 \
  --environment cde60f2a-12d6-40d6-afd9-9ecdb079cc47 \
  --json > ~/.railway-backups/t3rmx-old-2026-11-23.json
chmod 600 ~/.railway-backups/t3rmx-old-2026-11-23.json

# Verify WITHOUT printing values:
python3 -c "import json;d=json.load(open('$HOME/.railway-backups/t3rmx-old-2026-11-23.json'));print('keys:',len(d),'| sealed:',sum(1 for v in d.values() if v is None))"
```

Also export the Postgres service variables separately if needed (same pattern, service
`c0bc91b3-3e7d-4d7b-94d6-13adb39c0792`).

### Step 2 — Create the new project (in a SEPARATE directory)

Creating a project from the repo directory would re-link the local checkout away from
production. Use a scratch directory:

```bash
mkdir -p /tmp/t3rmx-new-railway && cd /tmp/t3rmx-new-railway
railway init --name <NEW_PROJECT_NAME>
railway status   # record new PROJECT_ID and ENVIRONMENT_ID

# Add a NEW PostgreSQL service for this deployment
railway add --service postgres
```

Deploy the app from this repo (`main`, Dockerfile, start `python3 -m JoKeRUB`, health `/health`).
Set required variables in the **new** project only:

`STRING_SESSION`, `APP_ID` (or `API_ID`), `API_HASH`, `TG_BOT_TOKEN`, `TG_BOT_USERNAME`,
`T3RMX_OWNER_ID`, `DATABASE_URL` (a reference to the new project's own Postgres URL).

Use `railway variable set KEY --stdin --skip-deploys` with values read from your secure
backup — never type a secret on a command line and never paste output here.

### Step 3 — Verify the new project

- `/health` returns 200
- deploy status SUCCESS
- no `ERROR` / `Traceback` / `AuthKeyDuplicated` in logs
- `.فحص` responds
- privileged commands reject unauthorized users
- `DATABASE_URL` points to the new project's own Postgres only

### Step 4 — Build the NEW clean template

Use a **clean** project (no secret values) as the template source:

```bash
railway templates create --project <CLEAN_PROJECT_ID> --environment <ENV> --json
```

Before publishing, inspect the generated template config for any leaked values. Then:

```bash
railway templates publish <TEMPLATE_ID> \
  --category Other \
  --description "Deploy your own Telegram UserBot with PostgreSQL" \
  --readme-file README.md \
  --json
```

The current template `t3rmx-sours-1` is **UNPUBLISHED**; publishing (or updating it) may be
needed for a genuinely public marketplace template.

### Step 5 — Template evidence checklist

- [ ] Deploy page reachable (200) and template content visible
- [ ] Manifest endpoint checked (previously returned 503)
- [ ] Two fresh, independent deployments from the new template URL
- [ ] Build/startup/healthcheck verified on both
- [ ] DB init + CRUD + persistence across restart verified on both
- [ ] Confirmed no inherited credentials/data

---

## 4. Important context

- The old outage error was:
  `The authorization key (session file) was used under two different IP addresses simultaneously... (InvokeWithLayerRequest(InitConnectionRequest(GetConfigRequest)))`
- `railway redeploy --from-source` is ineffective on the old service (no git source trigger,
  `repoTriggers: []`). Use direct upload or connect a real git source.
- `railway config migrate` warning is informational (Config as Code deprecation, deadline
  2026-12-01).
- The currently published deploy URL in docs is `https://railway.com/deploy/t3rmx-sours-1`.
- Add a domain health check with `curl -sS -o /dev/null -w "%{http_code}" <URL>/health`.

---

## 5. What is deliberately NOT in this file

No secret values, no session strings, no tokens, no DB URLs, no API hashes, no foreign
owner IDs. This runbook is safe to commit.
for the string session then the tow is ready stop the old one and the secand think use te dir you give it to my and i want do all think for make them not allow to say them for any one and the third use what you say and i want tell you i want from the user do the var for the userbot only the "STRING_SESSION         Yes     —       Your Telethon string session
APP_ID  Yes     —       Telegram API ID (API_ID alias supported)
API_HASH        Yes     —       Telegram API hash
TG_BOT_TOKEN    Yes     —       Telegram bot token from @BotFather
TG_BOT_USERNAME         Yes     —       Assistant bot username (with or without @)
T3RMX_OWNER_ID "and the another think do the defulte "ALIVE_NAME        No      T3rmx UserBot   Display name
TZ      No      UTC     Timezone
ENV     No      production      Runtime environment
COMMAND_HAND_LER        No      .       Primary command prefix
SUDO_COMMAND_HAND_LER   No      ،       Sudo command prefix
VCMODE  No      false   VC integration intent (backend-dependent)
VC_SESSION      No      empty " or use the internal like the db url and the all think for this filde "DATABASE_URL fe KR KK
PGDATA kK RRS
PGDATABASE AR RH
PGHOST kK RRS
PGPASSWORD AR RH
PGPORT kK RRS
PGUSER kK RRS
POSTGRES_DB kK RR KH
POSTGRES_PASSWORD ARK RRS
POSTGRES_USER HK R HH
RAILWAY_DEPLOYMENT_DRAINING_SECON.. *******
SSL_CERT_DAYS fe KR KK " use the refrance ")( ${{DATABASE_URL}}

{} ${{PGDATA}}

{} ${{PGDATABASE}}

{} ${{PGHOST}}

{} ${{PGPASSWORD}}

{} ${{PGPORT}}

{} ${{PGUSER}}

{} ${{POSTGRES_DB}}

{} ${{POSTGRES_PASSWORD}}
{} ${{POSTGRES_USER}} " and chek if its right and the olde template the app it's up but don't run you hace the mcp use it for make shure if all think is right and make the template from the github
