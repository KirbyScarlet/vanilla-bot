from miniopy_async import Minio
from minio.error import S3Error
from io import BytesIO
from httpx import AsyncClient
from httpx import HTTPError
from hashlib import md5
from re import compile
from PIL import Image
from PIL import ImageSequence
from pydantic import BaseModel

from typing import Any, Iterable, Optional, Tuple, Mapping, Literal

from nonebot import get_driver, get_bot
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent, Message
from nonebot import require
from nonebot import on, on_message, MatcherGroup
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.rule import Rule
import nonebot.params,nonebot.dependencies

import datetime

import traceback


from .config import minio_config
from .ocr import chineseocr_lite
from .vit import predict_async

require("elasticsearch")
from ..elasticsearch import es_cli
from ..elasticsearch.config import es_config

driver = get_driver()

minio_cli = Minio(
    minio_config.minio_hosts,
    access_key=minio_config.minio_access_key,
    secret_key=minio_config.minio_secret_key,
    secure=minio_config.minio_secure
)

INDEX = "qqimage-metadata-{self_id}-dev0.0.5"
cqimage_filename = compile(r"(.*)\.image")

@driver.on_bot_connect
async def minio_startup_checker(bot: Bot):
    if not await minio_cli.bucket_exists("qqimage"):
        await minio_cli.make_bucket("qqimage")
    if not await es_cli.indices.exists(index=INDEX.format(self_id=bot.self_id)):
        await es_cli.indices.create(
            index = INDEX.format(self_id=bot.self_id), 
            mappings = minio_config.minio_es_mapping
            )
        

class ImageMeta(BaseModel):
    #filename: str
    filepath: str
    fileurl: str
    lastmodified: datetime.datetime
    format: str
    size: int
    resolution: Mapping[Literal["width", "height"], int]
    n_frames: Optional[int]
    fileexist: bool = True
    tags: str = ""
    ocr: str = ""
    vit: list = []

    class Config:
        extra = "ignore"


def gif_extract(image: Image) -> bytes:
    im = Image.new("RGBA", (image.size[0], image.size[1]*image.n_frames))
    i = 0
    for frame in ImageSequence(image):
        im.paste(frame, (0, frame.size[1]*i))
        i += 1
    imageio = BytesIO()
    im.save(imageio, format="PNG")

    imagebytes = imageio.getvalue()
    
    im.close()
    imageio.close()

    return imagebytes

async def upload_image(data: dict[str, Any], bot: Bot, event: Event, **kwargs):
    if l:=cqimage_filename.findall(data.get("file","")):
        md5sum = l[0]
        #print(md5sum)
    # 如果图库内已经有该图片，则不执行重复上传
    es_meta_exists = await es_cli.exists(index=INDEX.format(self_id=bot.self_id), id=md5sum)
    #print(es_meta_exists)
    if md5sum and bool(es_meta_exists):
        await es_cli.update(
            index = INDEX.format(self_id=bot.self_id), 
            id = md5sum, 
            doc = {"lastmodified": datetime.datetime.now()-datetime.timedelta(hours=8)})
        return

    try:
        async with AsyncClient() as client:
            resp = await client.get(data.get("url"))
            img = await resp.aread()
    except HTTPError as e:
        logger.error(e)
        return
    except Exception as e:
        logger.error(e)
        return

    if img:
        imgio = BytesIO(img)
        imgio.flush()
        imgio.seek(0)
    else:
        logger.warning("image length 0" + data.get("url"))
        return

    # 重复一遍代码的理由：
    # Event的图片cq码返回的文件名都是 `<md5sum>.image` 格式
    # 万一这个文件名有问题，则这个md5sum获取可能会出问题。
    # 其实也没啥怕问题的，就怕直接从文件名获取的md5值可能为空
    if not md5sum:
        md5sum = md5(img).hexdigest()
    if md5sum and (await es_cli.exists(index=INDEX.format(self_id=bot.self_id), id=md5sum)):
        return


    image = Image.open(imgio)
    image_size = len(img)
    image_path_filename = f"{md5sum[0:2]}/{md5sum[2:4]}/{md5sum}.{image.format.lower()}"
    image.seek(0)

    # if image.format == "GIF":
    #     gif_image = Image.new("RGB", (image.size[0], image.size[1]*image.n_frames))
    #     for i in range(image.n_frames):
    #         image.seek(i)
    #         gif_image.paste(image, (0, image.size[1]*i))

        #gif_image.save(f"/tmp/{md5sum}.png")

        # with BytesIO() as gif_io:
        #     image.save(gif_io, "PNG")
        #     img = gif_io.getvalue()

    try:

        ocr = await chineseocr_lite(img)
        #print(ocr)
    except Exception as e:
        ocr = ""
        traceback.print_exc()
        logger.warning(f"ocr: {image_path_filename}")

    image.seek(0)
    try:
        vit = await predict_async(image)
        #vit = await predict_async(image if image.format != "GIF" else gif_image)
        #print(vit)
    except Exception as e:
        vit = []
        traceback.print_exc()
        logger.warning(f"vit: {image_path_filename}")

    imagemetadata = ImageMeta.parse_obj({
        #"filename": md5sum,
        "filepath": image_path_filename,
        "fileurl": data.get("url",None),
        "lastmodified": datetime.datetime.now()-datetime.timedelta(hours=8),
        "format": image.format.lower(),
        "size": image_size,
        "resolution": {"width": image.size[0], "height": image.size[1]},
        "n_frames": image.n_frames if hasattr(image, "n_frames") else 1,
        "ocr": ocr,
        "vit": vit
    })
    imgio.seek(0)

    try:
        try:
            exist = await minio_cli.stat_object(f"qqimage", image_path_filename)
        except:
            exist = False
        if not exist:
            result = await minio_cli.put_object(f"qqimage", image_path_filename, imgio, length=image_size)
    except Exception as e:
        logger.warning(result)
        logger.error(e)
    finally:
        imgio.close()
        image.close()
    
    try:
        await es_cli.index(
            index=INDEX.format(self_id=bot.self_id), 
            id=md5sum,
            document=imagemetadata.dict()
        )
    except Exception as e:
        logger.error(e)


async def image_in_event(event: Event) -> bool:
    has_image = False
    try:
        for message_segement in event.get_message():
            if message_segement.type == "image":
                has_image = True
                break
    except ValueError:
        pass
    return has_image
    
minio_other_sender = on_message(rule=image_in_event)

@minio_other_sender.handle()
async def image_upload_handler(bot: Bot, event: Event):
    for ms in event.get_message():
        if ms.type == "image":
            await upload_image(ms.data, bot, event)


async def self_image_in_event(event: Event) -> bool:
    has_image = False
    if hasattr(event, "message") and isinstance(event.message, Message):
        for message_segment in event.message:
            if message_segment.type == "image":
                has_image = True
                break
    return has_image

minio_self_sender = on("message_sent", rule=image_in_event)

@minio_self_sender.handle()
async def self_image_upload_hander(bot: Bot, event: Event):
    for ms in event.message:
        if ms.type == "image":
            await upload_image(ms.data, bot, event)