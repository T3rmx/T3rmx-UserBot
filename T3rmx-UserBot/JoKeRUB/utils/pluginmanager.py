import importlib
import sys
from pathlib import Path

from JoKeRUB import CMD_HELP, LOAD_PLUG

from ..Config import Config
from ..core import LOADED_CMDS, PLG_INFO
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..core.session import l313l, tgbot
from ..helpers.tools import media_type
from ..helpers.utils import _cattools, _catutils, _format, reply_id
from .decorators import admin_cmd, sudo_cmd

LOGS = logging.getLogger("t3rmx.pluginmanager")


def load_module(shortname, plugin_path=None):
    if shortname.startswith("__"):
        return
    elif shortname.endswith("_"):
        path = Path(f"JoKeRUB/plugins/{shortname}.py")
        checkplugins(path)
        name = "JoKeRUB.plugins.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        LOGS.info("Loaded plugin module: " + shortname)
    else:
        if plugin_path is None:
            path = Path(f"JoKeRUB/plugins/{shortname}.py")
            name = f"JoKeRUB.plugins.{shortname}"
        else:
            path = Path((f"{plugin_path}/{shortname}.py"))
            name = f"{plugin_path}/{shortname}".replace("/", ".")
        checkplugins(path)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        mod.bot = l313l
        mod.LOGS = LOGS
        mod.Config = Config
        mod._format = _format
        # Use the safe no-op client when the assistant bot is unavailable so
        # button/inline handlers never crash plugin imports.
        mod.tgbot = getattr(l313l, "tgbot", None) or tgbot
        mod.sudo_cmd = sudo_cmd
        mod.CMD_HELP = CMD_HELP
        mod.reply_id = reply_id
        mod.admin_cmd = admin_cmd
        mod._catutils = _catutils
        mod._cattools = _cattools
        mod.media_type = media_type
        mod.edit_delete = edit_delete
        # install_pip is intentionally disabled by default in helpers; keep attribute if present for compatibility
        try:
            from ..helpers.utils import install_pip
            mod.install_pip = install_pip
        except Exception:
            pass
        mod.parse_pre = _format.parse_pre
        mod.edit_or_reply = edit_or_reply
        mod.logger = logging.getLogger(shortname)
        mod.borg = l313l
        spec.loader.exec_module(mod)
        # for imports
        sys.modules["JoKeRUB.plugins." + shortname] = mod
        LOGS.info("Loaded plugin module: " + shortname)


def remove_plugin(shortname):
    try:
        cmd = []
        if shortname in PLG_INFO:
            cmd += PLG_INFO[shortname]
        else:
            cmd = [shortname]
        for cmdname in cmd:
            if cmdname in LOADED_CMDS:
                for i in LOADED_CMDS[cmdname]:
                    l313l.remove_event_handler(i)
                del LOADED_CMDS[cmdname]
        return True
    except Exception as e:
        LOGS.error(e)
    try:
        for i in LOAD_PLUG[shortname]:
            l313l.remove_event_handler(i)
        del LOAD_PLUG[shortname]
    except BaseException:
        pass
    try:
        name = f"JoKeRUB.plugins.{shortname}"
        for i in reversed(range(len(l313l._event_builders))):
            ev, cb = l313l._event_builders[i]
            if cb.__module__ == name:
                del l313l._event_builders[i]
    except BaseException:
        raise ValueError


def checkplugins(filename):
    try:
        with open(filename, "r") as f:
            filedata = f.read()
        filedata = filedata.replace("sendmessage", "send_message")
        filedata = filedata.replace("sendfile", "send_file")
        filedata = filedata.replace("editmessage", "edit_message")
        with open(filename, "w") as f:
            f.write(filedata)
    except Exception:
        # Best-effort compatibility normalization; do not fail plugin loading.
        return
