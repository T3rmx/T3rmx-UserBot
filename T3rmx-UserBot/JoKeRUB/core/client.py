import datetime
import inspect
import re
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Union

from telethon import TelegramClient, events
from telethon.errors import MessageIdInvalidError, MessageNotModifiedError

from ..Config import Config
from ..helpers.utils.events import checking
from ..helpers.utils.format import paste_message
from ..helpers.utils.utils import runcmd
from ..sql_helper.globals import gvarstatus
from . import BOT_INFO, CMD_INFO, GRP_INFO, LOADED_CMDS, PLG_INFO
from .auth import is_developer, is_owner
from .cmdinfo import _format_about
from .data import _sudousers_list, blacklist_chats_list, sudo_enabled_cmds
from .events import *
from .fasttelethon import download_file, upload_file
from .logger import logging
from .managers import edit_delete
from .pluginManager import get_message_link, restart_script

LOGS = logging.getLogger(__name__)


async def _report_command_error(check, error, disable_errors: bool = False) -> None:
    """Log one short line and send a short Arabic alert.

    Full tracebacks are intentionally not written to the console/log file:
    they made the log channel unreadable and hid the actual failure.
    """
    if disable_errors:
        return
    name = error.__class__.__name__
    message = str(error)[:180]
    LOGS.warning("Command error %s: %s", name, message)
    try:
        from ..utils.logchannel import send_log_alert

        await send_log_alert(
            check.client,
            "⚠️ تنبيه خطأ في T3rmx\n"
            f"• نوع الخطأ: `{name}`\n"
            f"• الرسالة: `{message}`\n",
        )
    except Exception:
        pass


class REGEX:
    def __init__(self):
        self.regex = ""
        self.regex1 = ""
        self.regex2 = ""


REGEX_ = REGEX()
sudo_enabledcmds = sudo_enabled_cmds()


