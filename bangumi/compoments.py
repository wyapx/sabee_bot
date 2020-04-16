from pydantic import BaseModel
from typing import List


# https://saucenao.com/search.php?output_type=2&testmode=0&numres=10&url=http://i0.hdslb.com/bfs/archive/469c23e1f352030fafd4ecccbc87bd686724640f.jpg
class Header(BaseModel):
    user_id: int
    account_type: int
    short_limit: str
    long_limit: str
    long_remaining: int
    short_remaining: int
    status: int
    results_requested: int
    index: dict
    search_depth: str
    minimum_similarity: float
    results_returned: int


class res_Header(BaseModel):
    similarity: str
    index_id: int
    index_name: str


class res_Data(BaseModel):
    ext_urls: List[str] = ["暂无信息"]

    source: str = "None"
    anidb_aid: int = 0
    part: str = "None"
    year: str = "None"
    est_time: str = "None"

    title: str = "None"
    pixiv_id: int = 0


class res_block(BaseModel):
    header: res_Header
    data: res_Data


class Parser(BaseModel):
    header: Header
    results: List[res_block]
