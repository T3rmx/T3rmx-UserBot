from telethon import events
from telethon.utils import pack_bot_file_id

from JoKeRUB import bot


@tgbot.on(
    events.NewMessage(
        pattern=r"^(?:/(?:id|الايدي)(?:@[\w_]+)?(?:\s|$)|الايدي)",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_id(event):
    replied = await event.get_reply_message()
    if replied:
        user_id = replied.sender_id or replied.from_id
        text = (
            f"⌯︙ايـدي الـدردشة: `{event.chat_id}`\n"
            f"⌯︙ايدي المستخدم: `{user_id}`"
        )
        if replied.media:
            try:
                text += f"\n⌯︙ايدي الملف: `{pack_bot_file_id(replied.media)}`"
            except Exception:
                pass
        return await event.reply(text)
    await event.reply(
        f"⌯︙ايـدي الـدردشة: `{event.chat_id}`\n"
        f"⌯︙ايديك: `{event.sender_id}`"
    )

