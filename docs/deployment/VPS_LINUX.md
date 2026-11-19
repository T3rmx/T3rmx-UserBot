# Deploy on VPS / Linux

## Recommended: systemd service

### 1. Install system dependencies
Debian/Ubuntu example:
```bash
sudo apt-get update
sudo apt-get install -y git ffmpeg python3 python3-venv python3-pip ca-certificates build-essential
```

### 2. Get the code
```bash
sudo git clone https://github.com/T3rmx/T3rmx-UserBot.git /opt/t3rmx-userbot
cd /opt/t3rmx-userbot
```

### 3. Create virtual environment and install pinned dependencies
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment
Create `/opt/t3rmx-userbot/.env` (or use an EnvironmentFile referenced by systemd) based on `.env.example` and set required values:
- `APP_ID`, `API_HASH`, `STRING_SESSION`, `TG_BOT_TOKEN`, `TG_BOT_USERNAME`
- `TZ=Asia/Aden`, `ENV=production`, `ALIVE_NAME`

Keep this file private (`chmod 600`).

### 5. Install and start systemd service
Copy and adjust the service unit:
```bash
sudo cp T3rmx-Deploy/vps/t3rmx-userbot.service /etc/systemd/system/t3rmx-userbot.service
# edit WorkingDirectory/User/Group/EnvironmentFile paths as needed
sudo systemctl daemon-reload
sudo systemctl enable --now t3rmx-userbot
sudo systemctl status t3rmx-userbot
sudo journalctl -u t3rmx-userbot -f
```

The provided unit runs `python3 -m JoKeRUB` from the repository directory and restarts on failure (no cron/keepalive required).

## Direct Linux execution
For manual runs (development or simple setups):
```bash
git clone https://github.com/T3rmx/T3rmx-UserBot.git
cd T3rmx-UserBot
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit values
# export variables (example): set -a; source .env; set +a
python3 -m JoKeRUB
```

## Updates
Use the in-bot `تحديث` command to check GitHub Releases safely (read-only). Apply updates manually by deploying a reviewed release/tag/source and restarting the service/container. Automatic in-place self-mutation is intentionally disabled.
