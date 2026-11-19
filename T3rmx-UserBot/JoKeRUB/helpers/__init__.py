import logging

from . import fonts
from . import memeshelper as catmemes
from .aiohttp_helper import AioHttp

_LOGS = logging.getLogger(__name__)

# Utilities/helpers are imported best-effort and in granular steps so one
# optional dependency or module issue does not prevent core startup or hide
# commonly used exports (media_type, readable_time, time_formatter, reply_id, etc.).
for _mod, _names in (
    ("utils", "*"),
    ("tools", "*"),
    ("progress", "*"),
    ("memeifyhelpers", "*"),
    ("functions", "*"),
    ("chatbot", "*"),
):
    try:
        if _names == "*":
            _m = __import__(f"{__name__}.{_mod}", fromlist=["*"])
            for _k, _v in vars(_m).items():
                if not _k.startswith("__"):
                    globals().setdefault(_k, _v)
        else:
            _m = __import__(f"{__name__}.{_mod}", fromlist=_names)
            for _k in _names:
                if hasattr(_m, _k):
                    globals().setdefault(_k, getattr(_m, _k))
    except Exception as _e:
        _LOGS.debug("Optional helpers.%s import issue: %s", _mod, _e)

try:
    from .qhelper import process  # noqa: F401
except Exception:
    pass

# Common internal helper namespaces expected by legacy code/plugin manager
try:
    from .utils import _cattools, _catutils, _format  # noqa: F401
except Exception:
    pass

# Explicit fallbacks for frequently imported symbols (compatibility)
try:
    from .tools import media_type, post_to_telegraph  # noqa: F401
except Exception:
    pass

try:
    from .progress import readable_time, time_formatter, progress  # noqa: F401
    get_readable_time = readable_time
except Exception:
    pass

try:
    from .utils.events import reply_id, get_user_from_event  # noqa: F401
except Exception:
    pass

try:
    from .memeifyhelpers import thumb_from_audio  # noqa: F401
except Exception:
    pass

try:
    from .functions.functions import fileinfo  # noqa: F401
except Exception:
    pass

