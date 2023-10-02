# 自助找图

from nonebot import require
from nonebot import Bot
from nonebot.adapters import Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message as Messagev11
from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegmentv11
from nonebot.params import CommandArg
from nonebot.log import logger
from nonebot.rule import ArgumentParser
from typing import Mapping, Union
from PIL import Image

from httpx import AsyncClient

httpxclient = AsyncClient(timeout=30.0)

try:
    require("selfmanagement")
    from ..selfmanagement import on_self_shell_command
    from ..selfmanagement import is_self_message
    from ..selfmanagement import on_self_command
except:
    on_self_shell_command = None

try:
    require("elasticsearch")
    from ..elasticsearch import es_cli
except RuntimeError:
    logger.error("请检查nonebot_plugin_elasticsearch是否正确安装")

from .config import minio_config

search_image_args = ArgumentParser()


find_image = on_self_command("image")

MINIO_URL = (("https://" if minio_config.minio_secure else "http://") +
             minio_config.minio_hosts+"/" +
             minio_config.minio_image_bucket_name+"/")

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
            query=query_body,
            sort=[{"_script": {"script": "Math.random()","type": "number","order": "asc"}}],
            size=10
        )
        if hits := res["hits"]["hits"]:
            hits.sort(key=lambda x: len(x["_source"]["ocr"]))
            imgurl = hits[0]["_id"]
            filename = await es_cli.search(
                index=minio_config.minio_es_image_metadata_indice.format(version="*"),
                query={"ids":{"values":[imgurl]}},
                )
            logger.debug("imgurl: "+MINIO_URL+filename["hits"]["hits"][0]["_source"]["localfile_path"])
            imgresponse = await httpxclient.get(MINIO_URL+filename["hits"]["hits"][0]["_source"]["localfile_path"])
            imgbytes = await imgresponse.aread()
            print(MINIO_URL+imgurl)
            resmsg = MessageSegmentv11.image(file=imgbytes)
            await find_image.finish(resmsg)
    await find_image.finish("not found")

async def search_image_from_text(text: str, cognitive: bool = False) -> Mapping:
    query_body = {
        "bool": {
            "must": [],
            "filter": [],
            "should": [],
            "must_not": []
        }
    }
    for w in text.split():
        if w:
            query_body["bool"]["filter"].append({"match_phrase": {"ocr": w}})
    if query_body["bool"]["filter"]:
        res = await es_cli.search(
            index=[minio_config.minio_es_ocr_indice+"*"],
            query=query_body,
            sort=[{"_script": {"script": "Math.random()","type": "number","order": "asc"}}],
            size=10
        )
        if hits := res["hits"]["hits"]:
            hits.sort(key=lambda x: len(x["_source"]["ocr"]))
            imgurl = hits[0]["_id"]
            filename = await es_cli.search(
                index=minio_config.minio_es_image_metadata_indice.format(version="*"),
                query={"ids":{"values":[imgurl]}},
                )
            logger.debug("imgurl: "+MINIO_URL+filename["hits"]["hits"][0]["_source"]["localfile_path"])
            try:
                imgresponse = await httpxclient.get(MINIO_URL+filename["hits"]["hits"][0]["_source"]["localfile_path"])
                imgbytes = await imgresponse.aread()
            except:
                imgbytes = b""
            return imgbytes
        
KNN_QUERY = {
    "field": "vit",
    "k": 20,
    "num_candidates": 10000,
    "query_vector": []
}
VIT_INDEX = minio_config.minio_es_vit_indice.format(version="*")

async def search_image_from_knn(
    image: Union[str, Image.Image, bytes], 
    k: int = 20, 
    num_candidates: int = 10000
) -> Mapping:
    pass