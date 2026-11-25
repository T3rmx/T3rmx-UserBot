#    T3rmx UserBot assistant (derived; see LICENSE and docs/audit/SOURCE_PROVENANCE.md)
#    Preserve required attribution notices.

import asyncio
import io
import re
import time

from telethon import Button, custom, events
from telethon.errors import BadRequestError, FloodWaitError, ForbiddenError
from telethon.tl.functions.users import GetFullUserRequest
from telethon.utils import get_display_name
from JoKeRUB import bot
from ..Config import Config
from JoKeRUB.sql_helper.blacklist_assistant import (
    add_nibba_in_db,
    is_he_added,
    removenibba,
)
from JoKeRUB.sql_helper.botusers_sql import add_me_in_db, his_userid
from JoKeRUB.sql_helper.bot_starters import get_all_starters
from JoKeRUB.sql_helper.idadder_sql import (
    add_usersid_in_db,
    already_added,
    get_all_users,
)
from l313l.razan.resources.assistant import *
#start 
@tgbot.on(events.NewMessage(pattern=r"^/start(?:@[\w_]+)?(?:\s+(\S+))?$"))
async def start(event):
    if event.pattern_match.group(1):
        # Deep-link payloads (e.g. ?start=hack) are handled by their own module.
        return
    rehu = await tgbot.get_me()
    bot_id = rehu.first_name
    bot_username = rehu.username
    replied_user = await event.client(GetFullUserRequest(event.sender_id))
    firstname = replied_user.users[0].first_name
    vent = event.chat_id
    starttext = f"**مـرحبا {firstname} ! انـا هـو {bot_id}, بـوت مساعـد بسيـط 🧸🤍 \n\n- [مـالك البـوت](tg://user?id={bot.uid}) \nيمكـنك مراسلـة المـالك عبـر هذا البـوت . \n\nاذا كـنت تـريد تنـصيب بـوت خـاص بـك تـاكد من الازرار بالأسفل**"
    if event.sender_id == bot.uid:
        await tgbot.send_message(
            vent,
            message=f"اهـلا يا مالكـي انـه انـا {bot_id}, مسـاعدك ! \nمـاذا تريـد ان تفعـل اليـوم ?",
            buttons=[
                                     [Button.inline("عرض المستخدمين 📬", data="users"), Button.inline(
                                         "اوامر البـوت ⚒️", data="gibcmd")],
                                     [Button.url("Owner", f"https://t.me/{getattr(Config, 'T3RMX_OWNER_USERNAME', 'vvsks')}"), Button.inline(
                                         "اوامر الزغـرفة", data="rozzag")],

                                 ])
    else:
        if already_added(event.sender_id):
            pass
        elif not already_added(event.sender_id):
            add_usersid_in_db(event.sender_id)
        await tgbot.send_message(
            event.chat_id,
            message=starttext,
            link_preview=False,
            buttons=[
                [custom.Button.inline("تنصيب T3rmx UserBot", data="deploy")],
                [Button.url("Support", getattr(Config, "T3RMX_SUPPORT_CHANNEL", "https://t.me/T3rmx_Support_channel"))],
            ],
        )

