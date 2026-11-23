import os
from typing import Set

try:
    from telethon.tl.types import ChatBannedRights
except Exception:  # pragma: no cover - allows config parsing/static checks without Telethon installed
    class ChatBannedRights:  # type: ignore
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


def _get_int(name, default=0):
    try:
        value = os.environ.get(name)
        if value is None or str(value).strip() == "":
            return int(default)
        return int(str(value).strip())
    except Exception:
        return int(default)


def _get_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return bool(default)
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _get_csv_ints(*names):
    out = set()
    for name in names:
        raw = os.environ.get(name, "")
        for part in str(raw).replace(",", " ").split():
            try:
                out.add(int(part))
            except Exception:
                continue
    return out


def _normalize_bot_username(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    return s[1:] if s.startswith("@") else s


class Config(object):
    LOGGER = True

    # --- T3rmx identity (centralized, configurable) ---
    T3RMX_PROJECT_NAME = os.environ.get("T3RMX_PROJECT_NAME", "T3rmx")
    T3RMX_DISPLAY_NAME = os.environ.get("T3RMX_DISPLAY_NAME", "T3rmx UserBot")
    T3RMX_DESCRIPTION = os.environ.get(
        "T3RMX_DESCRIPTION",
        "T3rmx UserBot is an independent, modular Telegram automation framework built with Python, "
        "designed for extensibility, reliability, security, and advanced Telegram MTProto interactions.",
    )
    T3RMX_REPOSITORY = os.environ.get("T3RMX_REPOSITORY", "https://github.com/T3rmx/T3rmx-UserBot")
    T3RMX_WEBSITE = os.environ.get("T3RMX_WEBSITE", "")
    T3RMX_OWNER_USERNAME = os.environ.get("T3RMX_OWNER_USERNAME", "vvsks")
    T3RMX_OWNER_ID = _get_int("T3RMX_OWNER_ID", 6023224495)
    T3RMX_BOT_USERNAME = _normalize_bot_username(os.environ.get("T3RMX_BOT_USERNAME", "t3rmx_official_bot"))
    T3RMX_SUPPORT_CHANNEL = os.environ.get("T3RMX_SUPPORT_CHANNEL", "https://t.me/+3tqPFLpxCgVjZGVk")
    T3RMX_SUPPORT_GROUP = os.environ.get("T3RMX_SUPPORT_GROUP", "https://t.me/+ByL7rwqxpEEwOTE8")
    T3RMX_UPDATES_CHANNEL = os.environ.get("T3RMX_UPDATES_CHANNEL", "https://t.me/t3rmx_official")
    T3RMX_LOG_GROUP_ID = _get_int("T3RMX_LOG_GROUP_ID", 0)
    T3RMX_LOGO = os.environ.get("T3RMX_LOGO", os.environ.get("T3RMX_LOGO_PATH", "assets/branding/t3rmx-logo.jpg"))
    T3RMX_GITHUB_REPO = os.environ.get("T3RMX_GITHUB_REPO", "T3rmx/T3rmx-UserBot")

    # Backward-compatible core variables
    ENV = os.environ.get("ENV", "production")
    PORT = os.environ.get("PORT", None)
    TZ = os.environ.get("TZ", "UTC")

    # Telegram credentials (user-provided; never hardcode)
    # Accept APP_ID or API_ID for compatibility with common deploy env naming
    APP_ID = _get_int("APP_ID", _get_int("API_ID", 0))
    API_HASH = os.environ.get("API_HASH") or None
    STRING_SESSION = os.environ.get("STRING_SESSION", None)
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN") or os.environ.get("TG_BOT_TOKEN_BF_HER", None)
    # Accept with/without '@' and normalize internally without '@'
    TG_BOT_USERNAME = _normalize_bot_username(os.environ.get("TG_BOT_USERNAME", None))
    ALIVE_NAME = os.environ.get("ALIVE_NAME", T3RMX_DISPLAY_NAME)

    # Database / storage (empty env values treated as unset)
    DB_URI = os.environ.get("DATABASE_URL") or os.environ.get("DB_URI") or None

    # Logging/groups (configurable; no invented IDs)
    PRIVATE_GROUP_BOT_API_ID = _get_int("PRIVATE_GROUP_BOT_API_ID", T3RMX_LOG_GROUP_ID)
    PRIVATE_GROUP_ID = _get_int("PRIVATE_GROUP_ID", 0)
    PRIVATE_CHANNEL_BOT_API_ID = _get_int("PRIVATE_CHANNEL_BOT_API_ID", 0)
    PM_LOGGER_GROUP_ID = _get_int("PM_LOGGER_GROUP_ID", _get_int("PM_LOGGR_BOT_API_ID", 0))

    # Ownership / access control
    OWNER_ID = _get_int("OWNER_ID", T3RMX_OWNER_ID)
    SUDO_USERS = _get_csv_ints("SUDO_USERS", "T3RMX_ADMIN_IDS")
    COMMAND_HAND_LER = os.environ.get("COMMAND_HAND_LER", r".")
    SUDO_COMMAND_HAND_LER = os.environ.get("SUDO_COMMAND_HAND_LER", r"،")

    # T3rmx VC module (independent, configurable, optional backend)
    VCMODE = _get_bool("VCMODE", False)
    VC_SESSION = os.environ.get("VC_SESSION", None)
    T3RMX_VC_ENABLED = _get_bool("T3RMX_VC_ENABLED", VCMODE)
    T3RMX_VC_BACKEND = os.environ.get("T3RMX_VC_BACKEND", "none")  # none|external|future adapter
    T3RMX_VC_SESSION = os.environ.get("T3RMX_VC_SESSION", VC_SESSION)

    # Feature/runtime toggles (safe defaults)
    T3RMX_ENABLE_AUTO_LOG_GROUPS = _get_bool("T3RMX_ENABLE_AUTO_LOG_GROUPS", False)
    T3RMX_AUTO_LOG_CHANNEL = _get_bool("T3RMX_AUTO_LOG_CHANNEL", True)
    T3RMX_LOG_FILE = os.environ.get("T3RMX_LOG_FILE", "logs/t3rmx.log")
    T3RMX_MEME_MANIFEST_URL = os.environ.get("T3RMX_MEME_MANIFEST_URL", "")
    T3RMX_ALLOW_RUNTIME_PIP_INSTALL = _get_bool("T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False)
    T3RMX_ALLOW_EXTERNAL_REPOS = _get_bool("T3RMX_ALLOW_EXTERNAL_REPOS", False)

    # Repository/update metadata (runtime auto-update disabled; use GitHub Releases flow)
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", T3RMX_REPOSITORY)
    UPSTREAM_REPO_BRANCH = os.environ.get("UPSTREAM_REPO_BRANCH", "main")

    # --- Legacy-compatible variables (preserved) ---
    A_PIC = os.environ.get("A_PIC", None)
    ALIVE_PIC = os.environ.get("ALIVE_PIC", T3RMX_LOGO)
    SC_TEXT = os.environ.get("SCPIC_TEXT", None)
    A_TEXT = os.environ.get("A_TEXT", None)
    AUTONAME = os.environ.get("AUTONAME", None)
    MAX_FLOOD_IN_PMS = _get_int("MAX_FLOOD_IN_PMS", 7)

    PING_PIC = os.environ.get("PING_PIC")
    T7KM = os.environ.get("T7KM")
    TIME_JEP = os.environ.get("TIME_JEP", None)
    JP_FN = os.environ.get("JP_FN", None)
    ID_EM = os.environ.get("ID_EM", None)
    ID_ET = os.environ.get("ID_ET", None)
    COMM_ET = os.environ.get("COMM_ET", None)
    ALIVE_ET = os.environ.get("ALIVE_ET", None)
    UP_ET = os.environ.get("UP_ET", None)
    DOWN_ET = os.environ.get("DOWN_ET", None)
    MUKRR_ET = os.environ.get("MUKRR_ET", None)
    WEL_ET = os.environ.get("WEL_ET", None)
    DEFAULT_PIC = os.environ.get("DEFAULT_PIC", None)
    COLOR_TIME = os.environ.get("COLOR_TIME", None)
    RMVWEL_ET = os.environ.get("RMVWEL_ET", None)
    ALLWEL_ET = os.environ.get("ALLWEL_ET", None)
    SCPIC_CMD = os.environ.get("SCPIC_CMD", None)
    PRV_ET = os.environ.get("PRV_ET", None)
    DELPRV_ET = os.environ.get("DELPRV_ET", None)
    NAME_ET = os.environ.get("NAME_ET", None)
    BIO_ET = os.environ.get("BIO_ET", None)
    PHOTO_ET = os.environ.get("PHOTO_ET", None)
    LOAD_MYBOT = os.environ.get("LOAD_MYBOT", "True")
    JOKER_START = os.environ.get("JOKER_START", None)
    PMPERMIT_TEXT_Jepthon = os.environ.get("PMPERMIT_TEXT_Jepthon", None)
    UB_BLACK_LIST_CHAT = {int(x) for x in os.environ.get("UB_BLACK_LIST_CHAT", "").split() if str(x).strip().lstrip('-').isdigit()}
    TAG_LOGGER = _get_int("TAG_LOGGER", 0)
    P_PIC = os.environ.get("P_PIC", None)
    P_TEXT = os.environ.get("P_TEXT", None)
    PMBOT_START_MSSG = os.environ.get("PMBOT_START_MSSG", None)

    BOT_PIC = os.environ.get("BOT_PIC", None)

    # Optional platform integrations (legacy; use only if configured)
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)

    PLUGIN_CHANNEL = _get_int("PLUGIN_CHANNEL", 0)
    TELEGRAPH_SHORT_NAME = os.environ.get("TELEGRAPH_SHORT_NAME", "t3rmx")
    THUMB_IMAGE = os.environ.get("THUMB_IMAGE", T3RMX_LOGO)
    NO_LOAD = [x for x in os.environ.get("NO_LOAD", "").split() if x]
    DIGITAL_PIC = os.environ.get("DIGITAL_PIC", None)
    DIGITAL_PIC_COLOR = os.environ.get("DIGITAL_PIC_COLOR", None)
    DIGITAL_GROUP_PIC = os.environ.get("DIGITAL_GROUP_PIC", None)
    DIGITAL_GROUP_PIC_COLOR = os.environ.get("DIGITAL_GROUP_PIC_COLOR", None)
    DEFAULT_BIO = os.environ.get("DEFAULT_BIO", None)
    DEFAULT_NAME = os.environ.get("DEFAULT_NAME", None)
    DEFAULT_GROUP = os.environ.get("DEFAULT_GROUP", None)

    TMP_DOWNLOAD_DIRECTORY = os.environ.get("TMP_DOWNLOAD_DIRECTORY", "downloads")
    TEMP_DIR = os.environ.get("TEMP_DIR", "./temp/")
    CHANGE_TIME = _get_int("CHANGE_TIME", 60)
    ANTISPAMBOT_BAN = _get_bool("ANTISPAMBOT_BAN", False)
    DUAL_LOG = _get_bool("DUAL_LOG", False)
    FINISHED_PROGRESS_STR = os.environ.get("FINISHED_PROGRESS_STR", "▰")
    UNFINISHED_PROGRESS_STR = os.environ.get("UNFINISHED_PROGRESS_STR", "▱")

    # API keys for optional features (all user-provided; leave empty if unused)
    SCREEN_SHOT_LAYER_ACCESS_KEY = os.environ.get("SCREEN_SHOT_LAYER_ACCESS_KEY", None)
    OPEN_WEATHER_MAP_APPID = os.environ.get("OPEN_WEATHER_MAP_APPID", None)
    IBM_WATSON_CRED_URL = os.environ.get("IBM_WATSON_CRED_URL", None)
    IBM_WATSON_CRED_PASSWORD = os.environ.get("IBM_WATSON_CRED_PASSWORD", None)
    OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY", None)
    GENIUS_API_TOKEN = os.environ.get("GENIUS_API_TOKEN", None)
    REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY", None)
    CURRENCY_API = os.environ.get("CURRENCY_API", None)
    G_DRIVE_CLIENT_ID = os.environ.get("G_DRIVE_CLIENT_ID", None)
    G_DRIVE_CLIENT_SECRET = os.environ.get("G_DRIVE_CLIENT_SECRET", None)
    G_DRIVE_FOLDER_ID = os.environ.get("G_DRIVE_FOLDER_ID", None)
    G_DRIVE_DATA = os.environ.get("G_DRIVE_DATA", None)
    G_DRIVE_INDEX_LINK = os.environ.get("G_DRIVE_INDEX_LINK", None)
    TG_2STEP_VERIFICATION_CODE = os.environ.get("TG_2STEP_VERIFICATION_CODE", None)
    WATCH_COUNTRY = os.environ.get("WATCH_COUNTRY", "IN")
    BIO_PREFIX = os.environ.get("BIO_PREFIX", None)
    LASTFM_API = os.environ.get("LASTFM_API", None)
    LASTFM_SECRET = os.environ.get("LASTFM_SECRET", None)
    LASTFM_USERNAME = os.environ.get("LASTFM_USERNAME", None)
    LASTFM_PASSWORD_PLAIN = os.environ.get("LASTFM_PASSWORD", None)
    SPAMWATCH_API = os.environ.get("SPAMWATCH_API", None)
    RANDOM_STUFF_API_KEY = os.environ.get("RANDOM_STUFF_API_KEY", None)
    GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN", None)
    GIT_REPO_NAME = os.environ.get("GIT_REPO_NAME", None)
    DEEP_AI = os.environ.get("DEEP_AI", None)
    HELP_INLINETYPE = os.environ.get("HELP_INLINETYPE", None)

    MAX_MESSAGE_SIZE_LIMIT = 4095
    LOAD = []
    ANTI_FLOOD_WARN_MODE = ChatBannedRights(
        until_date=None, view_messages=None, send_messages=True
    )
    CHROME_BIN = os.environ.get("CHROME_BIN", "/usr/bin/google-chrome")
    CHROME_DRIVER = os.environ.get("CHROME_DRIVER", "/usr/bin/chromedriver")
    GROUP_REG_SED_EX_BOT_S = os.environ.get(
        "GROUP_REG_SED_EX_BOT_S", r"(regex|moku|BananaButler_|rgx|l4mR)bot"
    )
    COUNTRY = str(os.environ.get("COUNTRY", ""))
    TZ_NUMBER = _get_int("TZ_NUMBER", 1)


class Production(Config):
    LOGGER = False


class Development(Config):
    LOGGER = True
