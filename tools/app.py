import json
import random

from mirai import Mirai, Group, MessageChain, Member, Plain, At, Source
from mirai.event.message.components import Json, Poke, FlashImage

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
    await app.sendGroupMessage(group, [Plain("爪巴!")])
    return True


"""async def calculator(app: Mirai, group: Group, message: MessageChain, member: Member):
    await app.sendGroupMessage(group, [At(member.id), Plain(ca(message.toString()[3:]))])
    return True"""


async def quote(app: Mirai, group: Group, message: MessageChain, member: Member, source: Source):
    if message.toString().find("骂我") != -1:
        await app.sendGroupMessage(group, [At(member.id),
                                           Plain((await wget("https://nmsl.shadiao.app/api.php?lang=zh_cn?level=min"))[
                                                     1])],
                                   quoteSource=source)
        return True


async def testjson(app: Mirai, group: Group, member: Member):
    if member.id in conf.get("permission", "operator"):
        return await app.sendGroupMessage(group, Json(json={"app": "com.tencent.gamecenter.gameshare", "desc": "", "view": "noDataView", "ver": "0.0.0.0","prompt": "英雄分享：影流之主", "meta": {"shareData": {"scene": "SCENE_SHARE_VIDEO","jumpUrl": "https://url.cn/5VN4uaZ","type": "video", "url": "http:\/\/t.cn\/A6wslkFS"}},"config": {"forward": 1}}))
    else:
        return await app.sendGroupMessage(group, Plain("功能暂未开放"))

async def testpoke(app: Mirai, group: Group):
    return await app.sendGroupMessage(group, Poke(random.choice(["Poke", "ShowLove", "Like", "Heartbroken", "SixSixSix", "FangDaZhao"])))


async def about(app: Mirai, group: Group, member: Member):
    await app.sendGroupMessage(group, [At(member.id),
                                       Plain(f"从启动到现在，共处理{conf.get('storage', 'total_handle')}条信息")])


async def test(app: Mirai, group: Group, message: MessageChain):
    xd = CommandParser(message).parse_raw()
    return await app.sendGroupMessage(group, [Plain(json.dumps(xd))])

async def flashimage(app: Mirai, group: Group):
    await app.sendGroupMessage(group, Plain("这不是一张色图"))
    return await app.sendGroupMessage(group, [FlashImage.fromFileSystem("tools/setu.jpg")])

export = {
    "active": [quote],
    "command": {
        "ping": ping,
        # "cu": calculator,
        "count": about,
        "test": test,
        "json": testjson,
        "poke": testpoke,
        "setu": flashimage
    }
}
