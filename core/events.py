from mirai import Mirai, Member, Group, MessageChain, Source, MemberMuteEvent, Plain, At, BotJoinGroupEvent
from .helpers import run_queue, run_command
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
        msg = message.toString()
        if msg.find(basic["command_head"]) == 0:
            if member.id not in conf.get("banner", "qq_id"):
                await run_command(message, manager.command, data_pack)
        else:
            await run_queue(manager.active, data_pack)
    else:
        await run_queue(manager.inactive, data_pack)


@app.receiver("MemberMuteEvent")
async def mute_event(app: Mirai, event: MemberMuteEvent):
    if event.member.group.id not in active_group:
        return
    await app.sendGroupMessage(event.member.group.id, [
        At(event.member.id),
        Plain("喝下了管理的红茶，睡了过去")
    ])


@app.receiver("BotJoinGroupEvent")
async def join_event(app: Mirai, event: BotJoinGroupEvent):
    if event.group.id not in conf.get("banner", "group_id"):
        await app.sendGroupMessage(event.group.id, [
            Plain("呃，好像被拉进来了\n"),
            Plain("请输入!cs来激活浩二（一次就够")
        ])

