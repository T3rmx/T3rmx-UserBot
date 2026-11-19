# Development

## Repository layout
- `T3rmx-UserBot/` – application runtime (`JoKeRUB/` core package, plugins, assistant, helpers, SQL helpers, resources)
- `T3rmx-VC/` – independent voice-chat adapter/interface module
- `T3rmx-Deploy/` – deployment assets (Heroku/Railway/Docker/VPS)
- `docs/` – audit, architecture, deployment, development, dependencies, security
- `tests/` – automated checks
- Root files provide compatibility entrypoints and platform configs (`app.json`, `railway.json`, `Dockerfile`, `docker-compose.yml`, `Procfile`, `sample_config.py`)

## Local setup
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill required values
python3 -m JoKeRUB
```

## Configuration
- Environment-based config is supported via `sample_config.py` (default when `ENV` is set or `config.py` absent).
- Preserve legacy env var names for compatibility. Defaults: `TZ=Asia/Aden`, `ENV=production`.
- `TG_BOT_USERNAME` is normalized internally (leading `@` removed).
- Owner/developer privileges default to `@vvsks` / `6023224495` (centralized in `JoKeRUB/core/auth.py`).

## Safety model
- No runtime `pip install`, no automatic external repository cloning/fetching, and no in-app git/heroku self-mutation by default.
- Update checks use GitHub Releases metadata (read-only) for `T3rmx/T3rmx-UserBot`.
- Sensitive controls (sec/update actions) are owner-restricted.

## Testing
Run project tests (when available):
```bash
python -m pytest -q
```
Static checks:
```bash
python -m compileall T3rmx-UserBot sample_config.py
```

## T3rmx-VC
Voice chat call-control requires a verified backend integrated via `T3rmx-VC/t3rmx_vc/adapter.py`. The adapter reports unavailable/not-configured status when no backend is present; it does not fetch external code at runtime.
