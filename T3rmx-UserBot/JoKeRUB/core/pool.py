import asyncio
import os
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial, wraps
from typing import Any, Callable

from .logger import logging

_LOG = logging.getLogger(__name__)
_LOG_STR = "<<<!  ||||  %s  ||||  !>>>"


# Local thread pool executor. Avoid depending on optional external packages
# (e.g. motor) for basic background task execution.
_MAX_WORKERS = int(os.environ.get("T3RMX_THREADPOOL_WORKERS", "4") or 4)
_EXECUTOR = ThreadPoolExecutor(max_workers=max(_MAX_WORKERS, 1), thread_name_prefix="t3rmx-worker")


def submit_thread(func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Future:
    """submit thread to thread pool"""
    return _EXECUTOR.submit(func, *args, **kwargs)


def run_in_thread(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """run in a thread"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_EXECUTOR, partial(func, *args, **kwargs))

    return wrapper


def _get() -> ThreadPoolExecutor:
    return _EXECUTOR


def _stop():
    try:
        _EXECUTOR.shutdown(wait=False, cancel_futures=True)
    except TypeError:
        _EXECUTOR.shutdown(wait=False)
    # pylint: disable=protected-access
    _LOG.info(f"⏳ جار تحميل  : {_EXECUTOR._max_workers} ")


# pylint: disable=protected-access
_LOG.info(f"⌛ اكتمل التحميل  : {_EXECUTOR._max_workers} ")

