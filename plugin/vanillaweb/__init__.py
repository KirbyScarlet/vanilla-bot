# 一个简单的es和minio管理页面
# 由于nonebot官方的cli-plugin-webui坑还没填
# 先自己实现一个，后续官方填坑后会进行适配

from nonebot import get_driver, require
from nonebot import on_command

from .index import *
from .image import *