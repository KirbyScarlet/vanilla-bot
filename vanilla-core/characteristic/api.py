#

__doc__ = """\
考虑到此部分执行速度远慢于机器人核心功能，且此部分代码改动不会过于频繁，则剥离计算图片特征相关的代码，作为独立的应用运行。
linux端使用pipe文件和机器人主程序通信。
win端以后再想办法"""

from typing import Literal
import fastapi
from pydantic import BaseModel
from PIL import Image
from httpx import AsyncClient
from io import BytesIO
import base64
import uvicorn

from fastapi import HTTPException
from .main import predict

httpxclient = AsyncClient(timeout=10)
app = fastapi.FastAPI()

class ImageRequest(BaseModel):
    """
    """
    raw: bytes|None = None
    url: str|None = None
    base64: str|None = None
    device: Literal["cpu", "cuda"]

@app.post("/feature/image")
async def image_predict(request: ImageRequest):
    if request.raw:
        image = Image.open(BytesIO(request.raw))
    elif request.url:
        image = Image.open(httpxclient.get(request.url, stream=True).raw)
    elif request.base64:
        image = Image.open(BytesIO(base64.b64decode(request.base64)))
    else:
        #return {"detail": "需要指定一种图片类型：图片二进制，图片链接，图片base64"}
        raise HTTPException(400, "需要至少指定一种图片类型：图片二进制，图片链接，图片base64")
    feature = await predict(image=image)
    return {"detail":"success", "data": {"image": feature}}

class TextRequest(BaseModel):
    text: str|list[str]|None = None

@app.post("/feature/text")
async def text_predict(request: TextRequest):
    if isinstance(request.text, list):
        pass
    else:
        feature = await predict(text=request.text)
    return {"detail": "success", "data": {"text": feature}}

class ClipSettings(BaseModel):
    
    device: Literal["cpu", "cuda"] = None
    model_name: str = None
    system: Literal["stop", "restart"] = None

    class Config:
        extra = "allow"

@app.post("/settings")
async def settings(request: ClipSettings):
    pass