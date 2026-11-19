#!/usr/bin/env bash
set -euo pipefail

# T3rmx UserBot - VPS install helper (Debian/Ubuntu-style)
# Review before running. Installs system packages, creates venv, installs pinned deps.

APP_DIR="${APP_DIR:-/opt/t3rmx-userbot}"
REPO_URL="${REPO_URL:-https://github.com/T3rmx/T3rmx-UserBot.git}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "Please run as root (or via sudo)." >&2
  exit 1
fi

apt-get update
apt-get install -y --no-install-recommends \
  git curl ca-certificates ffmpeg ${PYTHON_BIN} ${PYTHON_BIN}-venv ${PYTHON_BIN}-pip \
  build-essential libffi-dev libssl-dev

mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  echo "Repo already present at $APP_DIR (not auto-updating)."
fi

cd "$APP_DIR"
${PYTHON_BIN} -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p downloads temp
echo "Install complete. Configure environment variables (.env or systemd EnvironmentFile), then set up the systemd service from T3rmx-Deploy/vps/t3rmx-userbot.service."
