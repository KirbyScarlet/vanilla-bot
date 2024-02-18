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

from nonebot.adapters import MessageSegment
from nonebot.log import logger

async def put_image(
        image_hash: str = "", 
        image_url: str = "", 
        image_bytes: bytes|BytesIO|Image.Image|Path = None
        ):
    pass

