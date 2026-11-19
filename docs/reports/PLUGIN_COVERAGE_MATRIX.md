# T3rmx UserBot — 104-Plugin Test Coverage Matrix

## Full command sweep (2026-11-19, final)
Every command token found in the 104 plugin sources was extracted and classified (623 entries total). Commands were sent as a normal user from Saved Messages (chat `6023224495`) in 29 batches.

- **571 commands executed** (541 LOW-risk + 30 admin/menu commands safe as bare no-arg invocations in Saved Messages).
- **52 commands deliberately skipped** (broadcast, message/data deletion, shutdown/restart, install, AFK/sleep state, mass spam/ban/kick, sudo changes) — not run without explicit approval.
- **Result:** every executed command either returned a normal user-level response or a clear graceful Arabic message (needs reply/argument/context or external service unavailable). No unhandled exception remained in Railway logs after the final deploy.
- **Final deploy:** `ff806ff0-7b93-43a2-a743-1a6471cf6df1` — SUCCESS, `/health` 200, all plugin modules loaded, `.فحص` replied "T3rmx UserBot is running ✓".

Additional bugs found and fixed during this sweep (all committed and pushed):
| Plugin | Error | Fix |
|---|---|---|
| `اضافة.py` | `struct.error: GetFullChatRequest(chat_id='...')` | reject non-numeric chat arg early |
| `بنك.py` | missing-account guard crashed on uneditable message | edit→reply fallback |
| `بنك.py` | handler `func=lambda m:"راتب"` (always truthy) fired on **every** message | replaced with real `_bank_game_filter` |
| `بنك.py` | `.استثمار` with no/blank amount → `ValueError: invalid literal for int()` | validate digit amount |
| `اغنية.py` | `.بحث` with no query → `ValueError: message cannot be empty` | require query argument |
| `لستة.py` | empty inline results → `IndexError` | guard inline query results |
| `الصيغ.py` | `.تحويل متحركة` without reply → `NoneType.download_media` | require media reply |
| `اوامر الكروب.py` | `.ارسل` with no args → `IndexError: no such group` | parse/validate args |
| `تسلية1.py` / `تسلية4.py` | animation index `i % 10`/`i % 30` exceeded short char lists | use `% len(animation_chars)` |
| `تحذير.py` | warning without reply → `NoneType.sender_id` | require reply target |
| `منوع.py` | prayer times: `download_file(InputWebFileLocation)` → `TypeError: Cannot cast...` | fetch via HTTP with graceful fallback |
| `core/managers.py` / `core/client.py` | rapid testing FloodWait errors escalated to tracebacks | catch/fall back to reply; suppress transient FloodWait |

## تحديث: اختبار يدوي عبر MCP (2026-11-19)
تم اختبار أوامر عربية/إنجليزية يدوياً في الرسائل المحفوظة (chat 6023224495) كمستخدم عادي عبر MCP. النتائج:
- **أوامر تم تنفيذها بنجاح أو ردّت برسالة واضحة:** `.الاوامر`، `.فحص`، `.السورس`، `.المطور`، `.اذكار`، `.الردود`، `.فحص`، `.حاسبة`، `.الطقس`، `.م1`–`.م21`، `.تحديث`، `.تحديث الان`، `.غنيلي`، `.sec`، `.الم territorio`، `.معلوماتي`، `.معلومات`، `.تاك`، `.ملكية`، `.تاريخ`، `.متى`، `.تلكراف`، `.تهكير`، `.تطبيق`، `.اخفاء`، `.مصغر`، `.دنس`، `.صور`، `.تحويل`، `.زغرفة`، `.تشكيل`، `.النص`، `.لستة`، `.منشن`، `.فلم`، `.كورونا`، `.سرعة`، `.التحذيرات`، `.الملصقات`، `.انستا`، `.القنابل`، `.افعى`، `.الكعده`، `.الكمر`، `.البنر`، `.تغريد`، `.من`، `.اسم`، `.الاغنية`، `.شعر`، `.قران`، `.ثيم`، `.زيج`، `.اتصل`، `.افكر`، `.افكرر`، `.تك`، `.تخزين`، `.الفارات`، `.استخدامي`، `.قائمة`، `.رابط` — بدون أخطاء في السجل بعد الإصلاح.
- **أخطاء تم اكتشافها وإصلاحها أثناء الاختبار (6 بلاجنات):** `الحاسبة.py` (`e.client._bot`)، `طقس.py` (`KeyError 'IQ'`)، `فلم.py` (`Fernet=None`)، `ميمز.py` (`WebpageCurlFailedError` في `.قران`/`.ثيم`/`.انمي10`)، `الوهمي.py` (`PeerIdInvalidError` + `eod(time=)`).
- **حالة السجل النهائية:** 0 أخطاء / 0 استثناءات غير معالجة في آخر 600 سطر من سجلات Railway بعد إعادة النشر.
- **ملاحظة:** الأوامر التي تحتاج رداً أو وسائط (مثل `.الصورة`، `.البحث` بدون معاملات) لم تُختبر وظيفياً بالكامل لأنها تتطلب سياق تفاعلي؛ تم تسجيلها كـ PARTIAL.


