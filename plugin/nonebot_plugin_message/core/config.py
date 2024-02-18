from pydantic import BaseSettings

from typing import Optional, Union, Mapping

from nonebot import get_driver

class Config(BaseSettings):
    message_core_mapping_storage: str = "elasticsearch" #指定聊天记录存储位置，默认使用es
    message_core_files_storage: str = "minio"  #指定二进制数据存储位置
    message_core_storage_prefix: str = "vanillabot"
    class Config:
        extra = "ignore"

message_core_config = Config.parse_obj(get_driver().config)