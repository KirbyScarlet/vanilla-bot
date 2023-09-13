# 一个简单的es和minio管理页面
# 由于nonebot官方的cli-plugin-webui坑还没填
# 先自己实现一个，后续官方填坑后会进行适配

from nonebot.drivers.fastapi import Driver
from nonebot import get_driver
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pathlib import Path
from .config import vanilla_web_config

__all__ = [
    "PWD",
    "PREFIX",
    "app",
    "template"
]

PWD = Path(__file__).parent
PREFIX = vanilla_web_config.vanilla_web_prefix

driver: Driver = get_driver()
app = driver.server_app
template = Jinja2Templates(directory=PWD/"template")

app.mount(PREFIX+"/static/", StaticFiles(directory=PWD/"static"), name="static")