"""Deterministic wiring checks for the assistant bot commands.

Run with: python3 scripts/check_assistant_commands.py
No credentials or running Telegram client are needed.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ASSISTANT = ROOT / "T3rmx-UserBot" / "JoKeRUB" / "assistant"

EXPECTED = {
    "/start": ("start.py", False),
    "/ping": ("start.py", True),
    "/broadcast": ("start.py", True),
    "/id": ("id.py", True),
    "/alive": ("start.py", True),
    "/bun": ("start.py", True),
    "/unbun": ("start.py", True),
    "/prumote": ("start.py", True),
    "/demute": ("start.py", True),
    "/pin": ("start.py", True),
    "/stats": ("start.py", True),
    "/purge": ("purge.py", True),
    "/del": ("purge.py", True),
    "/ack": ("start.py", True),
}


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    sources = {p.name: p.read_text(encoding="utf-8") for p in ASSISTANT.glob("*.py")}
    combined = "\n".join(sources.values())

    for command, (filename, owner_only) in EXPECTED.items():
        source = sources.get(filename, "")
        needle = "id|الايدي" if command == "/id" else command
        check(needle in source, f"{command} handler is missing from {filename}")
        if command != "/start":
            check(
                "(?:@[\\w_]+)?" in source,
                f"{command} does not accept a @botusername suffix in groups",
            )
        if owner_only:
            check(
                "e.sender_id == bot.uid" in source or "e.sender_id == OWNER_ID" in source,
                f"{command} is not owner-only",
            )

    check(
        "id|الايدي" in sources["id.py"],
        "id slash and Arabic aliases are incomplete",
    )
    check("{mention}" not in combined, "alive still contains the literal {mention} placeholder")
    check(
        "or OWNER_ID or SUDO_USERS" not in combined,
        "purge admin check still has the always-true OWNER_ID expression",
    )
    check(
        "assistant_non_owner_notice" in combined,
        "non-owner command notice handler is missing",
    )
    notice = sources["start.py"]
    for command in EXPECTED:
        if command == "/start":
            continue
        name = command.lstrip("/")
        check(name in notice[notice.index("assistant_non_owner_notice") - 400:],
              f"non-owner notice does not cover {command}")

    total = len(EXPECTED)
    print(f"assistant command wiring checks: OK ({total} commands)")


if __name__ == "__main__":
    main()
