#

import nonebot
from nonebot import on_command, on_message
from nonebot.rule import startswith

from nonebot.adapters import Bot, Event
from nonebot.params import CommandArg

try:
    from nonebot.adapters.onebot.v11 import Bot as Botv11
    from nonebot.adapters.onebot.v11 import Event as Eventv11
    from nonebot.adapters.onebot.v11 import MessageEvent as MessageEventv11
    from nonebot.adapters.onebot.v11 import Message as Messagev11
    from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegmentv11
    from nonebot.adapters.onebot.v12 import Bot as Botv12
    from nonebot.adapters.onebot.v12 import Event as Eventv12
except ImportError:
    pass
    # Botv11 = None
    # Botv12 = None
    # Eventv11 = None
    # Eventv12 = None

from nonebot.typing import T_State
from nonebot.message import event_preprocessor

from aiohttp import ClientSession
from httpx import AsyncClient

import psutil

import asyncio

from .config import self_management_config

from ..elasticsearch import es_cli
from ..elasticsearch.config import es_config
from ..minio import minio_cli
miniosession = ClientSession()
httpxclient = AsyncClient()

# 该方案似乎不管用，但是先留着
#
# async def onebotv11_event_convert(bot: Botv11, event: Eventv11):
#     if event.get_event_name() == "message_sent":
#         event_json = event.dict()
#         event_json["post_type"] = "message"
#         event_json["to_me"] = False
#     
#         new_event = Eventv11.parse_obj(event_json)
#
#         asyncio.create_task(bot.handle_event(new_event))
#
# async def onebotv12_event_convert(bot: Botv12, event: Eventv12):
#     pass
#
# event_converter = {
#     Eventv11: onebotv11_event_convert,
#     Eventv12: onebotv12_event_convert,
#     }
#
# async def default_converter(*args, **kwargs):
#     pass

@event_preprocessor
async def self_management(bot: Botv11, event: Eventv11, state: T_State):
    if event.get_event_name() == "message_sent":
        event_json = event.dict()
        event_json["post_type"] = "message"
        event_json["to_me"] = True
        state["convert"] = True
  
        new_event = MessageEventv11.parse_obj(event_json)
        asyncio.create_task(bot.handle_event(new_event))

PREFIX = self_management_config.self_management_prefix

async def is_self_message(bot: Botv11, event: Eventv11, state: T_State):
    if event.get_user_id() == bot.self_id:
        return True
    
status = on_command(PREFIX+"test", rule=is_self_message)

@status.handle()
async def handle_selftest(bot: Bot, event: Event, state: T_State):
    await status.finish("test02")

find_image = on_command(PREFIX+"image", rule=is_self_message)

QUERY_BODY = {
  "bool": {
    "minimum_should_match": 1,
    "should": [
    #   {
    #     "match_phrase": {
    #       "ocr": "抛个"
    #     }
    #   },
    #   {
    #     "match_phrase": {
    #       "ocr": "媚眼"
    #     }
    #   }
    ]
  }
}

@find_image.handle()
async def handle_find_image(bot: Bot, event: Event, state: T_State, msg: Messagev11 = CommandArg()):
    if msg.extract_plain_text() == "":
        await find_image.finish("{{help document}}")
    query_body = {"bool":{"minimum_should_match":1,"should":[]}}
    for w in msg.extract_plain_text().split():
        if w:
            query_body["bool"]["should"].append({"match_phrase": {"ocr": w}})
    if query_body["bool"]["should"]:
        res = await es_cli.search(index=f"qqimage-metadata-{bot.self_id}-dev0.0.5", query=query_body)
        if hits := res["hits"]["hits"]:
            hits.sort(key=lambda x: len(x["_source"]["ocr"]))
            imgurl = hits[0]["_source"]["filepath"]
            print(imgurl)
            imgresponse = await httpxclient.get("http://127.0.0.1:9000/qqimage/"+imgurl)
            imgbytes = await imgresponse.aread()
            resmsg = MessageSegmentv11.image(file=imgbytes)
            await find_image.finish(resmsg)
    await find_image.finish("not found")
            

