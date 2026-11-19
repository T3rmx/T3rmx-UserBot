import asyncio

from telethon.errors import FloodWaitError, MessageNotModifiedError
from telethon.events import CallbackQuery

from ..Config import Config
from ..sql_helper.globals import gvarstatus
from .auth import is_sudo


def check_owner(func):
    async def wrapper(c_q: CallbackQuery):
        if c_q.query.user_id and is_sudo(c_q.query.user_id):
            try:
                await func(c_q)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds + 5)
            except MessageNotModifiedError:
                pass
        else:
            HELP_TEXT = (
                gvarstatus("HELP_TEXT")
                or "هذا الخيار غير متاح لك. الرجاء استخدام نسخة T3rmx UserBot الخاصة بك."
            )
            await c_q.answer(
                HELP_TEXT,
                alert=True,
            )

    return wrapper
