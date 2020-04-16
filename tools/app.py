import json

from mirai import Mirai, Group, MessageChain, Member, Plain, At, Source
from core.config import conf
# from sympy import sympify
from core.helpers import wget, CommandParser


"""def ca(lam: str):
    if lam.find("0x") != -1:
        return "你平时用16进制算数的吗？"
    try:
        return str(sympify(lam))
    except Exception as e:
        return str(e)"""


async def ping(app: Mirai, group: Group):
    await app.sendGroupMessage(group, [Plain("pong!")])
    return True


"""async def calculator(app: Mirai, group: Group, message: MessageChain, member: Member):
    await app.sendGroupMessage(group, [At(member.id), Plain(ca(message.toString()[3:]))])
    return True"""


async def quote(app: Mirai, group: Group, message: MessageChain, member: Member, source: Source):
    if message.toString().find("骂我") != -1:
        await app.sendGroupMessage(group, [At(member.id),
                                           Plain((await wget("https://nmsl.shadiao.app/api.php?lang=zh_cn"))[1])],
                                   quoteSource=source)
        return True


async def about(app: Mirai, group: Group, member: Member):
    await app.sendGroupMessage(group, [At(member.id),
                                       Plain(f"从启动到现在，共处理{conf.get('storage', 'total_handle')}条信息")])

async def test(app: Mirai, group: Group, message: MessageChain):
    xd = CommandParser(message).parse_raw()
    return await app.sendGroupMessage(group, [Plain(json.dumps(xd))])

export = {
    "active": [quote],
    "command": {
        "ping": ping,
        #"cu": calculator,
        "count": about,
        "test": test
    }
}
