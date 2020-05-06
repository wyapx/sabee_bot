import random
from core.helpers import CommandParser
from mirai import Mirai, Plain, Member, Group, At, Image, Source, JsonMessage
from .core import ChessControl

room = {}
bind = {}
state = {}


async def make(app: Mirai, group: Group, member: Member, cp: CommandParser):
    pa = cp.parse_with_valid(["Int"])
    if isinstance(pa, str):
        return await app.sendGroupMessage(group, [At(member.id), Plain(pa)])
    elif not pa:
        return await app.sendGroupMessage(group, [At(member.id), Plain("参数不能为空")])
    if pa[0][1] > 20:
        return await app.sendGroupMessage(group, [At(member.id), Plain("棋盘太大了")])
    elif pa[0][1] < 5:
        return await app.sendGroupMessage(group, [At(member.id), Plain("棋盘太小了")])
    elif member.id in state:
        return await app.sendGroupMessage(group, [At(member.id), Plain("你已经在一个房间里面了")])
    cc = ChessControl(pa[0][1]+2)  # 修正边界问题
    bind[member.id] = cc
    room[member.id] = [member.id]
    state[member.id] = member.id
    await app.sendGroupMessage(group, Plain(f'已经创建大小为{pa[0][1]}*{pa[0][1]}的棋盘\n输入"!cjoin {member.id}"即可加入'))

async def join(app: Mirai, group: Group, member: Member, cp: CommandParser):
    pa = cp.parse_with_valid(["Int"])
    if isinstance(pa, str):
        return await app.sendGroupMessage(group, [At(member.id), Plain(pa)])
    elif not pa:
        return await app.sendGroupMessage(group, [At(member.id), Plain("参数不能为空")])
    if pa[0][1] not in bind:
        return await app.sendGroupMessage(group, [At(member.id), Plain("没有找到这个房间")])
    elif member.id in bind:
        return await app.sendGroupMessage(group, [At(member.id), Plain("你不能加入自己的房间")])
    elif len(room[pa[0][1]]) > 1:
        return await app.sendGroupMessage(group, [At(member.id), Plain("已经开始了")])
    else:
        room[pa[0][1]].append(member.id)
        state[member.id] = state[pa[0][1]]
        await app.sendGroupMessage(group, [At(member.id), Plain("加入成功，若图片无法正常加载可输入!cget")])
    await app.sendGroupMessage(group, [At(pa[0][1]), Image.fromBytes(bind[state[member.id]].get_image()), Plain("输入!p x y来放置棋子")])

async def put(app: Mirai, group: Group, member: Member, source: Source, cp: CommandParser):
    pa = cp.parse_with_valid(["Int", "Int"])
    if isinstance(pa, str):
        return await app.sendGroupMessage(group, [At(member.id), Plain(pa)])
    elif not pa:
        return await app.sendGroupMessage(group, [At(member.id), Plain("参数不能为空")])
    if member.id not in state:
        return await app.sendGroupMessage(group, [At(member.id), Plain("你没有加入房间")])
    if room[state[member.id]][0] == member.id:
        if member.id in bind:
            code = bind[state[member.id]].put(pa[0][1], pa[1][1], -1)
        else:
            code = bind[state[member.id]].put(pa[0][1], pa[1][1], 1)
        if code == 1:
            await app.sendGroupMessage(group, [At(member.id), Plain("胜出\n"),
                                               Image.fromBytes(bind[state[member.id]].get_image())])
            for m in room[state[member.id]]:
                try:
                    state.pop(m)
                    room.pop(m)
                    bind.pop(m)
                except KeyError:
                    pass
        elif code == 0:
            await app.sendGroupMessage(group, [At(room[state[member.id]][1]), Plain("轮到你了"),
                                               Image.fromBytes(bind[state[member.id]].get_image())], quoteSource=source)
            room[state[member.id]].insert(0, room[state[member.id]].pop(1))
        elif code == -1:
            await app.sendGroupMessage(group, [At(member.id), Plain("这里已经有棋子了")])
        elif code == -2:
            await app.sendGroupMessage(group, [At(member.id), Plain("你放过界了")])
    else:
        return await app.sendGroupMessage(group, [At(member.id), Plain("还没有轮到你")])

async def left(app: Mirai, group: Group, member: Member):
    if member.id in room[state[member.id]]:
        for m in room[state[member.id]]:
            try:
                state.pop(m)
                room.pop(m)
                bind.pop(m)
            except KeyError:
                pass
        await app.sendGroupMessage(group, [At(member.id), Plain("已退出")])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("未找到你所处的房间")])

async def clear(app: Mirai, group: Group):
    room.clear()
    bind.clear()
    state.clear()
    await app.sendGroupMessage(group, Plain("强制清空完成"))

async def test():
    print(room, state, bind)

async def cget(app: Mirai, group: Group, member: Member):
    if member.id in room[state[member.id]]:
        await app.sendGroupMessage(group, [At(member.id),
                                           Image.fromBytes(bind[state[member.id]].get_image(quality=random.randint(90, 99)))])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("未找到你所处的房间")])

export = {
    "command": {
        "ccreate": make,
        "cjoin": join,
        "cget": cget,
        "p": put,
        "cexit": left,
        "clear": clear,
        "nmsl": test
    }
}