Generated: 2026-11-19. Evidence: plugin harness v4 (104/104 import/exec), Railway container logs (all plugins loaded), Telegram MCP live tests in Saved Messages (chat 6023224495) for selected plugins. Status vocabulary: `PASS|FAIL|PARTIAL|BLOCKED|NOT_TESTED`.

| Plugin | Import | Registration | Handler execution | Functional test | Dependency status | DB dependency | Integration test | Railway runtime status | Remaining issues |
|---|---|---|---|---|---|---|---|---|---|
| __init__.py | PASS | PASS (support) | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| afk.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| احچي.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ادوات_الروابط.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| اشراف عام.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| اضافة.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| اغنية.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الادمن.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الاذاعه.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الاذكار.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الانتحال.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الاوامر.py | PASS | PASS | PASS | PASS | PASS (core+pinned) | Yes | PARTIAL | PASS (loaded) | DB-backed runtime flow not exercised |
| البروفايل.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| التثبيت.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| التجميع.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| التحكم.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| التخزين.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| التخصيص.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الترجمه.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الترحيب.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الترحيب2.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| التقليد.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| التكرار.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| التمبلر.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| التنظيف.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الثكيل.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الحاسبة.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الحماية.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الخطوط.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الردود.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الصلاة.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الصلاحيات.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الصورة.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الصيغ.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الفارات.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الكتم.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| المطور.py | PASS | PASS | PASS | PASS | PASS (core+pinned) | Yes | PARTIAL | PASS (loaded) | DB-backed runtime flow not exercised |
| الملصقات.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| الموقع.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الوقت.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| الوقتي.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PARTIAL (optional-external lazy) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; optional external dependency unverified at runtime; handler execution not exercised |
| الوهمي.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| امونغ اس.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| اوامر الادمن الوقتية.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| اوامر التشغيل.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| اوامر الكروب.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| اوامر المنع.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| اوامري.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| بنك.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| تاريخ اسماء.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تحديث.py | PASS | PASS | PASS | PASS | PASS (core-only) | No | PARTIAL | PASS (loaded) | none observed in tested paths |
| تحذير.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| تحشيش .py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تحشيش.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ترجمة صوتية.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PARTIAL (optional-external lazy) | No | NOT_TESTED | PASS (loaded) | optional external dependency unverified at runtime; handler execution not exercised |
| تسلية1.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تسلية2.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تسلية3.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تسلية4.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تسلية5.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تسلية6.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تسلية7.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تسلية8.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تشكيل.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تطبيق.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تفرعات الاوامر.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تلكراف.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تنصيب.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تهكير.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| تيكتوك.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ذاتية.py | PASS | PARTIAL | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| رسالة موقوته.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| رسالة.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| زغرفة.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| سرعة النت.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| سي ام دي.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| صور.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ضع تكرار.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| طقس.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| فايروس كورونا.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PARTIAL (optional-external lazy) | No | NOT_TESTED | PASS (loaded) | optional external dependency unverified at runtime; handler execution not exercised |
| فحص.py | PASS | PASS | PASS | PASS | PASS (core+pinned) | Yes | PARTIAL | PASS (loaded) | DB-backed runtime flow not exercised |
| فلم.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| كشف.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| كوكل.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| لستة.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| متحركات ساد.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| متحركات كيوت.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| معلومات الحساب.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| معلومات الكروب.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ملخص معلومات.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ملفات السورس.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ملفات خارجيه.py | PASS | PARTIAL | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ملكية.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| منشن.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| منوع.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ميم.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core-only) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ميمز.py | PASS | PASS | PASS | PARTIAL | PASS (core+pinned) | No | PARTIAL | PASS (loaded) | none observed in tested paths |
| نشر تلقائي.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| نص.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| نوم.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| همسه.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | No | NOT_TESTED | PASS (loaded) | handler execution not exercised |
| ياعلي.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
| يوتيوب.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PARTIAL (optional-external lazy) | No | NOT_TESTED | PASS (loaded) | optional external dependency unverified at runtime; handler execution not exercised |
| ييبنك.py | PASS | PASS | NOT_TESTED | NOT_TESTED | PASS (core+pinned) | Yes | NOT_TESTED | PASS (loaded) | DB-backed runtime flow not exercised; handler execution not exercised |
