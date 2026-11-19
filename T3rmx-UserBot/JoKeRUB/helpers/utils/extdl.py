from ...Config import Config
from ...core.logger import logging

LOGS = logging.getLogger("t3rmx.utils")


def install_pip(pipfile):
    """Runtime pip install is disabled by default for security/reproducibility.

    This function remains for backward compatibility with legacy plugins.
    Enable only explicitly via T3RMX_ALLOW_RUNTIME_PIP_INSTALL.
    """
    if not getattr(Config, "T3RMX_ALLOW_RUNTIME_PIP_INSTALL", False):
        LOGS.warning(
            f"Blocked runtime pip install request for '{pipfile}'. "
            "Install dependencies via the pinned project manifests."
        )
        return b""
    try:
        from subprocess import PIPE, Popen
        LOGS.info(f"Installing {pipfile} (explicitly allowed)")
        pip_cmd = ["pip", "install", f"{pipfile}"]
        process = Popen(pip_cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        return stdout
    except Exception as e:
        LOGS.error(f"Runtime pip install failed for {pipfile}: {e}")
        return b""
