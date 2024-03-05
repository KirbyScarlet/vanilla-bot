#

from nonebot.adapters import Event
from typing import TypeAlias

from .es import es_cli

OCR_RESULT: TypeAlias = list[str]

async def text_search_image(event: Event, text: str, index="qqimage-metadata") -> OCR_RESULT:
    res = await es_cli.search(
        index = index,
        query = {
            "match_phrase": {
                "ocr": text
            }
        }
    )
    if res:
        return [x["_source"]["filepath"] for x in res["hits"]["hits"]]
    else:
        return []