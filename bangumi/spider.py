import re
import aiohttp
from bs4 import BeautifulSoup

Date = {
    "周一": 1,
    "周二": 2,
    "周三": 3,
    "周四": 4,
    "周五": 5,
    "周六": 6,
    "周日": 7
}


async def kisssub():
    async with aiohttp.request("GET", "http://104.28.23.212/", headers={"Host": "www.kisssub.org"}) as req:
        x = await req.read()
    bs = BeautifulSoup(x.replace(b"\n", b""), "lxml")
    xd = list(bs.select_one(".tbody"))[2:-5]
    rl = []
    for x in xd:
        if x != " ":
            rl.append(x)
    count = 0
    result = {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": []}
    for ro in rl:
        if count == 0:
            now = result["7"]
        else:
            now = result[str(count)]
        for e in ro.contents[3].children:
            if e != " ":
                if "data-balloon" in e.attrs:
                    parse = re.search(r"[→\s]?(\d{4})年(\d{1,2})月(\d{1,2})日起 [每]?(.{2})(\d{1,2}):(\d{2})",
                                      e.attrs["data-balloon"])
                    if not parse:
                        now.append({"name": e.text[20:], "tag": e.attrs["data-balloon"], "utime": None})
                    else:
                        now.append({"name": e.text[20:], "tag": e.attrs["data-balloon"][0:parse.span()[0]],
                                    "utime": parse.groups()})
        count += 1
    return result


if __name__ == '__main__':
    import asyncio

    asyncio.run(kisssub())
