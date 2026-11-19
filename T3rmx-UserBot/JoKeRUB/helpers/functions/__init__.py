import importlib
import logging

_LOGS = logging.getLogger(__name__)

# Import helper modules best-effort so optional/missing dependencies in one
# module do not prevent the userbot from starting.
for _mod in (
    "findquote",
    "functions",
    "ialivetext",
    "imgtools",
    "jikan",
    "nekos",
    "utils",
    "utube",
    "vidtools",
):
    try:
        _module = importlib.import_module(f".{_mod}", __name__)
        globals().update(
            {k: v for k, v in vars(_module).items() if not k.startswith("__")}
        )
    except Exception as _e:
        _LOGS.warning("Optional helper module '%s' not loaded: %s", _mod, _e)
