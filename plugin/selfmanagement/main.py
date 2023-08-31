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
from ..minio.config import minio_config

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
    if (event.get_event_name() == "message_sent") and event.raw_message.startswith(self_management_config.self_management_prefix):
        event_json = event.dict()
        event_json["post_type"] = "message"
        event_json["to_me"] = True
        state["convert"] = True

        new_event = MessageEventv11.parse_obj(event_json)
        asyncio.create_task(bot.handle_event(new_event))

PREFIX = self_management_config.self_management_prefix
MINIO_URL = (("https://" if minio_config.minio_secure else "http://") +
             minio_config.minio_hosts+"/" +
             minio_config.minio_image_bucket_name+"/")


async def is_self_message(bot: Botv11, event: Eventv11, state: T_State):
    if event.get_user_id() == bot.self_id:
        return True

status = on_command(PREFIX+"test", rule=is_self_message)


@status.handle()
async def handle_selftest(bot: Bot, event: Event, state: T_State):
    await status.finish("test02")

find_image = on_command(PREFIX+"image", rule=is_self_message)


@find_image.handle()
async def handle_find_image(bot: Bot, event: Event, state: T_State, msg: Messagev11 = CommandArg()):
    if msg.extract_plain_text() == "":
        await find_image.finish("{{help document}}")
    query_body = {
        "bool": {
            "must": [],
            "filter": [],
            "should": [],
            "must_not": []
        }
    }
    for w in msg.extract_plain_text().split():
        if w:
            query_body["bool"]["filter"].append({"match_phrase": {"ocr": w}})
    if query_body["bool"]["filter"]:
        res = await es_cli.search(
            index=[minio_config.minio_es_ocr_indice+"*"],
            query=query_body)
        if hits := res["hits"]["hits"]:
            hits.sort(key=lambda x: len(x["_source"]["ocr"]))
            imgurl = hits[0]["_id"]
            filename = await es_cli.search(
                index=minio_config.minio_es_image_metadata_indice.format(version="*"),
                query={"ids":{"values":[imgurl]}})
            nonebot.logger.debug("imgurl: "+MINIO_URL+filename["hits"]["hits"][0]["_source"]["localfile_path"])
            imgresponse = await httpxclient.get(MINIO_URL+filename["hits"]["hits"][0]["_source"]["localfile_path"])
            imgbytes = await imgresponse.aread()
            print(MINIO_URL+imgurl)
            resmsg = MessageSegmentv11.image(file=imgbytes)
            await find_image.finish(resmsg)
    await find_image.finish("not found")

self_plugin = on_command(PREFIX+"plugin", rule=is_self_message)


@self_plugin.handle()
async def handle_self_plugin(bot: Bot, event: Eventv11, state: T_State):
    event_json = event.dict()
