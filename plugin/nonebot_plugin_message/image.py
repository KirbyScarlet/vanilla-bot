#

from functools import cache
from io import BytesIO
from numbers import Number
from httpx import AsyncClient
from httpx import HTTPError
from hashlib import md5
from re import compile
from PIL import Image
from PIL import ImageSequence
from pydantic import BaseModel
from pathlib import Path
from argparse import Namespace
import datetime
import base64
from typing import Literal, Mapping, Optional, cast

from nonebot.adapters import MessageSegment
from nonebot.log import logger
from nonebot.rule import ArgumentParser
from nonebot import get_driver

from fastapi import FastAPI, Response

from .config import message_config, NONEBOT_PLUGIN_MESSAGE_VERSION
from .core import message_api
from .core import message_core_config
from .core import file_api

@cache
def build_index_name():
    return message_config.message_image_index_name.format(**{
        "bot_name": message_core_config.message_core_storage_prefix,
        "version": NONEBOT_PLUGIN_MESSAGE_VERSION
    })

image_args = ArgumentParser()
image_args.add_argument("tags", nargs="*", help="图片文字的关键字")
image_args.add_argument("-c", "--count", type=int, dest="count", default=1, help="指定图片数量")
image_args.add_argument("-n", "--ntags", nargs="*", dest="ntags", help="指定过滤关键词")
image_args.add_argument("-e", "--exact", action="store_true", dest="exact", default=False, help="精确匹配tags")
image_args.add_argument("-l", "--list", action="store_true", dest="list", default=False, help="仅输出文字信息")
image_args.add_argument("--regexp", action="store_true", dest="regexp", default=False, help="tags和ntags使用正则表达式")

image_args.add_argument("--wc", action="store_true", dest="wc", default=False, help="仅统计数据量")

image_args.add_argument("--knn", action="store_true", dest="knn", default=False, help="开启以图搜图")
image_args.add_argument("--knn-hnsw", action="store_true", dest="hnsw", default=True, help="开启以图搜图的hnsw搜索，此选项速度更快，准确度稍低")
image_args.add_argument("--knn-candidates", type=int, dest="candidates", default=10000, help="当使用hnsw搜索时，指定候选数量")
image_args.add_argument("--knn-threshold", type=float, dest="threshold", default=1.95, help="当不开启hnsw算法时，指定相似度")

image_args.add_argument("--ocr", action="store_true", dest="ocr", default=False, help="获取当前对话的第一张图并进行文字识别")
image_args.add_argument("--box", action="store_true", dest="box", default=False, help="获取当前对话的第一张图并进行文字识别，并返回文字选框的图片")

httpxclient = AsyncClient(timeout=30)
driver = get_driver()
app: FastAPI = driver.server_app
PREFIX = "/vanilla/bot"

class ImageMeta(BaseModel):
    # localfile_hash: str  #使用的数据库不同，该字段索引方式可能比较麻烦，则考虑将hash值传参入数据库接口函数
    localfile_storage: str  # 使用哪种存储保存图片 例如 local, minio, ...
    localfile_path: str  # 图片在上述系统中的路径 /path/to/your/pic.jpeg
    origin_url: str  # 网络图片来源，本地来源则为空
    create_time: datetime.datetime  # 该图片信息的创建时间
    last_modified: datetime.datetime  # 该图片信息的最后修改时间
    image_format: str  # 图片格式
    image_size_bytes: int  # 图片大小
    resolution: Mapping[Literal["width", "height"], int]  # 图片分辨率
    n_frames: Optional[int] = 1  # 如果该图片为动图，则记录该动图的帧数
    localfile_exists: bool = True  # 该图片是否保存于本地  #重复图片清理
    simular_hash: str = ""  # 若该图片被重复清理，则记录与该图片相同的hash值
    simularity: float = 0.0  # 若该图片被重复清理，则记录与该图片相同的相似度
    tags: list[str] = []  # 手动指定的图片标签
    ocr: str = ""  # 文字识别结果
    characteristic: list[float|int] = []  # 图片特征向量

    abadon: str|None = None  # 弃置标签，由算法确定该图片是否为重复图片，等待二次判定


