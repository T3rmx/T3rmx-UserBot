"""T3rmx-VC: independent, modular voice-chat integration layer.

This package provides a safe adapter/interface for VC/music features.
No verified external VC backend is bundled or auto-installed.
"""

from .adapter import get_vc_backend, get_vc_status

__all__ = ["get_vc_backend", "get_vc_status"]
