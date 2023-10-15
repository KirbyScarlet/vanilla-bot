# Vanilla Bot
# nonebot_plugin_minio

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
import nonebot.params
import nonebot.dependencies

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

VERSION = "v0.1.1"

BUCKET_NAME = minio_config.minio_image_bucket_name
META_INDEX = minio_config.minio_es_image_metadata_indice.format(
    version=VERSION)
OCR_INDEX = minio_config.minio_es_ocr_indice
VIT_INDEX = minio_config.minio_es_vit_indice.format(version=VERSION)

cqimage_filename = compile(r"(.*)\.image")

@driver.on_bot_connect
async def minio_startup_checker(bot: Bot):
    if not await minio_cli.bucket_exists(BUCKET_NAME):
        await minio_cli.make_bucket(BUCKET_NAME)
    if not await es_cli.indices.exists(
        index=META_INDEX
    ):
        await es_cli.indices.create(
            index=META_INDEX,
            mappings=minio_config.minio_es_image_mapping
        )
    if not await es_cli.indices.exists(
        index=OCR_INDEX
    ):
        await es_cli.indices.create(
            index=OCR_INDEX,
            mappings=minio_config.minio_es_ocr_mapping
        )
    if not await es_cli.indices.exists(
        index=VIT_INDEX
    ):
        await es_cli.indices.create(
            index=VIT_INDEX,
            mappings=minio_config.minio_es_vit_mapping
        )


class ImageMeta(BaseModel):
    # filename: str
    localfile_path: str
    origin_url: str
    last_modified: datetime.datetime
    image_format: str
    image_size_bytes: int
    resolution: Mapping[Literal["width", "height"], int]
    n_frames: Optional[int]
    localfile_exists: bool = True
    tags: str = ""
    # ocr: str = ""
    # vit: list = []

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
    if l := cqimage_filename.findall(data.get("file", "")):
        md5sum = l[0]
        logger.info("image md5: " + md5sum)
    # 如果图库内已经有该图片，则不执行重复上传
    es_meta_exists = await es_cli.exists(
        index=META_INDEX,
        id=md5sum
    )
    logger.info("image exist:" + bool(es_meta_exists).__str__() + " " + md5sum) 
    if md5sum and bool(es_meta_exists):
        await es_cli.update(
            index=META_INDEX,
            id=md5sum,
            doc={"lastmodified": datetime.datetime.utcfromtimestamp(event.time)},)
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
    if md5sum and (await es_cli.exists(index=META_INDEX, id=md5sum)):
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

    # gif_image.save(f"/tmp/{md5sum}.png")

    # with BytesIO() as gif_io:
    #     image.save(gif_io, "PNG")
    #     img = gif_io.getvalue()
    imagemetadata = ImageMeta.parse_obj({
        # "filename": md5sum,
        "localfile_path": image_path_filename,
        "origin_url": data.get("url", None),
        "last_modified": datetime.datetime.utcnow(),
        "image_format": image.format.lower(),
        "image_size_bytes": image_size,
        "resolution": {"width": image.size[0], "height": image.size[1]},
        "n_frames": image.n_frames if hasattr(image, "n_frames") else 1,
        # "ocr": ocr,
        # "vit": vit
    })

    try:
        await es_cli.index(
            index=META_INDEX,
            id=md5sum,
            document=imagemetadata.dict()
        )
    except Exception as e:
        logger.error(e)

    try:

        ocr = await chineseocr_lite(img)
        # print(ocr)
        if ocr.strip():
            await es_cli.index(
                index=OCR_INDEX,
                id=md5sum,
                document={"ocr": ocr}
            )
        logger.info(f"ocr: {ocr}")
    except Exception as e:
        #traceback.print_exc()
        logger.warning(f"ocr: {image_path_filename}")

    image.seek(0)
    try:
        if image.format == "PNG":
            vit = await predict_async(image.convert("RGB"))
        elif image.format == "GIF":
            img_tmp = Image.new("RGB", image.size, (255, 255, 255))
            for frame in ImageSequence.all_frames(image):
                img_tmp.paste(frame, (0,0))
                break
            vit = await predict_async(img_tmp)
            img_tmp.close()
        else:
            vit = await predict_async(image)
        # vit = await predict_async(image if image.format != "GIF" else gif_image)
        # print(vit)
        await es_cli.index(
            index=VIT_INDEX,
            id=md5sum,
            document={"vit": vit}
        )
    except Exception as e:
        #traceback.print_exc()
        logger.warning(f"\033[32mvit\033[0m: {image_path_filename} \n {e}")

    imgio.seek(0)

    try:
        try:
            exist = await minio_cli.stat_object(BUCKET_NAME, image_path_filename)
        except:
            exist = False
        if not exist:
            result = await minio_cli.put_object(BUCKET_NAME, image_path_filename, imgio, length=image_size)
    except Exception as e:
        logger.warning(result)
        logger.error(e)
    finally:
        imgio.close()
        image.close()



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
