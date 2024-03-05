from pydantic import BaseSettings
from nonebot import get_driver

from typing import List, Optional, Literal, TypeAlias, Union

class Config(BaseSettings):
    
    vanilla_web_prefix: str = "/vanilla/bot"

    class Config:
        extra = "ignore"

vanilla_web_config = Config.parse_obj(get_driver().config)