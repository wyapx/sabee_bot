from mirai import Mirai, Group, Member, At, Plain
from core.helpers import CommandParser
from core.config import conf

admin = conf.get("permission", "operator")

cache_msg = {}

async def repeat(app: Mirai, group: Group, member: Member, cp: CommandParser):
    args = cp.parse_with_valid(("Int", ("Int", "String")))  # count, content
    if isinstance(args, str):
        return await app.sendGroupMessage(group, [At(member.id), Plain(args)])
    if member.id not in admin and args[0][1] > 3:
        return await app.sendGroupMessage(group, [At(member.id), Plain("次数不能大于3")])
    for _ in range(args[0][1]):
        await app.sendGroupMessage(group, [Plain(str(args[1][1]))])

export = {
    "command": {"rp": repeat}
}
