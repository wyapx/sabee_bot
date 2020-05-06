import json
import re
import asyncio
import aiohttp
import importlib
from functools import partial
from mirai import MessageChain
from typing import List, Tuple
from .config import conf


class CommandParser:
    def __init__(self, message: MessageChain):
        sp = re.split(r"\s+", message.toString()[len(conf.get("basic", "command_head")):], 1)
        if len(sp) == 1:
            self.command, self.arg = sp[0], ""
        else:
            self.command, self.arg = sp
        self._msg = message

    def cmp(self, source: str):
        return self.command == source

    def _parse(self, count: int) -> List[Tuple[str, str]]:
        if not self.arg:
            return []
        result = []
        cm = 2
        sp = False
        if count:
            count -= 1
        for s in re.split(r"\s+", self.arg, count):
            match = re.match(r"(.*)::(.*)", s[1:-1])
            if match:
                cm += 1
                sp = True
                if match.group(1) in ("At", "Face"):
                    result.append((match.group(1), int(match.group(2).split("=", 1)[1])))
                else:
                    result.append(match.groups())
            else:
                if sp:
                    sp = False
                    cm += 1
                try:
                    result.append(("Int", int(s)))
                except ValueError:
                    result.append(("String", s))
        if len(self._msg) != cm:
            raise ValueError(f"{len(self._msg)} object need, but {cm} got")
        return result

    def parse_with_valid(self, typ: (list, tuple), ignore_type=False) -> (str, List[List], None):
        raw = self._parse(len(typ))
        if not raw:
            return None
        if len(raw) != len(typ):
            return "参数不足"
        for c, (t1, t2) in enumerate(zip(raw, typ)):
            if t1[0] not in t2:
                return f"参数{c}处应为{t2}，但获得了{t1[0]}"
        return raw

    def parse_raw(self, count=-1) -> list:
        return self._parse(count)


async def auto_param(func, attr):
    need_attr = func.__annotations__
    inn = {}
    for k, v in need_attr.items():
        inn[k] = attr[v]
    return await func(**inn)


async def run_queue(q: list, kwargs: dict):
    for func in q:
        if await auto_param(func, kwargs):
            break


async def run_command(msg: MessageChain, d: dict, kwargs: dict):
    cp = CommandParser(msg)
    kwargs[CommandParser] = cp
    if cp.command in d:
        await auto_param(d[cp.command], kwargs)


class Qname_pool:
    def __init__(self):
        self._cache = {}

    async def query(self, qid: int) -> str:
        if qid in self._cache:
            return self._cache.get(qid)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(f"https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?g_tk=&uins={qid}") as req:
                data = await req.read()
                status = req.status
        if status != 200:
            print(data)
        js = json.loads(data[17:-1].decode("gbk"))
        if str(qid) in js:
            self._cache[qid] = js[str(qid)][6]
            return js[str(qid)][6]
        return str(qid)

    def flush(self):
        self._cache.clear()


def run_with_wrapper(func, *args, **kwargs):
    exe = func(*args, **kwargs)
    if asyncio.iscoroutine(exe):
        asyncio.ensure_future(exe)


def interval(delay, func, *args, **kwargs):
    run_with_wrapper(func, *args, **kwargs)
    asyncio.get_event_loop().call_later(delay, partial(interval, delay, func, *args, **kwargs))


def call_later(delay, callback, *args, **kwargs):
    return asyncio.get_event_loop().call_later(delay, partial(run_with_wrapper, callback, *args, **kwargs))


# https://www.cntofu.com/book/127/aiohttp%E6%96%87%E6%A1%A3/ClientReference.md
async def wget(url: str, headers=None, typ="plain"):
    if not headers:
        headers = {}
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(family=2, verify_ssl=False)) as session:
        async with session.get(url, headers=headers) as res:
            if typ == "plain":
                return res.status, await res.read()
            elif typ == "json":
                return res.status, await res.json()
            else:
                raise ValueError("Unknown type:", typ)


def reload_modules(modules: list):
    for x in modules:
        importlib.reload(x)


def strQ2B(ustring):
    """
    全角转半角
    From https://www.cnblogs.com/kaituorensheng/p/3554571.html
    """
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:
            inside_code = 32
        elif 65281 <= inside_code <= 65374:
            inside_code -= 65248
        rstring += chr(inside_code)
    return rstring


qname = Qname_pool()
