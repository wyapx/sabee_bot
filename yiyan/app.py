import aiohttp
from mirai import Mirai, Group, Member, MessageChain, At, Plain
from core.config import conf


async def custom_trigger(app: Mirai, group: Group, member: Member, message: MessageChain):
    if member.id in conf.get("banner", "qq_id"):
        return True
    elif message.toString().find("一言") == -1:
        return False
    async with aiohttp.request("GET", "https://v1.alapi.cn/api/soul") as req:
        data = await req.json()
    if data["code"] != 200:
        raise ValueError("Status Error:"+str(data["code"]+":"+data["msg"]))
    return await app.sendGroupMessage(group, [At(member.id), Plain(data["data"]["title"])])

export = {
    "active": [custom_trigger]
}