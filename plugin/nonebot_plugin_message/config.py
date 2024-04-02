#

from pydantic import BaseModel

from typing import Optional, Union, Mapping
from elasticsearch._async.client.utils import _TYPE_HOSTS
from nonebot import get_driver

class Config(BaseModel):
    message_api = "elasticsearch"
    message_index_name = "vanillabot-message-{adapter}-{botid}-{version}"
    message_objects_storage = "minio"
    message_image_index_name = "vanillabot-image-{version}"
    message_file_index_name = "vanillabot-file-{version}"

    class Config:
        extra = "ignore"

class WebConfig(BaseModel):
    web_prefix: str = "/vanilla/bot/image"

    class Config:
        extra = "ignore"

message_config = Config.parse_obj(get_driver().config)
web_config = WebConfig.parse_obj(get_driver().config)

NONEBOT_PLUGIN_MESSAGE_VERSION = "1.0.1"