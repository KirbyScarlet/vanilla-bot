#!/usr/bin/python3

from nonebot import get_driver
from nonebot.drivers.fastapi import Driver
from nonebot.log import logger
from typing import cast, Optional, Generic
from pydantic import BaseModel

from .config import web_config, message_config
from .core import message_api, file_api

from fastapi import FastAPI
from fastapi.responses import Response

driver: Driver = get_driver()
if isinstance(driver, Driver):
    app = driver.server_app
else:
    logger.warning("only fastapi driver is supported now")
    app = None

#cast(FastAPI, app)

PREFIX = web_config.web_prefix


@app.get(PREFIX+"/image/{image_hash}")
async def get_image(image_hash: str):
    if len(image_hash)==32:
        r = await message_api.get_image_metadata(
            index_name = message_config.message_image_index_name,
            image_hash = image_hash
            )
        if r["hits"]["total"]:
            localfile_path = r["hits"]["hits"][0]["_source"]["localfile_path"]
        else:
            localfile_path = ""
    image_format = r["hits"]["hits"][0]["_source"]["image_format"]
    image_bytes = await file_api.get_file_data(localfile_path)
    return Response(image_bytes, media_type=f"image/{image_format}")

class ImageSearchRequest(BaseModel):
    type: str = "hash" # ["hash", "origin_bytes", "url", "base64"]
    hash: str = None
    url: str = None
    origin_bytes: bytes = None
    base64: str = None
    count: int = 10
    offset: int = 0

@app.post(PREFIX+"/image")
async def search_image(request: ImageSearchRequest):
    pass