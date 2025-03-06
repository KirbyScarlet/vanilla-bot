from pydantic import BaseModel

from typing import Optional, Union, Mapping

from nonebot import get_driver, get_plugin_config

class Config(BaseModel):
    message_core_mapping_storage: str = "elasticsearch" #指定聊天记录存储位置，默认使用es
    message_core_files_storage: str = "minio"  #指定二进制数据存储位置
    message_core_storage_prefix: str = "vanillabot"
    message_core_files_local_path: str|None = None 
    message_core_characteristic_dense: int = 1024
    message_core_characteristic_model: str|None = None
    
    class Config:
        extra = "ignore"

message_core_config = get_plugin_config(Config)