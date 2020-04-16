import os
import time
from datetime import datetime
from core.helpers import CommandParser, wget
from mirai import Mirai, Group, Member, Plain, At, MessageChain, Image
from .compoments import Parser
from .spider import kisssub

# code from https://github.com/DaRealFreak/saucenao/blob/master/saucenao/saucenao.py
DataBase = {
    0: "HMagazines",
    2: "HGameCG",
    3: "DoujinshiDB",
    5: "PixivImages",
    8: "NicoNicoSeiga",
    9: "Danbooru",
    10: "DrawrImages",
    11: "NijieImages",
    12: "YandeRe",
    15: "Shutterstock",
    16: "FAKKU",
    18: "HMisc",
    19: "TwoDMarket",
    20: "MediBang",
    21: "Anime",
    22: "HAnime",
    23: "Movies",
    24: "Shows",
    25: "Gelbooru",
    26: "Konachan",
    27: "SankakuChannel",
    28: "AnimePicturesNet",
    29: "E621Net",
    30: "IdolComplex",
    31: "BcyNetIllust",
    32: "BcyNetCosplay",
    33: "PortalGraphicsNet",
    34: "DeviantArt",
    35: "PawooNet",
    36: "MadokamiManga",
    37: "MangaDex",
    999: "All"
}
nt = 0
l = {}

ROOT = "/root/NullcatServer/static/img/"
async def search_image(app: Mirai, group: Group, member: Member, cp: CommandParser, message: MessageChain):
    pa = cp.parse_with_valid(["[Image"])
    if isinstance(pa, str):
        return await app.sendGroupMessage(group, [At(member.id), Plain(pa)])
    elif not pa:
        return await app.sendGroupMessage(group, [At(member.id), Plain("参数不能为空")])
    img = message.getFirstComponent(Image)
    with open(f"{ROOT}{str(img.imageId)}.jpg", "wb") as f:
        f.write((await img.toBytes()).getvalue())
    try:
        _, raw = await wget(f"https://saucenao.com/search.php?output_type=2&testmode=0&numres=4&url=https://www.pixivdl.net/static/img/{str(img.imageId)}.jpg")
    finally:
        os.remove(f"{ROOT}{str(img.imageId)}.jpg")
    data = Parser.parse_raw(raw)
    if data.header.status != 0:
        print(raw)
        return await app.sendGroupMessage(group, [At(member.id), Plain(f"发生错误：status: {data.header.status}")])
    result = ["查询结果：\n", f"作品类型：{DataBase.get(data.results[0].header.index_id)}\n",
              f"准确度：{data.results[0].header.similarity}%\n", f"剩余次数：{data.header.long_remaining}\n"]
    if data.results[0].header.index_id in (21, 22):  # Anime, HAnime
        result.append(f"作品名：{data.results[0].data.source}\n")
        result.append(f"年份：{data.results[0].data.year}\n")
        result.append(f"目标位置：第{data.results[0].data.part}集，{data.results[0].data.est_time}\n")
    elif data.results[0].header.index_id in (5, 31, 33, 34):  # Image
        result.append(f"标题：{data.results[0].data.title}\n")
    result.append(f"更多信息：{data.results[0].data.ext_urls[0]}")
    await app.sendGroupMessage(group, [At(member.id), *(Plain(msg) for msg in result)])

# 上面的是以图查图

async def bangumi_push(app: Mirai, member: Member, group: Group, cp: CommandParser):
    global nt
    pa = cp.parse_with_valid(["Int"])
    if isinstance(pa, str):
        return await app.sendGroupMessage(group, [At(member.id), Plain(pa)])
    elif not pa:
        week = datetime.today().isoweekday()
    else:
        week = pa[0][1]
    if nt+3600 < time.time():
        l.clear()
        l.update(await kisssub())
        if l:
            nt = time.time()
    print(l)
    now = l[str(week)]
    await app.sendGroupMessage(group, [At(member.id), Plain(f"{now[0]['utime'][3]}的番剧列表：\n"),
                                       *(Plain(f"{b['name']}：{b['tag']}\n") for b in now)])

export = {
    "command": {"query": search_image, "bangumi": bangumi_push}
}