 

import asyncio

from telethon import events
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError
from telethon.tl.types import ChannelParticipantsAdmins

from JoKeRUB import bot
from .. import *

OWNER_ID = bot.uid
# للتاكد من صلاحيات المشرف

async def is_administrator(user_id: int, message):
    if user_id == OWNER_ID:
        return True
    async for user in tgbot.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id:
            return True
    return False


@tgbot.on(
    events.NewMessage(
        pattern=r"^/purge(?:@[\w_]+)?(?:\s|$)",
        func=lambda e: e.sender_id == OWNER_ID,
    )
)
async def purge(event):
    if not event.is_group:
        await event.reply("هذا الأمر يعمل في المجموعات فقط.")
        return
    chat = event.chat_id
    msgs = []

    if not await is_administrator(user_id=event.sender_id, message=event):
        await event.reply("انـت لسـت ادمـن!")
        return

    msg = await event.get_reply_message()
    if not msg:
        await event.reply("قـم بالـرد على الـرسالة التـي تريـد حذف الـرسائل التـي تحـتها.")
        return

    try:
        msg_id = msg.id
        count = 0
        to_delete = event.message.id - 1
        await tgbot.delete_messages(chat, event.message.id)
        msgs.append(event.reply_to_msg_id)
        for m_id in range(to_delete, msg_id - 1, -1):
            msgs.append(m_id)
            count += 1
            if len(msgs) == 100:
                await tgbot.delete_messages(chat, msgs)
                msgs = []

        await tgbot.delete_messages(chat, msgs)
        del_res = await tgbot.send_message(
            event.chat_id, f"تنظيف سريع {count} رسالة ."
        )

        await asyncio.sleep(4)
        await del_res.delete()

    except MessageDeleteForbiddenError:
        text = "خـطأ في حـذف الـرسائل.\n"
        text += "الـرساله قد تكون قديمة او ليسـت لديـك صلاحـيات الـحذف"
        del_res = await event.reply(text, parse_mode="md")
        await asyncio.sleep(5)
        await del_res.delete()


@tgbot.on(
    events.NewMessage(
        pattern=r"^/del(?:@[\w_]+)?$",
        func=lambda e: e.sender_id == OWNER_ID,
    )
)
async def delete_msg(event):
    if not event.is_group:
        await event.reply("هذا الأمر يعمل في المجموعات فقط.")
        return

    if not await is_administrator(user_id=event.sender_id, message=event):
        await event.reply("انـت لـست ادمـن!")
        return

    chat = event.chat_id
    msg = await event.get_reply_message()
    if not msg:
        await event.reply("قـم بالـرد على الـرسالة التـي تريـد حذفها.")
        return
    to_delete = event.message
    chat = await event.get_input_chat()
    rm = [msg, to_delete]
    await tgbot.delete_messages(chat, rm)
