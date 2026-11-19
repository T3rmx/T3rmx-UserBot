from .extdl import *
from .paste import *

import logging
import types

_LOGS = logging.getLogger(__name__)

try:
    from . import format as _format
except Exception:
    _format = types.SimpleNamespace(
        parse_pre=lambda text, *a, **k: (text, []),
        md_to_text=lambda t: str(t or ""),
        paste_message=None,
    )

try:
    from . import tools as _cattools
except Exception:
    _cattools = types.SimpleNamespace()

try:
    from . import utils as _catutils
except Exception:
    _catutils = types.SimpleNamespace()

try:
    from .events import *
except Exception:
    pass

try:
    from .format import *
except Exception:
    pass

try:
    from .tools import *  # noqa: F401,F403
except Exception as _e:
    _LOGS.debug("helpers.utils.tools import issue: %s", _e)

try:
    from .utils import *  # noqa: F401,F403
except Exception as _e:
    _LOGS.debug("helpers.utils.utils import issue: %s", _e)

# Ensure common exports exist even if submodules had optional dependency issues
try:
    from .events import reply_id, get_user_from_event  # noqa: F401
except Exception:
    pass

