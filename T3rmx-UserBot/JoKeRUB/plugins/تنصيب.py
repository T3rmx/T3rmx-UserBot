# T3rmx UserBot - Installation / deployment help

from telethon import Button, events

from JoKeRUB import l313l
from ..Config import Config

plugin_category = "tools"


def _buttons():
    repo = getattr(Config, "T3RMX_REPOSITORY", "https://github.com/T3rmx/T3rmx-UserBot")
    updates = getattr(Config, "T3RMX_UPDATES_CHANNEL", "https://t.me/t3rmx_official")
    support = getattr(Config, "T3RMX_SUPPORT_GROUP", "https://t.me/+ByL7rwqxpEEwOTE8") or getattr(Config, "T3RMX_SUPPORT_CHANNEL", "https://t.me/+3tqPFLpxCgVjZGVk")
    rows = [
        [Button.url("Repository", repo)],
        [Button.url("Deploy to Heroku", f"{repo}#deploy-to-heroku"), Button.url("Railway Guide", f"{repo}#deploy-to-railway")],
        [Button.url("Docker Guide", f"{repo}#deploy-with-docker"), Button.url("VPS / Linux", f"{repo}#deploy-on-vps--linux")],
    ]
    extra = []
    if updates:
        extra.append(Button.url("Updates", updates))
    if support:
        extra.append(Button.url("Support", support))
    if extra:
        rows.append(extra)
    return rows


def _text():
    name = getattr(Config, "T3RMX_DISPLAY_NAME", "T3rmx UserBot")
    repo = getattr(Config, "T3RMX_REPOSITORY", "https://github.com/T3rmx/T3rmx-UserBot")
    return (
        f"**{name} — Installation & Deployment**\n\n"
        "T3rmx is deployed from a single standalone repository with in-repo configs for Heroku, Railway, Docker, VPS/systemd, and direct Linux execution.\n\n"
        f"• Repository: {repo}\n"
        "• Required vars: `APP_ID`, `API_HASH`, `STRING_SESSION`, `TG_BOT_TOKEN`, `TG_BOT_USERNAME`, `ALIVE_NAME`, `TZ`, `ENV`\n"
        "• Defaults: `TZ=Asia/Aden`, `ENV=production`\n"
        "• `TG_BOT_USERNAME` can be provided with or without `@` (normalized internally).\n\n"
        "Use the buttons below to open the repository and deployment guides. "
        "Do not use third-party installers or unknown repositories."
    )


@l313l.ar_cmd(
    pattern=r"تنصيب$",
    command=("تنصيب", plugin_category),
    info={"header": "Show T3rmx installation and deployment information.", "usage": ["{tr}تنصيب"]},
)
async def repo_install_info(event):
    await event.client.send_message(event.chat_id, _text(), buttons=_buttons(), link_preview=False)
    try:
        await event.delete()
    except Exception:
        pass


# Inline/assistant callback support (best-effort, legacy-compatible)
if Config.TG_BOT_USERNAME and getattr(l313l, "tgbot", None):
    @l313l.tgbot.on(events.InlineQuery)
    async def inline_handler(event):
        query = (event.text or "").strip()
        if event.query.user_id != l313l.uid:
            return
        if query in {"تنصيب", "السورس", "المصدر", "install", "deploy", "repo"}:
            try:
                builder = event.builder
                logo = getattr(Config, "T3RMX_LOGO", "assets/branding/t3rmx-logo.jpg")
                if logo:
                    result = builder.photo(logo, text=_text(), buttons=_buttons(), link_preview=False)
                else:
                    result = builder.article(title="T3rmx UserBot", text=_text(), buttons=_buttons(), link_preview=False)
                await event.answer([result])
            except Exception:
                pass
