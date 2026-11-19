import importlib
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import sys
import traceback
import types
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / 'T3rmx-UserBot'
PLUGINS = PKG / 'JoKeRUB' / 'plugins'
OUT = ROOT / 'docs/reports' / 'plugin_harness_results.json'
FAIL_OUT = ROOT / 'docs/reports' / 'plugin_failure_classification.json'

for p in [str(ROOT), str(PKG)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Safe defaults for import-time environment (no real credentials)
os.environ.setdefault('DB_URI', 'sqlite:///:memory:')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('APP_ID', '1')
os.environ.setdefault('API_HASH', 'dummy_api_hash')
os.environ.setdefault('ENV', 'production')
os.environ.setdefault('TZ', 'Asia/Aden')

def ensure_pkg(name, path=None):
    m = sys.modules.get(name)
    if m is None:
        m = types.ModuleType(name)
        sys.modules[name] = m
    if path is not None:
        p = str(path)
        if not hasattr(m, '__path__'):
            m.__path__ = []
        if p not in m.__path__:
            m.__path__.append(p)
        spec = importlib.machinery.ModuleSpec(name, loader=None, is_package=True)
        spec.submodule_search_locations = list(m.__path__)
        m.__spec__ = spec
    return m

class DummyLogger:
    def __getattr__(self, n):
        return lambda *a, **k: None

def make_logging_module():
    m = types.ModuleType('JoKeRUB.core.logger')
    logging_ns = types.SimpleNamespace(
        getLogger=lambda *a, **k: DummyLogger(),
        INFO=20, WARNING=30, ERROR=40, DEBUG=10,
        basicConfig=lambda *a, **k: None,
    )
    m.logging = logging_ns
    return m

class PatternMatch:
    def __init__(self, text=''):
        self.text = text
        self._g = (text,)
    def group(self, n=0):
        try:
            return self._g[n]
        except Exception:
            return None

class DummyMessage:
    def __init__(self):
        self.id = 1
        self.text = ''
        self.message = ''
        self.raw_text = ''
        self.reply_to_msg_id = None
        self.media = None
        self.entities = []
        self.photo = None
        self.document = None
        self.video = None
        self.audio = None
        self.voice = None
        self.sticker = None
        self.gif = None
        self.video_note = None
        self.chat_id = 123
        self.sender_id = 6023224495
    async def get_reply_message(self):
        return None
    async def reply(self, *a, **k):
        return None
    async def edit(self, *a, **k):
        return None
    async def delete(self, *a, **k):
        return None

class DummyEvent:
    def __init__(self):
        self.pattern_match = PatternMatch()
        self.chat_id = 123
        self.sender_id = 6023224495
        self.client = None
        self.message = DummyMessage()
        self.reply_to = None
        self.is_private = False
        self.is_group = True
        self.is_channel = False
        self.is_reply = False
        self.mentioned = False
        self.text = ''
        self.raw_text = ''
        self.data = b''
        self.query = types.SimpleNamespace(user_id=6023224495)
        self.actions = []
    async def edit(self, *a, **k): self.actions.append(('edit', a[:1])); return None
    async def reply(self, *a, **k): self.actions.append(('reply', a[:1])); return None
    async def respond(self, *a, **k): self.actions.append(('respond', a[:1])); return None
    async def delete(self, *a, **k): self.actions.append(('delete', None)); return None
    async def answer(self, *a, **k): self.actions.append(('answer', a[:1])); return None
    async def get_reply_message(self): return None
    async def get_sender(self): return types.SimpleNamespace(id=6023224495, bot=False, first_name='T3rmx', last_name='', username='vvsks')
    async def get_chat(self): return types.SimpleNamespace(id=123, title='T3rmx Test', username=None, megagroup=True)
    async def get_input_chat(self): return 123

class DummyClient:
    uid = 6023224495
    def __init__(self):
        self._ar_handlers = []
        self._bot_handlers = []
        self._on_handlers = []
        self.tgbot = self
        self.me = types.SimpleNamespace(id=6023224495, bot=False, username='t3rmx_official_bot', first_name='T3rmx')
        self.session = types.SimpleNamespace(save=lambda: 'dummy')
        # import-time compatibility: some plugins schedule startup tasks on l313l.loop
        self.loop = types.SimpleNamespace(
            create_task=lambda coro, *a, **k: (coro.close() if hasattr(coro, 'close') else None),
            run_until_complete=lambda coro, *a, **k: (coro.close() if hasattr(coro, 'close') else None),
            call_later=lambda delay, cb, *a, **k: None,
            is_running=lambda: False,
        )
    def ar_cmd(self, pattern=None, **kwargs):
        def dec(func):
            self._ar_handlers.append((pattern, func, kwargs))
            return func
        return dec
    def bot_cmd(self, pattern=None, **kwargs):
        def dec(func):
            self._bot_handlers.append((pattern, func, kwargs))
            return func
        return dec
    def on(self, *args, **kwargs):
        def dec(func):
            self._on_handlers.append((args, kwargs, func))
            return func
        return dec
    def add_event_handler(self, *a, **k): return None
    def remove_event_handler(self, *a, **k): return None
    async def send_message(self, *a, **k): return DummyEvent()
    async def send_file(self, *a, **k): return DummyEvent()
    async def edit_message(self, *a, **k): return DummyEvent()
    async def get_entity(self, *a, **k): return types.SimpleNamespace(id=123, username='x', bot=False)
    async def get_messages(self, *a, **k): return []
    async def get_participants(self, *a, **k): return []
    async def get_me(self): return self.me
    async def download_media(self, *a, **k): return ''
    async def upload_file(self, *a, **k): return None
    async def __call__(self, *a, **k): return None
    async def disconnect(self): return None
    async def start(self, *a, **k): return self
    async def iter_dialogs(self, *a, **k):
        if False:
            yield None
        return
    async def get_permissions(self, *a, **k): return types.SimpleNamespace(participant=None)

def _is_internal_module(modname: str) -> bool:
    if not modname:
        return False
    top = modname.split('.')[0]
    if top in ('JoKeRUB', 'l313l', 'ALJoker', 'HuRe', 'Config', 't3rmx_vc', 'sample_config'):
        return True
    rel = modname.replace('.', '/')
    return (PKG / (rel + '.py')).exists() or (PKG / rel / '__init__.py').exists() or (ROOT / (rel + '.py')).exists()

def classify_failure(tb_text, err_text, error_type):
    tb = tb_text or ''
    err = err_text or ''
    m = re.search(r"No module named '([^']+)'", tb + '\n' + err)
    if m:
        mod = m.group(1)
        top = mod.split('.')[0]
        if _is_internal_module(mod) or _is_internal_module(top):
            return 'harness_or_internal_interface', mod, None
        return 'missing_optional_dependency', mod, top
    m = re.search(r"cannot import name '([^']+)' from '([^']+)'", tb + '\n' + err)
    if m:
        name, frm = m.group(1), m.group(2)
        if _is_internal_module(frm):
            return 'load_error_interface_or_export', m.group(0), frm
        return 'missing_optional_dependency', f"{frm}.{name}", frm.split('.')[0]
    m = re.search(r"type object 'Config' has no attribute '([^']+)'", tb + '\n' + err)
    if m:
        return 'load_error_config_attribute', f"Config.{m.group(1)}", None
    m = re.search(r"name '([^']+)' is not defined", tb + '\n' + err)
    if m:
        return 'source_exec_defect_or_undefined_name', m.group(1), None
    if error_type == 'AttributeError':
        m = re.search(r"'DummyClient' object has no attribute '([^']+)'", tb + '\n' + err)
        if m:
            return 'harness_or_internal_interface', f'DummyClient.{m.group(1)}', None
    if error_type in ('SyntaxError', 'IndentationError', 'TabError'):
        return 'source_syntax_defect', None, None
    return 'load_error', None, None

def read_text_safe(p):
    try:
        return p.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''

def detect_source_defined_name(plugin_path, name):
    src = read_text_safe(plugin_path)
    if not name:
        return False
    defined = re.search(rf'^\s*(def|class)\s+{re.escape(name)}\b', src, re.M)
    assigned = re.search(rf'^\s*{re.escape(name)}\s*=', src, re.M)
    imported = re.search(rf'^\s*(from\s+.+\s+import\s+.*\b{re.escape(name)}\b|import\s+.*\b{re.escape(name)}\b)', src, re.M)
    return bool(defined or assigned or imported)

def get_config_attrs_used(plugin_path):
    src = read_text_safe(plugin_path)
    return sorted(set(re.findall(r'\bConfig\.([A-Za-z_][A-Za-z0-9_]*)', src)))

def get_required_config(plugin_path):
    # Conservative: attrs referenced as Config.X in module-level-ish code patterns or anywhere
    src = read_text_safe(plugin_path)
    attrs = sorted(set(re.findall(r'\bConfig\.([A-Za-z_][A-Za-z0-9_]*)', src)))
    return attrs

async def _async_none(*a, **k): return None
async def _async_true(*a, **k): return True
async def _async_false(*a, **k): return False
async def _async_empty_str(*a, **k): return ''
async def _async_list(*a, **k): return []

def _dummy_decorator(*a, **k):
    if len(a) == 1 and callable(a[0]) and not k:
        return a[0]
    def dec(f):
        return f
    return dec

class SQLStubModule(types.ModuleType):
    def __getattr__(self, n):
        if n.startswith('__') and n.endswith('__'):
            raise AttributeError(n)
        # common names
        if n in ('BASE', 'SESSION', 'engine'):
            return None
        if n.startswith('is_') or n.startswith('check_') or n.startswith('already_'):
            return lambda *a, **k: False
        if n.startswith('get_') and (n.endswith('s') or n.endswith('list') or n.endswith('all')):
            return lambda *a, **k: []
        return lambda *a, **k: None

def sql_stub(name):
    m = SQLStubModule(name)
    sys.modules[name] = m
    return m

def load_real_config_class():
    try:
        # Try sample_config first (env-based, safe defaults in this environment)
        from sample_config import Config as RealConfig
        return RealConfig
    except Exception:
        pass
    try:
        from JoKeRUB.Config.roza_config import Config as RealConfig
        return RealConfig
    except Exception:
        pass
    # fallback minimal
    class RealConfig:
        pass
    return RealConfig

def enrich_config(cls):
    defaults = {
        'APP_ID': 1, 'API_HASH': 'dummy', 'STRING_SESSION': '', 'TG_BOT_TOKEN': '', 'TG_BOT_USERNAME': 't3rmx_official_bot',
        'TZ': 'Asia/Aden', 'ENV': 'production', 'ALIVE_NAME': 'T3rmx UserBot', 'COMMAND_HAND_LER': '.',
        'SUDO_COMMAND_HAND_LER': '،', 'T3RMX_OWNER_ID': 6023224495, 'T3RMX_OWNER_USERNAME': 'vvsks',
        'OWNER_ID': 6023224495, 'T3RMX_DISPLAY_NAME': 'T3rmx UserBot', 'T3RMX_REPOSITORY': 'https://github.com/T3rmx/T3rmx-UserBot',
        'T3RMX_UPDATES_CHANNEL': 'https://t.me/t3rmx_official', 'T3RMX_SUPPORT_GROUP': '', 'T3RMX_SUPPORT_CHANNEL': '',
        'T3RMX_LOGO': 'assets/branding/t3rmx-logo.jpg', 'T3RMX_GITHUB_REPO': 'T3rmx/T3rmx-UserBot', 'T3RMX_VERSION': '1.0.0',
        'BOTLOG': False, 'BOTLOG_CHATID': 0, 'PRIVATE_GROUP_BOT_API_ID': 0, 'PM_LOGGER_GROUP_ID': -100,
        'HEROKU_APP': None, 'SUDO_USERS': set(), 'NO_LOAD': [], 'TMP_DOWNLOAD_DIRECTORY': 'temp', 'TEMP_DIR': 'temp',
        'UPSTREAM_REPO': 'https://github.com/T3rmx/T3rmx-UserBot', 'PLUGIN_CHANNEL': 0, 'VC_SESSION': None,
        'VCMODE': False, 'T3RMX_VC_ENABLED': False, 'T3RMX_VC_BACKEND': 'none',
        'TELEGRAPH_SHORT_NAME': 't3rmx', 'THUMB_IMAGE': 'assets/branding/t3rmx-logo.jpg',
        'DEFAULT_BIO': None, 'DEFAULT_NAME': None, 'DEFAULT_GROUP': None, 'AUTONAME': None,
        # legacy/plugin-specific attrs commonly accessed
        'T7KM': '', 'PRV_ET': 'رحب', 'DELPRV_ET': 'حذف رحب', 'UP_ET': 'ارفع', 'DOWN_ET': 'نزل',
        'MUKRR_ET': 'مكرر', 'COMM_ET': 'كومنت', 'ALIVE_ET': None, 'WEL_ET': None, 'RMVWEL_ET': None,
        'ALLWEL_ET': None, 'SCPIC_CMD': None, 'NAME_ET': None, 'BIO_ET': None, 'PHOTO_ET': None,
        'JP_FN': None, 'TIME_JEP': None, 'ID_EM': None, 'ID_ET': None, 'COLOR_TIME': None,
        'DEFAULT_PIC': None, 'DIGITAL_PIC': None, 'DIGITAL_PIC_COLOR': None, 'DIGITAL_GROUP_PIC': None,
        'DIGITAL_GROUP_PIC_COLOR': None, 'CHANGE_TIME': 60, 'PMBOT_START_MSSG': None, 'JOKER_START': None,
        'PMPERMIT_TEXT_Jepthon': None, 'P_PIC': None, 'P_TEXT': None, 'BOT_PIC': None,
        'A_PIC': None, 'A_TEXT': None, 'ALIVE_PIC': 'assets/branding/t3rmx-logo.jpg', 'PING_PIC': None,
        'SPAMWATCH_API': None, 'G_DRIVE_CLIENT_ID': None, 'G_DRIVE_CLIENT_SECRET': None, 'G_DRIVE_DATA': None,
        'G_DRIVE_FOLDER_ID': None, 'G_DRIVE_INDEX_LINK': None, 'OCR_SPACE_API_KEY': None, 'REM_BG_API_KEY': None,
        'OPEN_WEATHER_MAP_APPID': None, 'IBM_WATSON_CRED_URL': None, 'IBM_WATSON_CRED_PASSWORD': None,
        'SCREENSHOT_LAYER_ACCESS_KEY': None, 'SCREEN_SHOT_LAYER_ACCESS_KEY': None, 'TAG_LOGGER': 0,
        'MAX_FLOOD_IN_PMS': 7, 'HEROKU_API_KEY': None, 'HEROKU_APP_NAME': None,
        'T3RMX_ALLOW_RUNTIME_PIP_INSTALL': False, 'T3RMX_ALLOW_EXTERNAL_REPOS': False,
        'T3RMX_ENABLE_AUTO_LOG_GROUPS': False,
    }
    for k, v in defaults.items():
        try:
            if not hasattr(cls, k):
                setattr(cls, k, v)
        except Exception:
            pass
    # ensure getattr fallback for unknown attrs doesn't crash import-time access if code expects None-like? no.
    return cls

def setup_base_packages(client):
    # base package skeletons
    ensure_pkg('JoKeRUB', PKG / 'JoKeRUB')
    for name, path in [
        ('JoKeRUB.core', PKG / 'JoKeRUB' / 'core'),
        ('JoKeRUB.helpers', PKG / 'JoKeRUB' / 'helpers'),
        ('JoKeRUB.helpers.functions', PKG / 'JoKeRUB' / 'helpers' / 'functions'),
        ('JoKeRUB.helpers.utils', PKG / 'JoKeRUB' / 'helpers' / 'utils'),
        ('JoKeRUB.utils', PKG / 'JoKeRUB' / 'utils'),
        ('JoKeRUB.sql_helper', PKG / 'JoKeRUB' / 'sql_helper'),
        ('JoKeRUB.assistant', PKG / 'JoKeRUB' / 'assistant'),
        ('JoKeRUB.Config', PKG / 'JoKeRUB' / 'Config'),
        ('l313l', ROOT / 'l313l'),
        ('l313l.razan', ROOT / 'l313l' / 'razan'),
        ('l313l.razan.resources', ROOT / 'l313l' / 'razan' / 'resources'),
        ('t3rmx_vc', PKG / 't3rmx_vc'),
    ]:
        ensure_pkg(name, path if path.exists() else None)

    # logger
    sys.modules['JoKeRUB.core.logger'] = make_logging_module()

    # Config
    RealConfig = enrich_config(load_real_config_class())
    cfg_mod = types.ModuleType('JoKeRUB.Config')
    cfg_mod.Config = RealConfig
    sys.modules['JoKeRUB.Config'] = cfg_mod
    cfg_pkg = ensure_pkg('JoKeRUB.Config', PKG / 'JoKeRUB' / 'Config')
    setattr(cfg_pkg, 'Config', RealConfig)

    # core managers (safe async no-ops)
    managers = types.ModuleType('JoKeRUB.core.managers')
    async def edit_or_reply(event, text=None, *a, **k):
        try:
            return await event.edit(text) if hasattr(event, 'edit') else await event.reply(text)
        except Exception:
            return None
    async def edit_delete(event, text=None, time=None, *a, **k):
        try:
            return await event.edit(text) if hasattr(event, 'edit') else await event.reply(text)
        except Exception:
            return None
    managers.edit_or_reply = edit_or_reply
    managers.edit_delete = edit_delete
    sys.modules['JoKeRUB.core.managers'] = managers

    # core session stub
    session_mod = types.ModuleType('JoKeRUB.core.session')
    session_mod.l313l = client
    session_mod.tgbot = client
    session_mod.bot = client
    session_mod.__version__ = getattr(RealConfig, 'T3RMX_VERSION', '1.0.0')
    sys.modules['JoKeRUB.core.session'] = session_mod

    # core data/cmdinfo/events stubs (safe)
    data_mod = types.ModuleType('JoKeRUB.core.data')
    data_mod._sudousers_list = lambda: []
    data_mod._dev_list = lambda: []
    data_mod.blacklist_chats_list = lambda: []
    data_mod.sudo_enabled_cmds = lambda: []
    sys.modules['JoKeRUB.core.data'] = data_mod

    core_pkg = ensure_pkg('JoKeRUB.core', PKG / 'JoKeRUB' / 'core')
    core_pkg.CMD_INFO = {}
    core_pkg.PLG_INFO = {}
    core_pkg.GRP_INFO = {}
    core_pkg.CMD_HELP = {}
    core_pkg.BOT_INFO = []
    core_pkg.LOADED_CMDS = {}
    def _check_owner_stub(func=None):
        if func is None:
            return lambda f: f
        async def wrapper(*a, **k):
            return await func(*a, **k)
        return wrapper
    core_pkg.check_owner = _check_owner_stub
    try:
        import asyncio
        import functools

        def _run_in_thread(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
            wrapper.__wrapped__ = func
            return wrapper

        core_pkg.pool = types.SimpleNamespace(run_in_thread=_run_in_thread)
    except Exception:
        core_pkg.pool = types.SimpleNamespace(run_in_thread=lambda f: f)
    cmdinfo_mod = types.ModuleType('JoKeRUB.core.cmdinfo')
    sys.modules['JoKeRUB.core.cmdinfo'] = cmdinfo_mod
    events_mod = types.ModuleType('JoKeRUB.core.events')
    sys.modules['JoKeRUB.core.events'] = events_mod
    inlinebot_mod = types.ModuleType('JoKeRUB.core.inlinebot')
    sys.modules['JoKeRUB.core.inlinebot'] = inlinebot_mod
    fasttelethon_mod = types.ModuleType('JoKeRUB.core.fasttelethon')
    sys.modules['JoKeRUB.core.fasttelethon'] = fasttelethon_mod

    # try to use real core.auth/decorators when safe; fallback stubs
    try:
        # provide auth module backed by real implementation if importable
        import JoKeRUB.core.auth as real_auth  # noqa: F401
    except Exception:
        auth_mod = types.ModuleType('JoKeRUB.core.auth')
        auth_mod.is_owner = lambda uid=None, *a, **k: uid == 6023224495
        auth_mod.is_sudo = lambda uid=None, *a, **k: uid == 6023224495
        auth_mod.is_developer = lambda uid=None, *a, **k: uid == 6023224495
        auth_mod.authorized_for_sec = lambda uid=None, *a, **k: uid == 6023224495
        auth_mod.authorized_for_update = lambda uid=None, *a, **k: uid == 6023224495
        auth_mod.AUTHORIZED_OWNER_ID = 6023224495
        sys.modules['JoKeRUB.core.auth'] = auth_mod
    # core.decorators - provide check_owner stub if real import problematic
    def _co_dec(func=None):
        if func is None:
            return lambda f: f
        async def wrapper(*a, **k): return await func(*a, **k)
        return wrapper
    if 'JoKeRUB.core.decorators' not in sys.modules:
        try:
            import JoKeRUB.core.decorators as _dec  # noqa
            core_pkg.check_owner = getattr(_dec, 'check_owner', _co_dec)
        except Exception:
            dec_mod = types.ModuleType('JoKeRUB.core.decorators')
            dec_mod.check_owner = _co_dec
            sys.modules['JoKeRUB.core.decorators'] = dec_mod
            core_pkg.check_owner = _co_dec
    else:
        core_pkg.check_owner = getattr(sys.modules['JoKeRUB.core.decorators'], 'check_owner', _co_dec)

    # helpers/utils compatibility
    hu = ensure_pkg('JoKeRUB.helpers.utils', PKG / 'JoKeRUB' / 'helpers' / 'utils')
    hu_events = types.ModuleType('JoKeRUB.helpers.utils.events')
    async def reply_id(event):
        try:
            return getattr(getattr(event, 'reply_to_msg_id', None), 'reply_to_msg_id', None) or getattr(event, 'reply_to_msg_id', None) or getattr(getattr(event,'message',None),'reply_to_msg_id',None)
        except Exception:
            return None
    async def get_user_from_event(event, *a, **k):
        return None, None
    hu_events.reply_id = reply_id
    hu_events.get_user_from_event = get_user_from_event
    sys.modules['JoKeRUB.helpers.utils.events'] = hu_events
    hu_format = types.ModuleType('JoKeRUB.helpers.utils.format')
    hu_format.parse_pre = lambda t: t
    hu_format.yaml_format = lambda obj: str(obj)
    hu_format.reformattext = lambda t: t
    hu_format.mentionuser = lambda name, userid: f"[{name}](tg://user?id={userid})"
    hu_format.htmlmentionuser = lambda name, userid: f"<a href='tg://user?id={userid}'>{name}</a>"
    sys.modules['JoKeRUB.helpers.utils.format'] = hu_format
    hu_tools = types.ModuleType('JoKeRUB.helpers.utils.tools')
    hu_tools.media_type = lambda message: None
    hu_tools.media_to_pic = _async_none
    sys.modules['JoKeRUB.helpers.utils.tools'] = hu_tools
    hu_utils = types.ModuleType('JoKeRUB.helpers.utils.utils')
    hu_utils._format = types.SimpleNamespace(reformattext=lambda t: t)
    hu_utils.runcmd = _async_none
    hu_utils.run_sync = lambda func, *a, **k: func(*a, **k)
    hu_utils.run_async = lambda loop, coro: None
    sys.modules['JoKeRUB.helpers.utils.utils'] = hu_utils
    hu_paste = types.ModuleType('JoKeRUB.helpers.utils.paste')
    hu_paste.pastetext = _async_none
    sys.modules['JoKeRUB.helpers.utils.paste'] = hu_paste
    hu_ext = types.ModuleType('JoKeRUB.helpers.utils.extdl')
    hu_ext.install_pip = lambda *a, **k: b''
    sys.modules['JoKeRUB.helpers.utils.extdl'] = hu_ext
    hu.reply_id = reply_id
    hu.get_user_from_event = get_user_from_event
    hu.parse_pre = hu_format.parse_pre
    hu.yaml_format = hu_format.yaml_format
    hu.mentionuser = hu_format.mentionuser
    hu.htmlmentionuser = hu_format.htmlmentionuser
    hu._format = types.SimpleNamespace(reformattext=hu_format.reformattext, mentionuser=hu_format.mentionuser, htmlmentionuser=hu_format.htmlmentionuser)
    hu._catutils = types.SimpleNamespace(runcmd=_async_none, run_sync=hu_utils.run_sync)
    hu._cattools = types.SimpleNamespace(media_type=hu_tools.media_type)
    hu.install_pip = hu_ext.install_pip

    helpers_pkg = ensure_pkg('JoKeRUB.helpers', PKG / 'JoKeRUB' / 'helpers')
    helpers_pkg.get_user_from_event = get_user_from_event
    helpers_pkg.reply_id = reply_id
    helpers_pkg.media_type = hu_tools.media_type
    helpers_pkg.progress = _async_none
    helpers_pkg.thumb_from_audio = _async_none
    helpers_pkg.edit_or_reply = managers.edit_or_reply
    helpers_pkg.edit_delete = managers.edit_delete
    helpers_pkg.get_readable_time = lambda s=0: '0s'
    helpers_pkg.readable_time = lambda s=0: '0s'
    helpers_pkg.sanga_seperator = lambda *a, **k: ''
    helpers_pkg.admin_groups = _async_list
    helpers_pkg.mentionuser = hu_format.mentionuser
    helpers_pkg.htmlmentionuser = hu_format.htmlmentionuser
    helpers_pkg.parse_pre = hu_format.parse_pre
    helpers_pkg.yaml_format = hu_format.yaml_format
    helpers_pkg._format = hu._format
    helpers_pkg._catutils = hu._catutils
    helpers_pkg._cattools = hu._cattools

    hf_pkg = ensure_pkg('JoKeRUB.helpers.functions', PKG / 'JoKeRUB' / 'helpers' / 'functions')
    async def _get_readable_time(seconds=0):
        try:
            s = int(seconds)
        except Exception:
            s = 0
        return f"{s}s"
    async def _animator_stub(*a, **k):
        # stub for import-time compatibility
        return None
    async def _crop_and_divide_stub(*a, **k):
        return []
    _hf_exports = {
        'translate': _async_empty_str,
        'catalive': _async_empty_str,
        'check_data_base_heal_th': _async_empty_str,
        'get_readable_time': _get_readable_time,
        'convert_toimage': lambda *a, **k: None,
        'convert_tosticker': lambda *a, **k: None,
        'vid_to_gif': lambda *a, **k: None,
        'deEmojify': lambda s='': s,
        'soft_deEmojify': lambda s='': s,
        'hide_inlinebot': _async_none,
        'waifutxt': _async_none,
        'media_type': hu_tools.media_type,
        'animator': _animator_stub,
        'crop_and_divide': _crop_and_divide_stub,
        'unsavegif': _async_none,
    }
    for name, val in _hf_exports.items():
        setattr(hf_pkg, name, val)
    def _hf_getattr(name):
        if name in _hf_exports:
            return _hf_exports[name]
        if name.startswith('__'):
            raise AttributeError(name)
        # generic safe fallback for helper function imports
        return _async_none
    try:
        hf_pkg.__getattr__ = _hf_getattr  # PEP 562 module-level getattr
    except Exception:
        pass

    # sql_helper: try real package import first for structure? it can touch DB/Config; safer to stub heavily
    sql_pkg = ensure_pkg('JoKeRUB.sql_helper', PKG / 'JoKeRUB' / 'sql_helper')
    for attr in ('SESSION', 'BASE', 'engine'):
        setattr(sql_pkg, attr, None)
    # create stubs for common helper modules
    common_sql = [
        'globals', 'global_collection', 'global_list', 'global_collectionjson', 'no_log_pms_sql', 'pmpermit_sql',
        'echo_sql', 'welcome_sql', 'warns_sql', 'antiflood_sql', 'autopost_sql', 'gban_sql_helper', 'bot_pms_sql',
        'bot_blacklists', 'bot_starters', 'botusers_sql', 'broadcast_sql', 'chatbot_sql', 'filter_sql', 'fsub_sql',
        'gdrive_sql', 'gmute_sql', 'google_drive_sql', 'idadder_sql', 'locks_sql', 'mute_sql', 'snip_sql',
        'sqlrules_sql', 'blacklist_sql', 'blacklist_assistant_sql', 'welcomesql', 'group', 'bank', 'nsfw_watch_sql',
        'notes_sql', 'pmpermit_sql', 'gmute_sql', 'antiflood_sql', 'welcome_sql'
    ]
    for sub in sorted(set(common_sql)):
        if f'JoKeRUB.sql_helper.{sub}' not in sys.modules:
            sql_stub(f'JoKeRUB.sql_helper.{sub}')
    # specific APIs
    gl = sys.modules['JoKeRUB.sql_helper.globals']
    gl.gvarstatus = lambda k, default=None: default
    gl.addgvar = lambda k, v: None
    gl.delgvar = lambda k: None
    pm = sys.modules['JoKeRUB.sql_helper.pmpermit_sql']
    pm.is_approved = lambda *a, **k: False
    pm.approve = lambda *a, **k: None
    pm.disapprove = lambda *a, **k: None
    pm.get_all_approved = lambda *a, **k: []
    wel = sys.modules['JoKeRUB.sql_helper.welcomesql']
    wel.getcurrent_welcome_settings = lambda *a, **k: None
    wel.get_current_welcome_settings = lambda *a, **k: None
    wel.addwelcome_setting = lambda *a, **k: None
    wel.rmwelcome_setting = lambda *a, **k: None
    wel.updateprevious_welcome = lambda *a, **k: None
    locks = sys.modules['JoKeRUB.sql_helper.locks_sql']
    locks.is_locked = lambda *a, **k: False
    locks.update_lock = lambda *a, **k: None
    locks.get_locks = lambda *a, **k: None

    # utils package
    utils_pkg = ensure_pkg('JoKeRUB.utils', PKG / 'JoKeRUB' / 'utils')
    # try to expose common names
    utils_pkg.admin_cmd = _dummy_decorator
    utils_pkg.sudo_cmd = _dummy_decorator
    utils_pkg.register = _dummy_decorator
    utils_pkg.command = _dummy_decorator
    utils_pkg.errors_handler = _dummy_decorator
    utils_pkg.is_admin = _async_false
    utils_pkg.load_module = lambda *a, **k: None
    utils_pkg.remove_plugin = lambda *a, **k: None
    # also provide submodules where plugins import directly
    if 'JoKeRUB.utils.decorators' not in sys.modules:
        try:
            import JoKeRUB.utils.decorators as _ud  # noqa
        except Exception:
            ud = types.ModuleType('JoKeRUB.utils.decorators')
            ud.admin_cmd = _dummy_decorator
            ud.sudo_cmd = _dummy_decorator
            ud.register = _dummy_decorator
            ud.command = _dummy_decorator
            ud.errors_handler = _dummy_decorator
            sys.modules['JoKeRUB.utils.decorators'] = ud
    if 'JoKeRUB.utils.checks' not in sys.modules:
        try:
            import JoKeRUB.utils.checks as _uc  # noqa
        except Exception:
            uc = types.ModuleType('JoKeRUB.utils.checks')
            uc.is_admin = _async_false
            sys.modules['JoKeRUB.utils.checks'] = uc

    # plugins package (rich compat exports; do not execute real __init__ side effects here)
    plugins_pkg = ensure_pkg('JoKeRUB.plugins', PKG / 'JoKeRUB' / 'plugins')
    exports = {
        'Config': RealConfig,
        'l313l': client,
        'bot': client,
        'tgbot': client,
        'BOTLOG': False,
        'BOTLOG_CHATID': getattr(RealConfig, 'BOTLOG_CHATID', 0),
        'PM_LOGGER_GROUP_ID': getattr(RealConfig, 'PM_LOGGER_GROUP_ID', -100),
        'LOGS': DummyLogger(),
        'logging': sys.modules.get('JoKeRUB.core.logger', types.SimpleNamespace()).logging if hasattr(sys.modules.get('JoKeRUB.core.logger', None), 'logging') else types.SimpleNamespace(getLogger=lambda *a, **k: DummyLogger()),
        'CMD_HELP': {}, 'CMD_LIST': {}, 'SUDO_LIST': {}, 'CMD_INFO': {}, 'PLG_INFO': {},
        'ALIVE_NAME': getattr(RealConfig, 'ALIVE_NAME', 'T3rmx UserBot'),
        'AUTONAME': getattr(RealConfig, 'AUTONAME', None),
        'DEFAULT_BIO': getattr(RealConfig, 'DEFAULT_BIO', None),
        'DEFAULT_GROUP': getattr(RealConfig, 'DEFAULT_GROUP', None),
        'OWNER_ID': getattr(RealConfig, 'OWNER_ID', 6023224495),
        'SUDO_USERS': set(),
        'HEROKU_APP': None,
        'HEROKU_API_KEY': getattr(RealConfig, 'HEROKU_API_KEY', None),
        'HEROKU_APP_NAME': getattr(RealConfig, 'HEROKU_APP_NAME', None),
        'mention': 'T3rmx',
        'hmention': 'T3rmx',
        'spamwatch': None,
        'admin_cmd': _dummy_decorator,
        'sudo_cmd': _dummy_decorator,
        'edit_or_reply': managers.edit_or_reply,
        'edit_delete': managers.edit_delete,
        'reply_id': reply_id,
        'get_user_from_event': get_user_from_event,
        'media_type': hu_tools.media_type,
        'progress': _async_none,
        'thumb_from_audio': _async_none,
        'parse_pre': hu_format.parse_pre,
        'yaml_format': hu_format.yaml_format,
        'extract_time': lambda cat, time_val=None: (None, None),
        'admin_groups': _async_list,
        'humanbytes': lambda s=0: str(s),
        'time_formatter': lambda ms=0: str(ms),
        'readable_time': lambda s=0: '0s',
        'get_readable_time': lambda s=0: '0s',
        'convert_toimage': lambda *a, **k: None,
        'convert_tosticker': lambda *a, **k: None,
        'deEmojify': lambda s='': s,
        'phcomment': _async_none,
        'threats': _async_none,
        'trap': _async_none,
        'trash': _async_none,
        'changemymind': _async_none,
        'fakegs': _async_none,
        'kannagen': _async_none,
        'moditweet': _async_none,
        'trumptweet': _async_none,
        'tweets': _async_none,
        'covidindia': _async_none,
        'fonts': types.SimpleNamespace(),
        '_cattools': hu._cattools,
        '_catutils': hu._catutils,
        '_format': hu._format,
        'group_call': None,
        'translate': _async_empty_str,
    }
    for k, v in exports.items():
        try:
            setattr(plugins_pkg, k, v)
        except Exception:
            pass

    # JoKeRUB root package attrs
    jp = ensure_pkg('JoKeRUB', PKG / 'JoKeRUB')
    jp.Config = RealConfig
    jp.l313l = client
    jp.bot = client
    jp.tgbot = client
    jp.BOTLOG = False
    jp.BOTLOG_CHATID = getattr(RealConfig, 'BOTLOG_CHATID', 0)
    jp.HEROKU_APP = None
    jp.CMD_HELP = {}
    jp.CMD_LIST = {}
    jp.SUDO_LIST = {}
    jp.CMD_INFO = {}
    jp.PLG_INFO = {}
    jp.StartTime = 0
    jp.__version__ = getattr(RealConfig, 'T3RMX_VERSION', '1.0.0')
    jp.JEPVERSION = jp.__version__
    jp.T3RMX_VERSION = jp.__version__
    jp.T3RMX_REPOSITORY = getattr(RealConfig, 'T3RMX_REPOSITORY', 'https://github.com/T3rmx/T3rmx-UserBot')
    jp.T3RMX_DISPLAY_NAME = getattr(RealConfig, 'T3RMX_DISPLAY_NAME', 'T3rmx UserBot')

    # l313l helper namespace minimal
    l313l_pkg = ensure_pkg('l313l', ROOT / 'l313l')
    razan_pkg = ensure_pkg('l313l.razan', ROOT / 'l313l' / 'razan')
    res_pkg = ensure_pkg('l313l.razan.resources', ROOT / 'l313l' / 'razan' / 'resources')
    # avoid importing heavy/optional razan resources; provide empty modules if missing
    for name in ['Gif', 'strings', 'utils', 'mybot', 'assistant']:
        modname = f'l313l.razan.resources.{name}'
        if modname not in sys.modules:
            m = types.ModuleType(modname)
            sys.modules[modname] = m

    return RealConfig

def snapshot_modules():
    return set(sys.modules.keys())

def restore_extra_modules(before):
    # remove plugin-specific loaded modules to reduce cross-contamination, but keep heavy base stubs
    for k in list(sys.modules.keys()):
        if k in before:
            continue
        # keep dynamically loaded plugin modules cleanup; allow imported deps cache? remove harness plugin modules
        if k.startswith('JoKeRUB.plugins._harness_'):
            sys.modules.pop(k, None)

def analyze_plugin_entry(plugin_path, result, RealConfig):
    src = read_text_safe(plugin_path)
    cfg_used = get_required_config(plugin_path)
    cfg_missing = []
    for a in cfg_used:
        if not hasattr(RealConfig, a):
            cfg_missing.append(a)

    rec = {
        'file': plugin_path.name,
        'path': str(plugin_path.relative_to(ROOT)),
        'absolute_path': str(plugin_path),
        'exec_ok': result['exec_ok'],
        'classification': result['classification'],
        'error_type': result['error_type'],
        'error': result['error'],
        'traceback_tail': result['traceback_tail'],
        'missing_module_or_attribute': result.get('missing_module'),
        'handlers': {
            'ar_cmd': result.get('handlers_ar_cmd', 0),
            'bot_cmd': result.get('handlers_bot_cmd', 0),
            'on': result.get('handlers_on', 0),
        },
        'patterns_sample': result.get('patterns', [])[:10],
        'config_attributes_referenced': cfg_used,
        'config_attributes_missing_from_config': sorted(set(cfg_missing)),
        'required_external_services': [],
        'can_operate_without_optional_dependencies': 'n/a',
        'stub_incompatibility_suspected': result['classification'] in ('harness_or_internal_interface', 'load_error_interface_or_export'),
        'package_export_compat_issue_suspected': result['classification'] == 'load_error_interface_or_export' or ('cannot import name' in (result.get('error') or '') and 'JoKeRUB' in (result.get('error') or '')),
        'actual_source_defect_suspected': False,
        'recommended_action': '',
        'notes': [],
    }

    # detect external service hints
    hints = []
    if re.search(r'api\.telegram\.org|heroku|github|openai|google|ocr|remove\.bg|spotify|youtube', src, re.I):
        hints.append('possible external API/service usage')
    if re.search(r'postgres|psycopg|DATABASE_URL|DB_URI', src):
        hints.append('database-dependent behavior possible')
    rec['required_external_services'] = hints

    # optional dependency operability
    if rec['classification'] == 'missing_optional_dependency':
        mm = (rec['missing_module_or_attribute'] or '').split('.')[0]
        rec['can_operate_without_optional_dependencies'] = 'no_for_affected_feature_or_import' if mm else 'unknown'
    else:
        rec['can_operate_without_optional_dependencies'] = 'n/a'

    # source defect refinement
    if result['classification'] == 'source_exec_defect_or_undefined_name':
        name = rec['missing_module_or_attribute']
        if name and not detect_source_defined_name(plugin_path, name):
            rec['actual_source_defect_suspected'] = True
            rec['notes'].append(f"Name '{name}' appears undefined/unimported in source.")
        else:
            rec['notes'].append(f"NameError for '{name}' may be runtime-state dependent; inspect manually.")
    if result['classification'] == 'source_syntax_defect':
        rec['actual_source_defect_suspected'] = True
    if rec['config_attributes_missing_from_config']:
        rec['notes'].append('Config attribute(s) missing from resolved Config may break import-time access; add compatible defaults if intentional legacy vars.')

    # recommendation
    if rec['exec_ok']:
        rec['recommended_action'] = 'none (loaded in harness)'
    elif rec['classification'] == 'missing_optional_dependency':
        rec['recommended_action'] = 'map/install vetted optional dependency and/or preserve graceful degradation'
    elif rec['stub_incompatibility_suspected']:
        rec['recommended_action'] = 'improve harness compatibility interfaces; avoid production-only changes'
    elif rec['actual_source_defect_suspected']:
        rec['recommended_action'] = 'fix actual source defect with minimal safe change'
    elif rec['classification'] == 'load_error_config_attribute':
        rec['recommended_action'] = 'provide compatible Config attribute/default or defer access if safe'
    else:
        rec['recommended_action'] = 'inspect traceback and determine source defect vs interface/config issue'

    return rec

def try_load(plugin_path, RealConfig):
    # fresh client and base setup per plugin for isolation
    client = DummyClient()
    setup_base_packages(client)
    name = f"JoKeRUB.plugins._harness_{plugin_path.stem}_{abs(hash(str(plugin_path))) & 0xffff}"
    # ensure plugins package points to client
    sys.modules['JoKeRUB'].l313l = client
    sys.modules['JoKeRUB'].bot = client
    sys.modules['JoKeRUB.plugins'].l313l = client
    sys.modules['JoKeRUB.plugins'].bot = client
    sys.modules['JoKeRUB.plugins'].tgbot = client
    sys.modules['JoKeRUB.core.session'].l313l = client

    spec = importlib.util.spec_from_file_location(name, str(plugin_path))
    if spec is None or spec.loader is None:
        return {
            'file': plugin_path.name,
            'name': plugin_path.stem,
            'exec_ok': False,
            'handlers_ar_cmd': 0, 'handlers_bot_cmd': 0, 'handlers_on': 0,
            'patterns': [],
            'error_type': 'SpecError',
            'error': 'Could not create module spec',
            'traceback_tail': None,
            'missing_module': None,
            'classification': 'load_error',
            'stdout_tail': None, 'stderr_tail': None,
        }
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = 'JoKeRUB.plugins'
    mod.__name__ = name
    mod.__file__ = str(plugin_path)
    # legacy globals
    mod.borg = client
    mod.l313l = client
    mod.bot = client
    mod.tgbot = client
    mod.client = client
    mod.Config = RealConfig
    mod.CMD_HELP = {}
    mod.CMD_LIST = {}
    mod.admin_cmd = _dummy_decorator
    mod.sudo_cmd = _dummy_decorator
    mod.register = _dummy_decorator
    mod.command = _dummy_decorator
    sys.modules[name] = mod

    stdout = io.StringIO(); stderr = io.StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            spec.loader.exec_module(mod)
        return {
            'file': plugin_path.name,
            'name': plugin_path.stem,
            'exec_ok': True,
            'handlers_ar_cmd': len(client._ar_handlers),
            'handlers_bot_cmd': len(client._bot_handlers),
            'handlers_on': len(client._on_handlers),
            'patterns': [
                {'pattern': p, 'command': (k.get('command') if isinstance(k, dict) else None)}
                for p, f, k in client._ar_handlers[:15]
            ],
            'error_type': None,
            'error': None,
            'traceback_tail': None,
            'missing_module': None,
            'classification': 'load_ok',
            'stdout_tail': stdout.getvalue()[-800:] or None,
            'stderr_tail': stderr.getvalue()[-800:] or None,
        }
    except Exception as e:
        tb = traceback.format_exc()
        cls, missing, extra = classify_failure(tb, str(e), type(e).__name__)
        # refine interface issues
        if missing and _is_internal_module(missing):
            cls = 'harness_or_internal_interface'
        if cls == 'load_error_interface_or_export' and extra and _is_internal_module(extra):
            pass
        return {
            'file': plugin_path.name,
            'name': plugin_path.stem,
            'exec_ok': False,
            'handlers_ar_cmd': len(client._ar_handlers),
            'handlers_bot_cmd': len(client._bot_handlers),
            'handlers_on': len(client._on_handlers),
            'patterns': [
                {'pattern': p, 'command': (k.get('command') if isinstance(k, dict) else None)}
                for p, f, k in client._ar_handlers[:15]
            ],
            'error_type': type(e).__name__,
            'error': str(e),
            'traceback_tail': tb[-5000:],
            'missing_module': missing,
            'classification': cls,
            'stdout_tail': stdout.getvalue()[-800:] or None,
            'stderr_tail': stderr.getvalue()[-800:] or None,
        }

def main():
    files = sorted([p for p in PLUGINS.glob('*.py')])
    results = []
    analyzed = []
    RealConfig = enrich_config(load_real_config_class())
    before = snapshot_modules()
    for p in files:
        r = try_load(p, RealConfig)
        results.append(r)
        analyzed.append(analyze_plugin_entry(p, r, RealConfig))
        restore_extra_modules(before)

    summary = {
        'total': len(results),
        'exec_ok': sum(1 for r in results if r['exec_ok']),
        'failed': sum(1 for r in results if not r['exec_ok']),
        'with_ar_cmd': sum(1 for r in results if r.get('handlers_ar_cmd', 0) > 0),
        'with_bot_cmd': sum(1 for r in results if r.get('handlers_bot_cmd', 0) > 0),
        'with_on': sum(1 for r in results if r.get('handlers_on', 0) > 0),
        'by_classification': {},
        'missing_external_modules': {},
    }
    for r in results:
        summary['by_classification'][r['classification']] = summary['by_classification'].get(r['classification'], 0) + 1
        if r['classification'] == 'missing_optional_dependency' and r.get('missing_module'):
            top = str(r['missing_module']).split('.')[0]
            if not _is_internal_module(top):
                summary['missing_external_modules'][top] = summary['missing_external_modules'].get(top, 0) + 1
    summary['missing_external_modules'] = dict(sorted(summary['missing_external_modules'].items(), key=lambda x: (-x[1], x[0])))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({'summary': summary, 'results': results}, ensure_ascii=False, indent=2), encoding='utf-8')

    fail_report = {
        'generated_by': 'scripts/plugin_harness_v4.py',
        'scope': 'all_plugins_load_exec_import_registration_analysis',
        'summary': {
            'total_plugins': len(analyzed),
            'failed_plugins': sum(1 for a in analyzed if not a['exec_ok']),
            'successful_plugins': sum(1 for a in analyzed if a['exec_ok']),
            'by_classification': summary['by_classification'],
            'analysis_notes': [
                'Classification distinguishes missing optional external dependencies and harness/interface/config issues from suspected source defects.',
                'exec_ok means module import/exec completed in mocked harness with handler registration counts observed; it does not prove functional correctness.',
            ],
        },
        'plugins': analyzed,
    }
    FAIL_OUT.write_text(json.dumps(fail_report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
