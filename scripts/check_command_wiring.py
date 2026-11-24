"""Deterministic command wiring/collision check.

Run with: python3 scripts/check_command_wiring.py

It rebuilds the plugin harness report, extracts every dot-command shown in the
Arabic menus/help text, and asserts that each one reaches exactly one registered
handler after normalising placeholders and required arguments.
"""

import contextlib
import io
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PLUGINS = ROOT / "T3rmx-UserBot" / "JoKeRUB" / "plugins"

MENU_FILES = [
    "الاوامر.py",
    "تفرعات الاوامر.py",
    "الصيد.py",
    "الاذكار.py",
    "ميمز.py",
]

IGNORED_COMMANDS = {"{name}"}

# Commands advertised in `.م19` as conditional on an external voice-call
# backend, plus the bank game which registers a dynamic `func` filter that the
# static harness cannot see. These are documented as unavailable / dynamic by
# design, not broken command wiring.
DOCUMENTED_COMMANDS = {
    "تشغيل_المكالمة",
    "انهاء_المكالمة",
    "دعوة",
    "معلومات_المكالمة",
    "تسمية_المكالمة",
    "انضمام",
    "مغادرة",
    "تشغيل",
    "قائمة_التشغيل",
    "ايقاف_مؤقت",
    "استمرار",
    "تخطي",
    "البنك",
}


def handler_prefixes(pattern):
    """Extract the literal command word(s) a handler claims."""
    text = str(pattern or "").lstrip("^")
    if text.startswith(r"\#"):
        text = text[2:]
    if text.startswith(r"\."):
        text = text[2:]
    if text.startswith("("):
        end = text.find(")")
        if end != -1:
            alternatives = text[1:end].split("|")
            return {
                part.strip()
                for part in alternatives
                if part.strip() and not re.search(r"[()\[\]?*+{}\\$]", part)
            }
        return set()
    match = re.match(r"[^\[\]()?*+{}|\\$]+", text)
    return {match.group(0).strip()} if match and match.group(0).strip() else set()


def build_report():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import plugin_harness_v4 as harness

    with contextlib.redirect_stdout(io.StringIO()):
        harness.main()
    return json.loads(harness.OUT.read_text(encoding="utf-8"))


def compile_handlers(report):
    handlers = []
    for result in report["results"]:
        for key in ("patterns", "on_patterns"):
            for item in result.get(key, []):
                pattern = item.get("pattern")
                if not pattern:
                    continue
                try:
                    expression = (
                        pattern
                        if pattern.startswith(("^", r"\#"))
                        else r"^\." + pattern
                    )
                    regex = re.compile(expression)
                except re.error:
                    continue
                handlers.append(
                    {
                        "file": result["file"],
                        "kind": key,
                        "pattern": pattern,
                        "regex": regex,
                        "prefixes": handler_prefixes(pattern),
                    }
                )
    return handlers


def menu_commands():
    commands = set()
    for name in MENU_FILES:
        path = PLUGINS / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"`\.([^`\n]+)`", text):
            raw = match.group(1).strip()
            raw = re.split(r"\s*\+\s*|\s+بالرد|\s+مع\s|\s*\(", raw, maxsplit=1)[0]
            raw = raw.strip(" ,،-")
            if raw:
                commands.add(raw)
    return sorted(commands - IGNORED_COMMANDS)


def command_candidates(raw):
    """Turn menu notation into concrete outgoing Telegram messages."""
    base = raw.strip().strip(" ,،-")
    variants = {base}
    if "/" in base:
        pieces = base.split("/")
        prefix = pieces[0].rsplit(" ", 1)[0] if " " in pieces[0] else ""
        for piece in pieces:
            candidate = piece.strip()
            if prefix and not candidate.startswith(prefix):
                candidate = f"{prefix} {candidate}"
            variants.add(candidate)
    expanded = set()
    for variant in variants:
        normalised = re.sub(r"<[^>]+>", "123", variant)
        normalised = re.sub(r"\[[^\]]+\]", "123", normalised)
        expanded.add(normalised)
        expanded.add(normalised + " اختبار")
    return sorted(v for v in expanded if v)


def main():
    report = build_report()
    handlers = compile_handlers(report)
    commands = menu_commands()

    unwired = []
    collisions = []
    for command in commands:
        hits_for_command = []
        for candidate in command_candidates(command):
            hits = [
                handler
                for handler in handlers
                if handler["regex"].match("." + candidate)
            ]
            if hits:
                hits_for_command.append((candidate, hits))
        if not hits_for_command:
            # A handler like `جلب (ALIAS...)$` owns the command word `جلب`
            # without matching a generic test argument.
            prefix_hits = [
                handler
                for handler in handlers
                if command in handler["prefixes"]
            ]
            if prefix_hits:
                hits_for_command.append(("(prefix)", prefix_hits))
        if not hits_for_command and command not in DOCUMENTED_COMMANDS:
            unwired.append(command)
        for candidate, hits in hits_for_command:
            if len(hits) > 1:
                collisions.append(
                    (
                        command,
                        candidate,
                        [
                            f"{h['file']}:{h['kind']} {h['pattern']}"
                            for h in hits
                        ],
                    )
                )

    duplicate_patterns = defaultdict(list)
    for handler in handlers:
        duplicate_patterns[handler["pattern"]].append(handler["file"])
    duplicates = {
        pattern: sorted(set(files))
        for pattern, files in duplicate_patterns.items()
        if len(set(files)) > 1
    }

    print(f"menu commands: {len(commands)}")
    print(f"unwired commands: {len(unwired)}")
    for command in unwired:
        print(f"  UNWIRED {command}")
    print(f"colliding commands: {len(collisions)}")
    for command, candidate, hits in collisions:
        print(f"  COLLISION {command} -> .{candidate}: {' | '.join(hits)}")
    print(f"duplicate raw patterns: {len(duplicates)}")
    for pattern, files in sorted(duplicates.items()):
        print(f"  DUPLICATE {pattern}: {', '.join(files)}")

    if unwired or collisions or duplicates:
        raise SystemExit(1)
    print("command wiring checks: OK")


if __name__ == "__main__":
    main()
