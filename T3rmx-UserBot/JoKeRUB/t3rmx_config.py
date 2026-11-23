"""
T3rmx centralized configuration helpers.

Preserves backward compatibility with legacy environment variable names while
adding T3rmx identity defaults and safe normalization/validation.
"""

from __future__ import annotations

import os
from typing import Iterable, Optional, Set


def get_env(name: str, default=None):
    val = os.environ.get(name)
    if val is None:
        return default
    # keep empty string behavior explicit for some vars; callers can decide
    return val


def get_str(name: str, default: str = "") -> str:
    val = os.environ.get(name)
    if val is None:
        return str(default)
    s = str(val)
    return s if s != "" else str(default)


def get_int(name: str, default: int = 0) -> int:
    val = os.environ.get(name)
    if val is None or str(val).strip() == "":
        return int(default)
    try:
        return int(str(val).strip())
    except Exception:
        return int(default)


def get_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return bool(default)
    return str(val).strip().lower() in {"1", "true", "yes", "on", "enable", "enabled"}


def get_int_set(name: str, default: Optional[Iterable[int]] = None) -> Set[int]:
    raw = os.environ.get(name)
    if raw is None or str(raw).strip() == "":
        return set(default or [])
    out: Set[int] = set()
    for part in str(raw).replace(",", " ").split():
        try:
            out.add(int(part))
        except Exception:
            continue
    return out


def normalize_bot_username(value: Optional[str]) -> Optional[str]:
    """Accept with/without '@' and normalize internally without '@'."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    if s.startswith("@"):
        s = s[1:]
    return s or None


# --- T3rmx identity / ownership (configurable, safe defaults) ---
T3RMX_PROJECT_NAME = get_str("T3RMX_PROJECT_NAME", "T3rmx")
T3RMX_DISPLAY_NAME = get_str("T3RMX_DISPLAY_NAME", "T3rmx UserBot")
T3RMX_REPOSITORY = get_str("T3RMX_REPOSITORY", "https://github.com/T3rmx/T3rmx-UserBot")
T3RMX_WEBSITE = get_str("T3RMX_WEBSITE", "")  # Not available
T3RMX_OWNER_USERNAME = get_str("T3RMX_OWNER_USERNAME", "vvsks")
T3RMX_OWNER_ID = get_int("T3RMX_OWNER_ID", 6023224495)
T3RMX_BOT_USERNAME = normalize_bot_username(get_str("T3RMX_BOT_USERNAME", "t3rmx_official_bot"))
T3RMX_SUPPORT_CHANNEL = get_str("T3RMX_SUPPORT_CHANNEL", "https://t.me/T3rmx_Support_channel")
T3RMX_SUPPORT_GROUP = get_str("T3RMX_SUPPORT_GROUP", "https://t.me/T3rmx_Support_group")
T3RMX_OFFICIAL_PHOTO_URL = get_str(
    "T3RMX_OFFICIAL_PHOTO_URL",
    "https://t.me/i/userpic/320/T3rmx_Support_channel.jpg",
)
T3RMX_UPDATES_CHANNEL = get_str("T3RMX_UPDATES_CHANNEL", "https://t.me/t3rmx_official")
T3RMX_LOG_GROUP_ID = get_int("T3RMX_LOG_GROUP_ID", 0)  # Not configured by default
T3RMX_LOGO_PATH = get_str("T3RMX_LOGO_PATH", "assets/branding/t3rmx-logo.jpg")

T3RMX_DESCRIPTION = (
    "T3rmx UserBot is an independent, modular Telegram automation framework built with Python, "
    "designed for extensibility, reliability, security, and advanced Telegram MTProto interactions."
)

# Update system
T3RMX_GITHUB_REPO = get_str("T3RMX_GITHUB_REPO", "T3rmx/T3rmx-UserBot")
T3RMX_RELEASES_API = f"https://api.github.com/repos/{T3RMX_GITHUB_REPO}/releases"


def is_owner(user_id) -> bool:
    try:
        return int(user_id) == int(T3RMX_OWNER_ID)
    except Exception:
        return False


def owner_ids() -> Set[int]:
    return {int(T3RMX_OWNER_ID)}
