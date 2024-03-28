#

from io import BytesIO
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
from typing import Literal, Mapping, Optional

from nonebot.adapters import MessageSegment
from nonebot.log import logger
from nonebot.rule import ArgumentParser

from .config import message_config

image_args = ArgumentParser()
image_args.add_argument("tags", nargs="*", dest="tags", help="图片文字的关键字")
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

httpxclient = AsyncClient(timeout=30)

class ImageMeta(BaseModel):
    # localfile_hash: str
    localfile_storage: str 
    localfile_path: str
    origin_url: str
    create_time: datetime.datetime
    last_modified: datetime.datetime
    image_format: str
    image_size_bytes: int
    resolution: Mapping[Literal["width", "height"], int]
    n_frames: Optional[int] = 1
    localfile_exists: bool = True
    tags: list[str] = []
    ocr: str = ""
    characteristic: list = []

class ImageMetaTemp(BaseModel):
    ocr: bool = False
    characteristic: bool = False

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
    
    image_format = image_Image.format or ""
    image_size_bytes = len(image_io)
    if image_hash:
        localfile_path = localfile_path[0:2] + "/" + localfile_path[2:4] + "/" + localfile_path[4:] + image_format

    localfile_storage = message_config.message_objects_storage
    origin_url = image_url
    create_time = datetime.datetime.now()
    last_modified = create_time
    image_format = image_Image.format.lower()
    image_size_bytes = len(image_io)
    image_width, image_height = image_Image.size
    n_frames = image_Image.n_frames if image_Image.format or image_Image.format == "GIF" else 1




async def search_image(cmd: Namespace):
    pass