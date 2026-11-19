"""Graceful VC/music command integration for T3rmx.

Registers preserved VC/music command names when a command client is available.
When no verified backend is configured, commands respond with adapter status
instead of attempting unsafe external installs or invoking a missing backend.
"""

from __future__ import annotations

from .adapter import get_vc_status

try:
    from JoKeRUB import l313l
except Exception:  # pragma: no cover
    l313l = None

VC_COMMANDS = [
    "ميوزك",
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
]


def _status_message():
    st = get_vc_status()
    state = "متاح" if st.available else "غير متاح"
    configured = "نعم" if st.configured else "لا"
    enabled = "مفعّل" if st.enabled else "غير مفعّل"
    return (
        "**T3rmx-VC**\n"
        f"• الحالة: {state}\n"
        f"• التفعيل: {enabled}\n"
        f"• مهيأ: {configured}\n"
        f"• الخلفية (backend): `{st.backend}`\n"
        f"• التفاصيل: {st.message}\n\n"
        "لا يتم تحميل أو تشغيل أي Backend خارجي تلقائياً. "
        "للتشغيل الفعلي يجب توفير Backend متحقق وتهيئته عبر متغيرات T3RMX_VC_*."
    )


async def _vc_unavailable_handler(event):
    try:
        await event.edit(_status_message())
    except Exception:
        try:
            await event.reply(_status_message())
        except Exception:
            pass


def register_vc_commands(client=None):
    """Register graceful handlers for preserved VC command names."""
    cli = client or l313l
    if cli is None:
        return 0

    # Prefer ar_cmd decorator if present (T3rmx/JoKeRUB client)
    if hasattr(cli, "ar_cmd"):
        for cmd in VC_COMMANDS:
            try:
                @cli.ar_cmd(pattern=f"{cmd}(?:\\s|$)([\\s\\S]*)")
                async def _handler(event, _cmd=cmd):
                    await _vc_unavailable_handler(event)
            except Exception:
                continue
        return len(VC_COMMANDS)

    # Fallback: try telethon-style on pattern
    if hasattr(cli, "on"):
        try:
            from telethon import events
        except Exception:
            return 0
        for cmd in VC_COMMANDS:
            try:
                @cli.on(events.NewMessage(pattern=rf"^[\./،]{cmd}"))
                async def _handler(event, _cmd=cmd):
                    await event.reply(_status_message())
            except Exception:
                continue
        return len(VC_COMMANDS)

    return 0