#Data

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"deploy")))
async def help(event):
    await event.delete()
    if event.query.user_id is not bot.uid:
        await tgbot.send_message(
            event.chat_id,
            message="**لنشر نسخة T3rmx UserBot الخاصة بك، استخدم المستودع الرسمي وأدلة التنصيب المضمّنة. للمساعدة استخدم قنوات الدعم الرسمية.**",
            buttons=[
                [Button.url("Repository", getattr(Config, "T3RMX_REPOSITORY", "https://github.com/T3rmx/T3rmx-UserBot"))],
                [Button.url("Support", getattr(Config, "T3RMX_SUPPORT_GROUP", "https://t.me/T3rmx_Support_group"))],
            ],
        )


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"users")))
async def users(event):
    if event.query.user_id == bot.uid:
        await event.delete()
        total_users = get_all_users()
        users_list = "- قـائمة مستخـدمين البـوت  : \n\n"
        for starked in total_users:
            users_list += ("==> {} \n").format(int(starked.chat_id))
        with io.BytesIO(str.encode(users_list)) as tedt_file:
            tedt_file.name = "JoKeRUB.txt"
            await tgbot.send_file(
                event.chat_id,
                tedt_file,
                force_document=True,
                caption="مجموع مستخدمـين بوتـك",
                allow_cache=False,
            )
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"gibcmd")))
async def users(event):
    if event.query.user_id != bot.uid:
        await event.answer(
            "هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.",
            alert=True,
        )
        return
    await event.delete()
    rorza = "**قائمة أوامر البوت المساعد (T3rmx UserBot)**:\n- **جميع هذه الاوامر تستخدم بعد اضافة البوت في مجموعة ورفعه مشـرف مع بعض الصلاحيـات**\n• /start \n ( للـتأكد من حالـة البـوت) \n• /ping \n ( امـر بنـك )  \n• /broadcast \n ( لعمـل اذاعـة لجميـع المستخدمين في البـوت )  \n• /id \n  ( لعـرض ايدي المسـتخدم ) \n• /alive \n- ( لـرؤية معلومات البـوت ) \n• /bun \n-  ( تعمل في المجموعات لحظر شخص )\n• /unbun  \n-  ( تعمل في المجموعات لالغاء حظر مستخدم )  \n• /prumote  \n-  ( لرفـع شخص مشـرف )\n• /demute  \n-  ( لتنزيل الشخص من رتبة الاشراف ) \n• /pin  \n-  ( لتثبيـت رسالة في المجموعـة )  \n• /stats  \n-  ( لعرض مستخدمين البوت )  \n• /purge  \n-  ( بالرد على رسالة ليقوم بحذف ما تحتها من رسائل ) \n• /del  \n-  ( بالـرد على الرسالـة لحـذفها ) \n• /ack \n- ( للـتأكد من استلام الامر )"
    await tgbot.send_message(event.chat_id, rorza)


@tgbot.on(
    events.NewMessage(
        pattern=(
            r"^(?:/(?:ping|broadcast|id|alive|bun|unbun|prumote|demute|pin|stats|"
            r"purge|del|ack|help|hack)(?:@[\w_]+)?(?:\s|$)|الايدي)"
        ),
        func=lambda e: e.sender_id != bot.uid,
    )
)
async def assistant_non_owner_notice(event):
    """Block non-owners from using assistant commands."""
    await event.reply(
        "هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot."
    )


@tgbot.on(events.NewMessage(pattern="^/help", func=lambda e: e.sender_id == bot.uid))
async def starkislub(event):
    rorza = "**قائمة أوامر البوت المساعد (T3rmx UserBot)**:\n- **جميع هذه الاوامر تستخدم بعد اضافة البوت في مجموعة ورفعه مشـرف مع بعض الصلاحيـات**\n• /start \n ( للـتأكد من حالـة البـوت) \n• /ping \n ( امـر بنـك )  \n• /broadcast \n ( لعمـل اذاعـة لجميـع المستخدمين في البـوت )  \n• /id \n  ( لعـرض ايدي المسـتخدم ) \n• /alive \n- ( لـرؤية معلومات البـوت ) \n• /bun \n-  ( تعمل في المجموعات لحظر شخص )\n• /unbun  \n-  ( تعمل في المجموعات لالغاء حظر مستخدم )  \n• /prumote  \n-  ( لرفـع شخص مشـرف )\n• /demute  \n-  ( لتنزيل الشخص من رتبة الاشراف ) \n• /pin  \n-  ( لتثبيـت رسالة في المجموعـة )  \n• /stats  \n-  ( لعرض مستخدمين البوت )  \n• /purge  \n-  ( بالرد على رسالة ليقوم بحذف ما تحتها من رسائل ) \n• /del  \n-  ( بالـرد على الرسالـة لحـذفها ) \n• /ack \n- ( للـتأكد من استلام الامر )"
    await event.reply(rorza)

