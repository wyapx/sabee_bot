from mirai import Mirai, Member, Group, MessageChain, Source, MemberMuteEvent, Plain, BotJoinGroupEvent, \
    MemberUnmuteEvent, MemberJoinEvent, At
from .helpers import run_queue, run_command, strQ2B
from .config import conf
from .loader import manager

basic = conf.get("basic")
if not basic["auth_key"] or not basic["bind_qq"]:
    raise ValueError("auth_key or bind_qq not found, please check your configFile")
if basic["use_websocket"]:
    ws = "ws"
else:
    ws = ""
app = Mirai(f'mirai://{basic["host"]}:{basic["port"]}/{ws}?authKey={basic["auth_key"]}&qq={basic["bind_qq"]}')

if "total_handle" not in conf.get("storage"):
    conf.get("storage")["total_handle"] = 0
active_group = conf.get("active", "group_id")
storage = conf.get("storage")


@app.receiver("GroupMessage")
async def group_recv(app: Mirai, message: MessageChain, group: Group, member: Member, source: Source):
    data_pack = {Mirai: app, MessageChain: message, Group: group, Member: member, Source: source}
    if group.id in active_group:
        storage["total_handle"] += 1
        msg = strQ2B(message.toString())
        if msg.find(basic["command_head"]) == 0:
            if member.id not in conf.get("banner", "qq_id"):
                await run_command(message, manager.command, data_pack)
        else:
            await run_queue(manager.active, data_pack)
    else:
        await run_queue(manager.inactive, data_pack)

@app.receiver("MemberJoinEvent")
async def join_event(app: Mirai, event: MemberJoinEvent):
    if event.member.group.id not in active_group:
        return
    await app.sendGroupMessage(event.member.group.id, [At(event.member.id), Plain("你已经是群大佬了，快来和鸽子们聊天吧")])

@app.receiver("MemberMuteEvent")
async def mute_event(app: Mirai, event: MemberMuteEvent):
    if event.member.group.id not in active_group:
        return
    if not event.operator:
        return
    await app.sendGroupMessage(event.member.group.id, Plain(f"{event.member.memberName} 喝下红茶，睡了过去"))

@app.receiver("MemberUnmuteEvent")
async def unmute_event(app: Mirai, event: MemberUnmuteEvent):
    if event.member.group.id not in active_group:
        return
    await app.sendGroupMessage(event.member.group.id, Plain(f"{event.member.memberName} 被先辈叫醒了"))

@app.receiver("BotJoinGroupEvent")
async def join_event(event: BotJoinGroupEvent):
    if event.group.id not in conf.get("banner", "group_id"):
        conf.get("active", "group_id").append(event.group.id)
