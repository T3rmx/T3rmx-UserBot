# config values will be loaded from here

import os

# Prefer environment-based configuration when ENV is set or when no local config.py exists.
if os.environ.get("ENV") is not None or not os.path.exists("config.py"):
    try:
        from sample_config import Config  # noqa
    except Exception:
        # Fallback for local development config if present
        from config import Development as Config  # noqa
elif os.path.exists("config.py"):
    from config import Development as Config  # noqa
