# 主页？

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Mapping, Union, Any

from .main import app
from .main import PREFIX
from .main import template

__all__ = [
    "get_index",
    "post_index",
]

@app.get(PREFIX, response_class=HTMLResponse)
async def get_index(): 
    return """
    <html>
    <head>
    <title>vanilla bot</title>
    </head>
    <body>
    vanilla bot
    </body>
    </html>
    """

class Item(BaseModel):
    cmd: str = ""
    args: Optional[Mapping[str, Any]] = None

@app.post(PREFIX, response_class=JSONResponse)
async def post_index(item: Item):
    return {"item": item.dict()}