from pydantic import BaseSettings

from typing import Optional, Union, Tuple, Mapping, Dict
from nonebot import get_driver

class Config(BaseSettings):
    self_management_prefix: str = "#!/"

    class Config:
        extra = "ignore"

self_management_config = Config.parse_obj(get_driver().config)