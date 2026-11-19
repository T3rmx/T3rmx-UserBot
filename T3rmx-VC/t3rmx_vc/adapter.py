"""VC backend adapter for T3rmx UserBot.

Preserves existing VC-related configuration hooks while avoiding unsafe
runtime fetching of unverified external sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class VCStatus:
    enabled: bool
    backend: str
    configured: bool
    available: bool
    message: str
    details: Dict[str, Any]


class BaseVCBackend:
    name = "none"

    def status(self) -> VCStatus:
        return VCStatus(
            enabled=False,
            backend=self.name,
            configured=False,
            available=False,
            message="VC backend is not configured.",
            details={},
        )

    async def start(self, *args, **kwargs):
        raise RuntimeError(self.status().message)

    async def stop(self, *args, **kwargs):
        raise RuntimeError(self.status().message)


class UnavailableVCBackend(BaseVCBackend):
    name = "unavailable"

    def __init__(self, backend_name: str = "none", enabled: bool = False):
        self._backend_name = backend_name or "none"
        self._enabled = bool(enabled)

    def status(self) -> VCStatus:
        if not self._enabled or self._backend_name in {"none", "", "disabled"}:
            return VCStatus(
                enabled=False,
                backend=self._backend_name or "none",
                configured=False,
                available=False,
                message=(
                    "T3rmx-VC is disabled or not configured. "
                    "Set VC-related variables and provide a verified backend to enable call-control features."
                ),
                details={"adapter": "t3rmx-vc"},
            )
        return VCStatus(
            enabled=True,
            backend=self._backend_name,
            configured=True,
            available=False,
            message=(
                "T3rmx-VC adapter is present, but no verified VC backend is installed/configured for this environment. "
                "Music/download helpers may work where available; call-control/playback requires a verified backend integration."
            ),
            details={"adapter": "t3rmx-vc", "backend": self._backend_name},
        )


def _get_config():
    try:
        from JoKeRUB.Config import Config

        return Config
    except Exception:
        return None


def get_vc_backend(config: Optional[Any] = None):
    cfg = config or _get_config()
    enabled = False
    backend_name = "none"
    try:
        if cfg is not None:
            enabled = bool(getattr(cfg, "T3RMX_VC_ENABLED", False) or getattr(cfg, "VCMODE", False))
            backend_name = str(getattr(cfg, "T3RMX_VC_BACKEND", "none") or "none")
    except Exception:
        pass
    # Future: resolve verified in-repo/external-approved backends here.
    return UnavailableVCBackend(backend_name=backend_name, enabled=enabled)


def get_vc_status(config: Optional[Any] = None) -> VCStatus:
    return get_vc_backend(config).status()
