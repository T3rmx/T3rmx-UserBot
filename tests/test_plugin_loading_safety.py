import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_by_path(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem + "_testmod", str(path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    return spec, mod


def test_core_plugin_files_compileable():
    # Basic syntax/import-structure check by compiling representative files
    files = [
        ROOT / "T3rmx-UserBot/JoKeRUB/core/client.py",
        ROOT / "T3rmx-UserBot/JoKeRUB/core/auth.py",
        ROOT / "T3rmx-UserBot/JoKeRUB/plugins/المطور.py",
        ROOT / "T3rmx-UserBot/JoKeRUB/plugins/تحديث.py",
        ROOT / "T3rmx-UserBot/JoKeRUB/plugins/تنصيب.py",
    ]
    for f in files:
        src = f.read_text(encoding="utf-8")
        compile(src, str(f), "exec")


def test_startup_module_importable_syntax_only():
    # Avoid executing side effects; compile only
    f = ROOT / "T3rmx-UserBot/JoKeRUB/utils/startup.py"
    compile(f.read_text(encoding="utf-8"), str(f), "exec")
