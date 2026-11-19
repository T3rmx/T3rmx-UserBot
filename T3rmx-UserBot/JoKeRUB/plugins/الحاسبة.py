import ast
import operator
import re

from telethon import Button
from telethon.events import CallbackQuery, InlineQuery

from JoKeRUB import CMD_HELP, l313l

# 𝗧𝗲𝗹𝗲𝗚𝗿𝗮𝗠 : @t3rmx_official  ~ @vvsks
from ..core.decorators import check_owner

CALC = {}
plugin_category = "utils"

m = [
    "AC",
    "C",
    "⌫",
    "%",
    "7",
    "8",
    "9",
    "+",
    "4",
    "5",
    "6",
    "-",
    "1",
    "2",
    "3",
    "x",
    "00",
    "0",
    ".",
    "÷",
]
tultd = [Button.inline(f"{x}", data=f"calc{x}") for x in m]
lst = list(zip(tultd[::4], tultd[1::4], tultd[2::4], tultd[3::4]))
lst.append([Button.inline("=", data="calc=")])


_ALLOWED_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
}
_ALLOWED_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_calc_eval(expr: str):
    """Safely evaluate a basic arithmetic expression (no names/calls/attributes)."""
    if expr is None:
        raise ValueError("empty")
    expr = str(expr).strip()
    if not expr:
        raise ValueError("empty")
    # allow only characters produced by the calculator UI/normal arithmetic
    if not re.fullmatch(r"[0-9+\-*/%.()\s]+", expr):
        raise ValueError("invalid characters")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Num):  # pragma: no cover (py<3.8 compat)
            return node.n
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY_OPS:
            return _ALLOWED_UNARY_OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BIN_OPS:
            left = _eval(node.left)
            right = _eval(node.right)
            # avoid absurd exponentiation
            if isinstance(node.op, ast.Pow) and abs(float(right)) > 100:
                raise ValueError("exponent too large")
            return _ALLOWED_BIN_OPS[type(node.op)](left, right)
        raise ValueError("unsupported expression")

    tree = ast.parse(expr, mode="eval")
    return _eval(tree)


@l313l.on(admin_cmd(pattern="حاسبة(?:\s|$)([\s\S]*)"))
async def icalc(e):
    if getattr(e.client, "_bot", False):
        return await e.reply(
            "**الحاسبة العلمية لـ T3rmx UserBot\n@t3rmx_official**", buttons=lst
        )
    results = await e.client.inline_query(Config.TG_BOT_USERNAME, "calc")
    await results[0].click(e.chat_id, silent=True, hide_via=True)
    await e.delete()


@l313l.tgbot.on(InlineQuery)
async def inlinecalc(event):
    query_user_id = event.query.user_id
    query = event.text
    string = query.lower()
    if (
        query_user_id == Config.OWNER_ID or query_user_id in Config.SUDO_USERS
    ) and string == "calc":
        event.builder
        calc = event.builder.article(
            "Calc", text="**الحاسبة العلمية لـ T3rmx UserBot\n@t3rmx_official**", buttons=lst
        )
        await event.answer([calc])


# 𝗧𝗲𝗹𝗲𝗚𝗿𝗮𝗠 : @t3rmx_official  ~ @vvsks
@l313l.tgbot.on(CallbackQuery(data=re.compile(b"calc(.*)")))
@check_owner
async def _(e):  # sourcery no-metrics
    x = (e.data_match.group(1)).decode()
    user = e.query.user_id
    get = None
    if x == "AC":
        if CALC.get(user):
            CALC.pop(user)
        await e.edit(
            "**الحاسبة العلمية لـ T3rmx UserBot\n@t3rmx_official**",
            buttons=[Button.inline("افتح مره اخرى", data="recalc")],
        )
    elif x == "C":
        if CALC.get(user):
            CALC.pop(user)
        await e.answer("تم الحذف")
    elif x == "⌫":
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: get[:-1]})
            await e.answer(str(get[:-1]))
    elif x == "%":
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: get + "/100"})
            await e.answer(str(get + "/100"))
    elif x == "÷":
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: get + "/"})
            await e.answer(str(get + "/"))
    elif x == "x":
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: get + "*"})
            await e.answer(str(get + "*"))
    elif x == "=":
        if CALC.get(user):
            get = CALC[user]
        if get:
            if get.endswith(("*", ".", "/", "-", "+")):
                get = get[:-1]
            try:
                out = _safe_calc_eval(get)
                num = float(out)
                await e.answer(f"▾∮ الجـواب : {num}", cache_time=0, alert=True)
            except BaseException:
                CALC.pop(user)
                await e.answer("خـطأ", cache_time=0, alert=True)
        await e.answer("غير معروف")
    else:
        if CALC.get(user):
            get = CALC[user]
        if get:
            CALC.update({user: get + x})
            return await e.answer(str(get + x))
        CALC.update({user: x})
        await e.answer(str(x))


# 𝗧𝗲𝗹𝗲𝗚𝗿𝗮𝗠 : @t3rmx_official  ~ @vvsks
@l313l.tgbot.on(CallbackQuery(data=re.compile(b"recalc")))
@check_owner
async def _(e):
    m = [
        "AC",
        "C",
        "⌫",
        "%",
        "7",
        "8",
        "9",
        "+",
        "4",
        "5",
        "6",
        "-",
        "1",
        "2",
        "3",
        "x",
        "00",
        "0",
        ".",
        "÷",
    ]
    tultd = [Button.inline(f"{x}", data=f"calc{x}") for x in m]
    lst = list(zip(tultd[::4], tultd[1::4], tultd[2::4], tultd[3::4]))
    lst.append([Button.inline("=", data="calc=")])
    await e.edit("**الحاسبة العلمية لـ T3rmx UserBot\n@t3rmx_official**", buttons=lst)

CMD_HELP.update(
    {"الحسابة": ".حاسبة" "\n فقط اكتب الامر لعرض حاسبة علميه تحتاج الى تفعيل وضع الانلاين اولا\n\n"}
)
