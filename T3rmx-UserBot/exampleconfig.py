"""Example local development config for T3rmx UserBot.

Copy/rename as needed and provide your own credentials via environment variables
or a local (git-ignored) config file. NEVER commit real secrets/session strings.
"""

from sample_config import Config


class Development(Config):
    # Get APP_ID and API_HASH from https://my.telegram.org
    APP_ID = 0
    API_HASH = ""

    # Backward-compatible variables (required for operation)
    STRING_SESSION = ""
    TG_BOT_TOKEN = ""
    TG_BOT_USERNAME = ""  # with or without @

    ALIVE_NAME = "T3rmx UserBot"
    TZ = "Asia/Aden"
    ENV = "production"

    # Optional database URL
    DB_URI = ""

    # Command handlers
    COMMAND_HAND_LER = "."
    SUDO_COMMAND_HAND_LER = "،"

    # Sudo users (comma/space separated in env: SUDO_USERS)
    SUDO_USERS = set()