class ImageMetaTemp(BaseModel):
    """
    由于计算文字识别和特征向量消耗时间较长，
    获取新图片时，临时表记录图片信息。
    当两个值都计算完成时，临时表删除该记录。
    """
    # _id = localfile_hash
    # localfile_hash: str  
    create_time: datetime.datetime
    ocr: bool = False
    characteristic: bool = False
    delete_flag: bool = False

async def put_image(
        image_hash: str = "", 
        image_url: str = "", 
        image_bytes: bytes|BytesIO|Image.Image|Path = None
        ):
    if image_bytes:
        if isinstance(image_bytes, bytes):
            image_io = BytesIO(image_bytes)
        elif isinstance(image_bytes, BytesIO):
            image_Image = Image.open(image_bytes)
            image_bytes = image_bytes.getvalue()
            image_io = BytesIO(image_bytes)
    elif image_url:
        image_res = await httpxclient.get(image_url)
        image_bytes = await image_res.aread()
        image_io = BytesIO(image_bytes)
        image_Image = Image.open(image_io)
    else:
        raise ValueError("image_bytes or image_url must be provided")
    
    image_format = image_Image.format or ""
    image_size_bytes = len(image_bytes)
    if image_hash:
        image_hash = image_hash.lower()
    else: 
        image_hash = md5(image_bytes).hexdigest()
    localfile_path = image_hash[0:2] + "/" + image_hash[2:4] + "/" + image_hash + "." + image_format.lower()

    localfile_storage = message_config.message_objects_storage
    origin_url = image_url
    create_time = datetime.datetime.now()
    last_modified = create_time
    image_format = image_Image.format.lower()
    image_size_bytes = len(image_bytes)
    image_width, image_height = image_Image.size
    n_frames = image_Image.n_frames if image_Image.format == "GIF" else 1

    image_meta = ImageMeta(
        localfile_storage=localfile_storage,
        localfile_path=localfile_path,
        origin_url=origin_url,
        create_time=create_time,
        last_modified=last_modified,
        image_format=image_format,
        image_size_bytes=image_size_bytes,
        resolution={"width": image_width, "height": image_height},
        n_frames=n_frames,
        localfile_exists=True,
        simular="",
        tags=[],
        ocr="",
        characteristic=[],
    )

    try:
        await message_api.put_image_metadata(
            index_name = build_index_name(), 
            image_hash = image_hash,
            image_data = image_meta.model_dump()
        )
    except Exception as e:
        logger.warning(f"Failed to put image metadata: {e}")
        return False
    
    try:
        await file_api.upload_file_data(
            file_path = localfile_path,
            file_data = image_io
        )
    except Exception as e:
        logger.warning(f"Failed to upload image file: {e}")
        return False
    
    try:
        await message_api.put_image_metadata(
            index_name = "vanillabot-temp-image",
            image_hash = image_hash,
            image_data = {
                "create_time": create_time,
                "ocr": False,
                "characteristic": False,
                "version": NONEBOT_PLUGIN_MESSAGE_VERSION
            }
        )  # 类似一个消息队列，用于异步处理OCR和特征提取，默认处理方式在vanilla-core
    except Exception as e:
        logger.warning(f"Failed to put image metadata: {e}")
        return False
    return True


async def search_image(cmd: Namespace):
    if image:=cmd.knn:  # 以图搜图，相似搜索
        image_type, image_value = image.items()[0]
        match image_type:  # 允许传入的图片类型
            case "url":
                resp = await httpxclient.get(image_value)
                image_bytes = await resp.aread()
            case "hash":
                if len(image_value)==32:
                    r = await message_api.get_image_metadata(query={"ids": {"values": [image_value]}})
                    if r["hits"]["total"]:
                        localfile_path = r["hits"]["hits"][0]["_source"]["localfile_path"]
                    else:
                        localfile_path = ""
                image_bytes = await file_api.get_file_data(localfile_path)
            case "origin_bytes":
                image_bytes = image_value
            case "base64":
                image_bytes = base64.b64decode(image_value)
            case "MessageSegment":
                if image_value.type == "image":
                    ...
            case _:
                pass
    