@tgbot.on(
    events.NewMessage(
        pattern=r"^/alive(?:@[\w_]+)?(?:\s|$)",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_alive(event):
    razan = (
        "**T3rmx UserBot**\n"
        "•━═━═━═━═━━═━═━═━═━•‌‌\n"
        "**- حالة البوت ** يعمـل بنجـاح\n"
        "**- اصدار التليثون **: 1.23.0\n"
        "**- اصدار البايثون **: 3.9.6\n"
        f"**- يوزرك ** [المالك](tg://user?id={bot.uid})\n"
        f"**- Repo:** {getattr(Config, 'T3RMX_REPOSITORY', 'https://github.com/T3rmx/T3rmx-UserBot')}\n"
        "•━═━═━═━═━━═━═━═━═━•‌‌\n"
    )
    await event.reply(razan)


@tgbot.on(
    events.NewMessage(
        pattern=r"^/ping(?:@[\w_]+)?(?:\s|$)",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_ping(event):
    started = time.monotonic()
    msg = await event.reply("🏓 **پنك ...**")
    latency = int((time.monotonic() - started) * 1000)
    await msg.edit(f"🏓 **پنك** `{latency} ms`")


@tgbot.on(
    events.NewMessage(
        pattern=r"^/ack(?:@[\w_]+)?(?:\s|$)",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_ack(event):
    await event.reply("✅ **تم الاستلام**")


@tgbot.on(
    events.NewMessage(
        pattern=r"^/stats(?:@[\w_]+)?(?:\s|$)",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_stats(event):
    try:
        starters = get_all_starters() or []
    except Exception as exc:
        return await event.reply(f"**تعذر جلب الاحصائيات:** `{type(exc).__name__}`")
    text = f"**احصائيات البوت المساعد**\n• عدد المستخدمين: `{len(starters)}`"
    if starters:
        ids = "\n".join(f"• `{int(user.user_id)}`" for user in starters[:20])
        text += f"\n• أول 20 معرّف:\n{ids}"
    await event.reply(text)


@tgbot.on(
    events.NewMessage(
        pattern=r"^/broadcast(?:@[\w_]+)?(?:\s|$)",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_broadcast(event):
    replied = await event.get_reply_message()
    if not replied:
        return await event.reply("**يجب الرد على رسالة أولا لعمل اذاعة.**")
    users = get_all_starters() or []
    if not users:
        return await event.reply("**عدد مستخدمين البوت: 0، لم يتم الاذاعة.**")
    status = await event.reply("**جار الاذاعة ... أنتظر قليلا**")
    sent = 0
    skipped = 0
    for user in users:
        try:
            await tgbot.send_message(int(user.user_id), replied)
            sent += 1
            await asyncio.sleep(0.8)
        except FloodWaitError as exc:
            await asyncio.sleep(exc.seconds)
        except (BadRequestError, ValueError, ForbiddenError):
            skipped += 1
        except Exception:
            skipped += 1
    await status.edit(
        f"**تمت الاذاعة بنجاح إلى {sent} مستخدم.**\n**تم تخطي {skipped} مستخدم.**"
    )


async def _assistant_target(event):
    replied = await event.get_reply_message()
    if replied and replied.sender_id:
        return int(replied.sender_id), None
    raw = (event.pattern_match.group(1) or "").strip()
    if not raw:
        return None, "يجب الرد على الرسالة أو كتابة معرّف المستخدم."
    if raw.isdigit():
        return int(raw), None
    if raw.startswith("@"):
        return raw, None
    return None, "تعذر فهم المستخدم. استخدم الرد أو المعرّف أو المعرف."


async def _resolve_assistant_user(identifier, event):
    try:
        return await tgbot.get_entity(identifier)
    except Exception as exc:
        await event.reply(f"**تعذر العثور على المستخدم:** `{type(exc).__name__}`")
        return None


async def _assistant_group(event):
    if event.is_group:
        return True
    await event.reply("هذا الأمر يعمل في المجموعات فقط.")
    return False


@tgbot.on(
    events.NewMessage(
        pattern=r"^/bun(?:@[\w_]+)?(?:\s+([\s\S]*))?$",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_ban_user(event):
    if not await _assistant_group(event):
        return
    identifier, error = await _assistant_target(event)
    if error:
        return await event.reply(f"**{error}**")
    user = await _resolve_assistant_user(identifier, event)
    if not user:
        return
    if user.id == bot.uid:
        return await event.reply("لا يمكنني حظر مالك البوت.")
    try:
        await tgbot.edit_permissions(event.chat_id, user, view_messages=False)
        await event.reply(f"**تم حظر {get_display_name(user)} من المجموعة.**")
    except Exception as exc:
        await event.reply(f"**تعذر الحظر:** `{type(exc).__name__}`")


@tgbot.on(
    events.NewMessage(
        pattern=r"^/unbun(?:@[\w_]+)?(?:\s+([\s\S]*))?$",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_unban_user(event):
    if not await _assistant_group(event):
        return
    identifier, error = await _assistant_target(event)
    if error:
        return await event.reply(f"**{error}**")
    user = await _resolve_assistant_user(identifier, event)
    if not user:
        return
    try:
        await tgbot.edit_permissions(event.chat_id, user, view_messages=True)
        await event.reply(f"**تم الغاء حظر {get_display_name(user)} في المجموعة.**")
    except Exception as exc:
        await event.reply(f"**تعذر الغاء الحظر:** `{type(exc).__name__}`")


@tgbot.on(
    events.NewMessage(
        pattern=r"^/prumote(?:@[\w_]+)?(?:\s+([\s\S]*))?$",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_promote_user(event):
    if not await _assistant_group(event):
        return
    identifier, error = await _assistant_target(event)
    if error:
        return await event.reply(f"**{error}**")
    user = await _resolve_assistant_user(identifier, event)
    if not user:
        return
    try:
        await tgbot.edit_permissions(
            event.chat_id,
            user,
            change_info=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=False,
            manage_call=True,
            manage_messages=True,
        )
        await event.reply(f"**تم رفع {get_display_name(user)} إلى الاشراف.**")
    except Exception as exc:
        await event.reply(f"**تعذر رفع المستخدم:** `{type(exc).__name__}`")


@tgbot.on(
    events.NewMessage(
        pattern=r"^/demute(?:@[\w_]+)?(?:\s+([\s\S]*))?$",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_demote_user(event):
    if not await _assistant_group(event):
        return
    identifier, error = await _assistant_target(event)
    if error:
        return await event.reply(f"**{error}**")
    user = await _resolve_assistant_user(identifier, event)
    if not user:
        return
    try:
        await tgbot.edit_permissions(
            event.chat_id,
            user,
            change_info=False,
            delete_messages=False,
            ban_users=False,
            invite_users=False,
            pin_messages=False,
            add_admins=False,
            manage_call=False,
            manage_messages=False,
        )
        await event.reply(f"**تم تنزيل {get_display_name(user)} من الاشراف.**")
    except Exception as exc:
        await event.reply(f"**تعذر تنزيل المستخدم:** `{type(exc).__name__}`")


@tgbot.on(
    events.NewMessage(
        pattern=r"^/pin(?:@[\w_]+)?$",
        func=lambda e: e.sender_id == bot.uid,
    )
)
async def assistant_pin(event):
    if not await _assistant_group(event):
        return
    msg = await event.get_reply_message()
    if not msg:
        return await event.reply("**يجب الرد على الرسالة التي تريد تثبيتها.**")
    try:
        await tgbot.pin_message(event.chat_id, msg.id, notify=False)
        await event.reply("**تم تثبيت الرسالة.**")
    except Exception as exc:
        await event.reply(f"**تعذر تثبيت الرسالة:** `{type(exc).__name__}`")





@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rozzag"))) 
async def settings(event):
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 "**⌯︙ اختر احد خيارات الزغرفه : **",
                                 buttons=[
                                 [Button.inline(
                                     "اسماء انكلش َِ🛹", data="rozname"),
                                  Button.inline(
                                     "البايو َِ🛹", data="rozpio1")],
                                 [Button.inline(
                                     "الاشهر َِ🛹 ⁦⁩", data="rozmonth"),
                                  Button.inline(
                                     "اسماء القنوات َِ🛹", data="chanlan")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)




@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rozname"))) 
async def settings(event):  
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 "**⌯︙ اختر احد الخيارات الاتيه. **",
                                 buttons=[
                                     [Button.inline(
                                         "اسماء شباب َِ🛹 ", data="razan"),
                                      Button.inline(
                                         "اسماء بنات َِ🛹", data="RR7PP"),
                                      Button.inline(
                                         "║ رجوع ║ ⁦⁩", data="rozzag")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"razan")))  
async def settings(event):  
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 "**⌯︙ اختر احد الخيارات الاتيه. **",
                                 buttons=[
                                     [Button.inline(
                                         "القائمه الاولى َِ🛹 ", data="rzan1"),
                                      Button.inline(
                                         "القائمه الثانيه َِ🛹", data="raza2")],
                                     [Button.inline(
                                         "║ رجوع ║", data="rozname")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)



# Boys zag list1 - قائمه اسماء الشباب 
@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rzan1")))
async def settings(event): #   
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 Boyroz1, 
                                 buttons=[[Button.inline("║ رجوع ║", data="razan")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


# Boys zag list2 - قائمه اسماء الشباب الثانيه
@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"raza2"))) 
async def settings(event):  #    قـسـم  الزغرفـة لأسـماء الشـباب 2
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 Boyroz2, 
                                 buttons=[[Button.inline("║ رجوع ║", data="razan")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"RR7PP")))
async def settings(event): #    قـسـم  الزغرفـة لأسـماء البـنات
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 "**⌯︙ اختر احد الخيارات الاتيه. **",
                                 buttons=[
                                     [Button.inline(
                                         "القائمه الاولى َِ🛹 ", data="RR7PP1"),
                                      Button.inline(
                                         "القائمه الثانيه َِ🛹", data="RR7PP2")],
                                     [Button.inline(
                                         "║ رجوع ║", data="rozname")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)

# شنو تـدور  :)
@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"RR7PP1")))
async def settings(event): #    قـسـم  الزغرفـة لأسـماء البـنات 1
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 Girlan1, 
                                 buttons=[[Button.inline("║ رجوع ║", data="RR7PP")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"RR7PP2")))
async def settings(event):  #    قـسـم  الزغرفـة لأسـماء البـنات 2
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 Girlan2, 
                                 buttons=[[Button.inline("║ رجوع ║", data="RR7PP")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rozpio1"))) 
async def settings(event):  #    قـسـم  البـايو 1
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 ROZPIO1,
                                 buttons=[
                                     [Button.inline(
                                         " السابق ⫸", data="rozpio5"),
                                      Button.inline(
                                         "║ خروج ║ ⁦⁩", data="rozzag"),
                                      Button.inline(
                                         "⫷ التالي ", data="rozpio2")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rozpio2"))) 
async def settings(event): #    قـسـم  البـايو 2
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 ROZPIO2,
                                 buttons=[
                                     [Button.inline(
                                         "السابق ⫸ ", data="rozpio1"),
                                      Button.inline(
                                         "║ خروج ║ ⁦⁩", data="rozzag"),
                                      Button.inline(
                                         "⫷ التالي", data="rozpio3")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rozpio3"))) 
async def settings(event): #    قـسـم  البـايو 3
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 ROZPIO3,
                                 buttons=[
                                     [Button.inline(
                                         "السابق ⫸ ", data="rozpio2"),
                                      Button.inline(
                                         "║ خروج ║ ⁦⁩", data="rozzag"),
                                      Button.inline(
                                         "⫷ التالي", data="rozpio4")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rozpio4"))) 
async def settings(event): #    قـسـم  البـايو 4
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 ROZPIO4,
                                 buttons=[
                                     [Button.inline(
                                         "السابق ⫸ ", data="rozpio3"),
                                      Button.inline(
                                         "║ خروج ║ ⁦⁩", data="rozzag"),
                                      Button.inline(
                                         "⫷ التالي", data="rozpio5")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rozpio5"))) 
async def settings(event):#    قـسـم  البـايو 5
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 ROZPIO5,
                                 buttons=[
                                     [Button.inline(
                                         "السابق ⫸ ", data="rozpio4"),
                                      Button.inline(
                                         "║ خروج ║⁦⁩", data="rozzag"),
                                      Button.inline(
                                         "⫷ التالي", data="rozpio1")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rozmonth")))  
async def settings(event): #    قـسم الـمواليـد و الأشـهر
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id,
                                 "**⌯︙ اختر احد الخيارات الاتيه. **",
                                 buttons=[
                                     [Button.inline(
                                         "المواليد َِ🛹 ", data="rozyear"),
                                      Button.inline(
                                         "الاشهر َِ🛹", data="months")],
                                     [Button.inline(
                                         "║ رجوع ║", data="rozzag")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"months")))  
async def settings(event):#    قـسم  الأشـهر
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id, 
                                 JMTHSH, 
                                 buttons=[[Button.inline("║ رجوع ║", data="rozzag")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)

@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"rozyear")))  
async def settings(event):#    قـسم  السنـوات  :)
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id, 
                                 JEPYEAR, 
                                 buttons=[[Button.inline("║ رجوع ║", data="rozmonth")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)


@tgbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"chanlan")))  
async def settings(event):  
    if event.sender_id == bot.uid:
        await event.delete()
        await tgbot.send_message(event.chat_id, 
                                 CHANLAN, 
                                 buttons=[[Button.inline("║ رجوع ║", data="rozzag")]
                                 ])
    else:
        await event.answer("هذا البوت خاص. يمكنك نشر نسختك من مستودع T3rmx UserBot.", alert=True)