class HuReClient(TelegramClient):
    def ar_cmd(
        self: TelegramClient,
        pattern: str or tuple = None,
        info: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]]
        or tuple = None,
        groups_only: bool = False,
        private_only: bool = False,
        allow_sudo: bool = True,
        edited: bool = True,
        forword=False,
        disable_errors: bool = False,
        command: str or tuple = None,
        **kwargs,
    ) -> callable:  # sourcery no-metrics
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forword)
        if gvarstatus("blacklist_chats") is not None:
            kwargs["blacklist_chats"] = True
            kwargs["chats"] = blacklist_chats_list()
        stack = inspect.stack()
        previous_stack_frame = stack[1]
        file_test = Path(previous_stack_frame.filename)
        file_test = file_test.stem.replace(".py", "")
        if command is not None:
            command = list(command)
            if not command[1] in BOT_INFO:
                BOT_INFO.append(command[1])
            try:
                if file_test not in GRP_INFO[command[1]]:
                    GRP_INFO[command[1]].append(file_test)
            except BaseException:
                GRP_INFO.update({command[1]: [file_test]})
            try:
                if command[0] not in PLG_INFO[file_test]:
                    PLG_INFO[file_test].append(command[0])
            except BaseException:
                PLG_INFO.update({file_test: [command[0]]})
            if not command[0] in CMD_INFO:
                CMD_INFO[command[0]] = [_format_about(info)]
        if pattern is not None:
            if (
                pattern.startswith(r"\#")
                or not pattern.startswith(r"\#")
                and pattern.startswith(r"^")
            ):
                REGEX_.regex1 = REGEX_.regex2 = re.compile(pattern)
            else:
                reg1 = "\\" + Config.COMMAND_HAND_LER
                reg2 = "\\" + Config.SUDO_COMMAND_HAND_LER
                REGEX_.regex1 = re.compile(reg1 + pattern)
                REGEX_.regex2 = re.compile(reg2 + pattern)

        def decorator(func):  # sourcery no-metrics
            async def wrapper(check):
                try:
                    if gvarstatus("blockedfrom") == "yes" and not is_developer(getattr(check, "sender_id", None)):
                        await edit_delete(check, "**This T3rmx UserBot instance is currently restricted by the owner.**")
                        return
                except Exception:
                    pass
                if groups_only and not check.is_group:
                    try:
                        await edit_delete(check, "`This command can only be used in groups.`", 10)
                    except Exception:
                        pass
                    return
                if private_only and not check.is_private:
                    try:
                        await edit_delete(
                            check, "`This command can only be used in private chats.`", 10
                        )
                    except Exception:
                        pass
                    return
                try:
                    await func(check)
                except events.StopPropagation:
                    raise events.StopPropagation
                except KeyboardInterrupt:
                    pass
                except MessageNotModifiedError:
                    LOGS.error("Message was same as previous message")
                except MessageIdInvalidError:
                    LOGS.error("Message was deleted or cant be found")
                except Exception as e:
                    # FloodWait is transient; never turn it into a traceback.
                    if e.__class__.__name__ == "FloodWaitError":
                        LOGS.warning("Command rate-limited (FloodWait).")
                        return
                    await _report_command_error(check, e, disable_errors)
                except BaseException as e:
                    await _report_command_error(check, e, disable_errors)

            from .session import l313l

            if not func.__doc__ is None and command is not None and command[0] in CMD_INFO:
                CMD_INFO[command[0]].append((func.__doc__).strip())
            if pattern is not None:
                if command is not None:
                    if command[0] in LOADED_CMDS and wrapper in LOADED_CMDS[command[0]]:
                        return None
                    try:
                        LOADED_CMDS[command[0]].append(wrapper)
                    except BaseException:
                        LOADED_CMDS.update({command[0]: [wrapper]})
                if edited:
                    l313l.add_event_handler(
                        wrapper,
                        MessageEdited(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                    )
                l313l.add_event_handler(
                    wrapper,
                    NewMessage(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                )
                if allow_sudo and gvarstatus("sudoenable") is not None:
                    if command is None or command[0] in sudo_enabledcmds:
                        if edited:
                            l313l.add_event_handler(
                                wrapper,
                                MessageEdited(
                                    pattern=REGEX_.regex2,
                                    from_users=_sudousers_list(),
                                    **kwargs,
                                ),
                            )
                        l313l.add_event_handler(
                            wrapper,
                            NewMessage(
                                pattern=REGEX_.regex2,
                                from_users=_sudousers_list(),
                                **kwargs,
                            ),
                        )
            else:
                if file_test in LOADED_CMDS and func in LOADED_CMDS[file_test]:
                    return None
                try:
                    LOADED_CMDS[file_test].append(func)
                except BaseException:
                    LOADED_CMDS.update({file_test: [func]})
                if edited:
                    l313l.add_event_handler(func, events.MessageEdited(**kwargs))
                l313l.add_event_handler(func, events.NewMessage(**kwargs))
            return wrapper

        return decorator

    def bot_cmd(
        self: TelegramClient,
        disable_errors: bool = False,
        edited: bool = False,
        **kwargs,
    ) -> callable:  # sourcery no-metrics
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)

        def decorator(func):
            async def wrapper(check):
                try:
                    await func(check)
                except events.StopPropagation:
                    raise events.StopPropagation
                except KeyboardInterrupt:
                    pass
                except MessageNotModifiedError:
                    LOGS.error("Message was same as previous message")
                except MessageIdInvalidError:
                    LOGS.error("Message was deleted or cant be found")
                except BaseException as e:
                    await _report_command_error(check, e, disable_errors)

            from .session import l313l

            if edited is True:
                l313l.tgbot.add_event_handler(func, events.MessageEdited(**kwargs))
            else:
                l313l.tgbot.add_event_handler(func, events.NewMessage(**kwargs))

            return wrapper

        return decorator

    async def get_traceback(self, exc: Exception) -> str:
        return "".join(
            traceback.format_exception(etype=type(exc), value=exc, tb=exc.__traceback__)
        )

    def _kill_running_processes(self) -> None:
        """Kill all the running asyncio subprocessess"""
        for _, process in getattr(self, "running_processes", {}).items():
            try:
                process.kill()
                LOGS.debug("Killed %d which was still running.", process.pid)
            except Exception as e:
                LOGS.debug(e)
        if hasattr(self, "running_processes"):
            self.running_processes.clear()


HuReClient.fast_download_file = download_file
HuReClient.fast_upload_file = upload_file
HuReClient.reload = restart_script
HuReClient.get_msg_link = get_message_link
HuReClient.check_testcases = checking
