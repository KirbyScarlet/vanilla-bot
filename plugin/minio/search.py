# 自助找图

from nonebot import require
from nonebot import Bot
from nonebot.adapters import Event
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import MessageEvent as MessageEventv11
from nonebot.adapters.onebot.v11 import Message as Messagev11
from nonebot.adapters.onebot.v11 import Event as Eventv11
from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegmentv11
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.log import logger
from nonebot.rule import ArgumentParser
from typing import Mapping, Union
from PIL import Image
from argparse import Namespace

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
search_image_args.add_argument("tags", nargs="*", help="图片文字的关键字")
search_image_args.add_argument("-c", "--count", type=int, dest="count", default=1, help="指定图片数量")
search_image_args.add_argument("-n", "--ntags", nargs="*", dest="ntags", help="指定过滤关键词")
search_image_args.add_argument("-l", "--list", action="store_true", dest="list", default=False, help="仅输出文字信息")
search_image_args.add_argument("--wc", action="store_true", dest="wc", default=False, help="仅统计数据量")

search_image_args.add_argument("--knn", action="store_true", dest="knn", default=False, help="开启以图搜图")
search_image_args.add_argument("--knn-hnsw", action="store_true", dest="hnsw", default=True, help="开启以图搜图的hnsw搜索，此选项速度更快，准确度稍低")
search_image_args.add_argument("--knn-candidates", type=int, dest="candidates", default=10000, help="当使用hnsw搜索时，指定候选数量")
search_image_args.add_argument("--knn-threshold", type=float, dest="threshold", default=1.95, help="当不开启hnsw算法时，指定相似度")

SEARCH_IMAGE_ARGS_HELP = """\
"""
SEARCH_IMAGE_ARGS_HELP_KNN = """\
usage:
image --knn [--wc] [--knn-hnsw] [--knn-candidates=10000] [--knn-threshold] IMAGE | CQ:reply,Image
"""

find_image = on_self_shell_command("image", parser=search_image_args)

MINIO_URL = (("https://" if minio_config.minio_secure else "http://") +
             minio_config.minio_hosts+"/" +
             minio_config.minio_image_bucket_name+"/")

@find_image.handle()
async def handle_find_image(
    bot: Bot, 
    event: Event, 
    state: T_State, 
    msg: Messagev11 = CommandArg(), 
    args: Namespace = ShellCommandArgs()
):
    logger.info("search image")
    if args.knn:
        if args.wc:
            await find_image.finish("图搜图近似数量以后再写")
        filename = ""
        for messagesegment in event.get_message():
            if messagesegment.type == "image":
                filename = messagesegment.data["file"][:32]
                fileurl = messagesegment.data["url"]
        if event.reply:
            for messagesegment in event.reply.message:
                if messagesegment.type == "image":
                    filename = messagesegment.data["file"][:32]
                    fileurl = messagesegment.data["url"]
        if not filename:
            await find_image.finish(SEARCH_IMAGE_ARGS_HELP_KNN)
        image_meta = await es_cli.search(
            index=minio_config.minio_es_image_metadata_indice.format(version="*"),
            query={"ids": {"values": [filename]}}
            )
        if image_meta["hits"]["total"] == 0:
            image_resp = await httpxclient.get(fileurl)
            image_bytes = image_resp.read()
            res = await search_image_from_knn(image_bytes, args.count, args.candidates)
        else:
            res = await search_image_from_knn(filename, args.count, args.candidates)
    else:        
        res = await search_image_from_text(tags=args.tags, ntags=args.ntags, count=args.count, wc=args.wc)

    if not res:
        logger.warning(f"[Image Search] not found ?")
        await find_image.finish("not found")

    #logger.info(str(res))
    return_message = Messagev11()

    if len(res) == 1:
        image_bytes = await httpxclient.get(MINIO_URL+res[0]["url"])
        return_message.append(MessageSegmentv11.image(image_bytes))
    else:
        for im in res:
            pass

    return_message.append(MessageSegmentv11.image(res))

    await find_image.finish(return_message)


async def search_image_from_text(tags:list[str], ntags:list[str] = None, count: int = 1, wc: bool = False) -> Mapping:
    query_body = {
        "bool": {
            "must": [],
            "filter": [],
            "should": [],
            "must_not": []
        }
    }
    for w in tags:
        if w:
            query_body["bool"]["filter"].append({"match_phrase": {"ocr": w}})
    if ntags:
        for n in ntags:
            if n:
                query_body["bool"]["must_not"].append({"match_phrase": {"ocr": n}})
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
                #size=10
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