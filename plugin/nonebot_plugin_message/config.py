from pydantic import BaseSettings

from typing import Optional, Union, Mapping
from elasticsearch._async.client.utils import _TYPE_HOSTS
from nonebot import get_driver

class Config(BaseSettings):
    message_api = "elasticsearch"
    message_index_name = "vanillabot-message-{adapter}-{botid}-{version}"
    message_objects_api = "minio"
    message_image_index_name = "vanillabot-image-{version}"
    message_file_index_name = "vanillabot-file-{version}"

    class Config:
        extra = "ignore"

message_config = Config.parse_obj(get_driver().config)

NONEBOT_PLUGIN_MESSAGE_VERSION = "1.0.1"