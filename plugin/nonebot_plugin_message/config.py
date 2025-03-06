#

from pydantic import BaseModel

from typing import Optional, Union, Mapping
from elasticsearch._async.client.utils import _TYPE_HOSTS
from nonebot import get_driver, get_plugin_config

class Config(BaseModel):
    message_api: str = "console"
    message_index_name: str = "vanillabot-message-{adapter}-{botid}-{version}"
    message_objects_storage: str = "console"
    message_image_index_name: str = "vanillabot-image-{version}"
    message_file_index_name: str = "vanillabot-file-{version}"

    class Config:
        extra = "ignore"

class WebConfig(BaseModel):
    web_prefix: str = "/vanilla/bot/image"

    class Config:
        extra = "ignore"

message_config = get_plugin_config(Config)
web_config = get_plugin_config(WebConfig)

NONEBOT_PLUGIN_MESSAGE_VERSION = "1.0.1"