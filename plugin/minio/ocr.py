###

from PIL import Image

import aiopytesseract
import re
from httpx import AsyncClient
from base64 import b64encode
from nonebot import logger
from io import BufferedIOBase
from elasticsearch import AsyncElasticsearch


spaceline = re.compile(r"\s*\n+")

async def tesseract(imageio: Image, lang="chi_sim+eng", **kwargs) -> str:
    text = await aiopytesseract.image_to_string(imageio, lang=lang)
    text = spaceline.sub("\n",text)
    if not "".join(text.split()):
        text = ""
    return text

async def save_tesseract(es_cli: AsyncElasticsearch, id: str, text: str):
    await es_cli.update(
        index = "qqimage-metadata",
        id = id,
        doc = {"ocr": text}
    )

OCR_URL = "http://127.0.0.1:8089/api/tr-run/"
client = AsyncClient(timeout=30)

async def chineseocr_lite(image: bytes):
    data = {"img": b64encode(image).decode()}
    response = await client.post(OCR_URL, data=data)
    json = response.json()
    if json.get("code") == 200:
        if json.get("data",""):
            return " ".join([s[1] for s in json["data"]["raw_out"]])
        else:
            return ""
    else:
        logger.warning(json)
        return ""
