import json
from mirai import At, Plain, Member, Group, Mirai, MessageChain
from core.helpers import call_later, CommandParser
from core.config import conf
from core.loader import manager


async def set_active(app: Mirai, group: Group, member: Member, message: MessageChain):
    if message.toString().find(conf.get("basic", "command_head") + "cs") == 0:
        if group.id in conf.get("banner", "group_id"):
            return
        conf.get("active", "group_id").append(group.id)
        msg = await app.sendGroupMessage(group, [At(member.id), Plain("启用")])
        call_later(10, app.revokeMessage, msg.messageId)


async def set_inactive(app: Mirai, group: Group, member: Member):
    conf.get("active", "group_id").remove(group.id)
    msg = await app.sendGroupMessage(group, [At(member.id), Plain("禁用")])
    call_later(10, app.revokeMessage, msg.messageId)


async def active_list(app: Mirai, group: Group, member: Member):
    if member.id not in conf.get("permission", "operator"):
        await app.sendGroupMessage(group, [At(member.id), Plain("权限不足")])
        return
    await app.sendGroupMessage(group, [At(member.id), Plain("已激活群组："),
                                       Plain(json.dumps(conf.get("active", "group_id"), indent=2))])


async def set_banner(app: Mirai, group: Group, member: Member, cp: CommandParser):
    if member.id in conf.get("permission", "operator"):
        pa = cp.parse_with_valid(["String", ("Int", "At")])
        if isinstance(pa, str):
            return await app.sendGroupMessage(group, [At(member.id), Plain(pa)])
        elif not pa:
            return await app.sendGroupMessage(group, [At(member.id), Plain("参数不能为空")])
        if pa[0][1] == "group":
            target = "group_id"
        elif pa[0][1] == "member":
            target = "qq_id"
        else:
            return await app.sendGroupMessage(group, [At(member.id), Plain("类型错误")])
        if pa[1][1] in conf.get("banner", target):
            return await app.sendGroupMessage(group, [At(member.id), Plain("已经在清单里面了")])
        conf.get("banner", target).append(pa[1][1])
        if group.id in conf.get("active", "group_id"):
            conf.get("active", "group_id").remove(group.id)
        await app.sendGroupMessage(group, [At(member.id), Plain(f"已经将{pa[1][1]}拉入清单")])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("权限不足")])


async def rm_banner(app: Mirai, group: Group, member: Member, cp: CommandParser):
    if member.id in conf.get("permission", "operator"):
        pa = cp.parse_with_valid(["String", ("Int", "At")])
        if isinstance(pa, str):
            return await app.sendGroupMessage(group, [At(member.id), Plain(pa)])
        elif not pa:
            return await app.sendGroupMessage(group, [At(member.id), Plain("参数不能为空")])
        if pa[0][1] == "group":
            target = "group_id"
        elif pa[0][1] == "member":
            target = "qq_id"
        else:
            return await app.sendGroupMessage(group, [At(member.id), Plain("类型错误")])
        if pa[1][1] not in conf.get("banner", target):
            return await app.sendGroupMessage(group, [At(member.id), Plain("还不在清单里")])
        conf.get("banner", target).remove(pa[1][1])
        await app.sendGroupMessage(group, [At(member.id), Plain(f"移除{pa[1][1]}成功")])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("权限不足")])


async def reload_modules(app: Mirai, group: Group, member: Member):
    if member.id in conf.get("permission", "operator"):
        from core.loader import manager
        error = manager.reload_modules()
        await app.sendGroupMessage(group, [At(member.id), Plain("重载模块成功")])
        if error:
            await app.sendGroupMessage(group, [Plain("但在重载时，发生了一些错误：\n"), *[Plain(str(e) + "\n") for e in error]])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("权限不足")])


async def add_modules(app: Mirai, group: Group, member: Member, message: MessageChain):
    if member.id in conf.get("permission", "operator"):
        mp = message.toString().split(" ", 1)[1]
        conf.get("plugins", "active").append(mp)
        await app.sendGroupMessage(group, [At(member.id), Plain("增加模块成功，将在下次重载生效")])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("权限不足")])


async def rm_modules(app: Mirai, group: Group, member: Member, message: MessageChain):
    if member.id in conf.get("permission", "operator"):
        mp = message.toString().split(" ", 1)[1]
        conf.get("plugins", "active").remove(mp)
        await app.sendGroupMessage(group, [At(member.id), Plain("删除模块成功，将在下次重载生效")])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("权限不足")])


async def get_list(app: Mirai, group: Group, member: Member):
    if member.id in conf.get("permission", "operator"):
        await app.sendGroupMessage(group, [At(member.id), Plain("模块列表："),
                                           Plain(json.dumps(conf.get("plugins", "active"), indent=2))])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("权限不足")])


async def edit_config(app: Mirai, group: Group, member: Member, message: MessageChain):
    if member.id in conf.get("permission", "operator"):
        try:
            _, segment, block, method, value = message.toString().split(" ")
        except ValueError:
            await app.sendGroupMessage(group, [At(member.id), Plain("参数不足")])
            return
        try:
            data = json.loads(value)
        except json.decoder.JSONDecodeError:
            data = value
        try:
            if method == "replace":
                conf.set(segment, block, data)
            elif method == "update":
                c = conf.get(segment, block)
                if isinstance(c, (list, tuple)):
                    c.append(data)
                elif isinstance(c, dict):
                    c.update(data)
            else:
                await app.sendGroupMessage(group, [At(member.id), Plain(f"未知方法:{method}")])
                return
            await app.sendGroupMessage(group, [At(member.id), Plain("修改成功")])
        except ValueError as e:
            await app.sendGroupMessage(group, [At(member.id), Plain(f"修改配置时发生错误:\n{e}")])


async def save_config(app: Mirai, group: Group, member: Member):
    if member.id in conf.get("permission", "operator"):
        conf.save()
        await app.sendGroupMessage(group, [At(member.id), Plain("保存配置成功")])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("权限不足")])


async def edit_nick(app: Mirai, group: Group, member: Member, cp: CommandParser):
    if member.id in conf.get("permission", "operator"):
        pa = cp.parse_with_valid([("Int", "String")])
        if isinstance(pa, str):
            return await app.sendGroupMessage(group, [At(member.id), Plain(pa)])
        elif not pa:
            return await app.sendGroupMessage(group, [At(member.id), Plain("参数不能为空")])
        info = await app.botMemberInfo(group)
        info.modify({"name": pa[0][1]})
        await app.changeMemberInfo(group, app.qq, info)
        await app.sendGroupMessage(group, [At(member.id), Plain("修改成功")])
    else:
        await app.sendGroupMessage(group, [At(member.id), Plain("权限不足")])


async def get_command_list(app: Mirai, group: Group, member: Member):
    await app.sendGroupMessage(group, [At(member.id), Plain("命令列表:"),
                                       Plain(json.dumps(list(manager.command.keys()), indent=2))])


export = {
    "command": {
        "cl": get_command_list,
        "cs": set_inactive,
        "sb": set_banner,
        "rb": rm_banner,
        "al": active_list,
        "ec": edit_config,
        "cn": edit_nick,
        "reload": reload_modules,
        "add": add_modules,
        "remove": rm_modules,
        "save": save_config,
        "list": get_list
    },
    "inactive": [set_active]
}
