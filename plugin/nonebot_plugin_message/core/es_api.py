##

__version__ = "0.1.0"

from io import BytesIO
from typing import TypeAlias, TypeVar
from async_lru import alru_cache

from nonebot import require
from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters import Bot

from .config import message_core_config
from .base_api import MessageAPI

try:
    esmodule = require("nonebot_plugin_elasticsearch")
    es_cli = esmodule.elasticsearch_client
except RuntimeError:
    try:
        from ...nonebot_plugin_elasticsearch import elasticsearch_client as es_cli
    except ImportError:
        logger.error("请检查 nonebot_plugin_elasticsearch 是否安装，或该插件路径与 nonebot_plugin_message 位于同一路径。")
        raise

INDEX_NAME = "{bot_name}-{message_type}-{driver_name}-{bot_id}-{version}"

MESSAGE_MAPPING_TEMPLATE = {
    "properties": {
        "time": {
            "type": "date"
        },
        "plain_text": {
            "type": "text",
            "analyzer": "ik_smart",
            "search_analyzer": "ik_smart",
            "fielddata": "true",
            "fields": {
                "keywords": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        }
    }
}

IMAGE_MAPPING_TEMPLATE = {
    "properties": {
        "localfile_storage": {"type": "keyword"},
        "localfile_path": {"type": "text"},
        "origin_url": {"type": "text", "index": False},
        "image_format": {"type": "keyword"},
        "image_size_bytes": {"type": "integer"},
        "resolution": {
            "properties": {
                "width": {"type": "integer"},
                "height": {"type": "integer"}
            }
        },
        "n_frames": {"type": "integer"},
        "tags": {
            "type": "text",
            "analyzer": "ik_smart",
            "search_analyzer": "ik_smart",
            "fielddata": True,
            "fields": {
                "keywords": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "localfile_exists": {
            "type": "boolean"
        },
        "simular_hash": {
            "type": "keyword"
        },
        "simularity": {
            "type": "float"
        },
        "ocr": {
            "type": "text",
            "analyzer": "ik_smart",
            "search_analyzer": "ik_smart",
            "fielddata": True,
            "fields": {
                "keywords": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        },
        "abadon": {
            "type": "keyword"
        }
    }
}

IMAGE_CHARACTERISTIC_MAPPING = {
    "properties": {
        "characteristic": {
            "type": "dense_vector",
            "dims": message_core_config.message_core_characteristic_dense,
            "index": True,
            "similarity": "l2_norm"
        },
    }
}

IMAGE_TEMP_MAPPING_TEMPLATE = {
    "properties": {
        "ocr": {"type": "boolean"},
        "characteristic": {"type": "boolean"},
        "delete_flag": {"type": "boolean"}
    }
}

@get_driver().on_bot_connect
async def init_es_cli(bot: Bot):
    message_index_name = INDEX_NAME.format(
        bot_name = message_core_config.message_core_storage_prefix,
        message_type = "message",
        driver_name = "".join(bot.adapter.get_name().split()).lower(),
        bot_id = bot.self_id,
        version = __version__
    )
    image_index_name = message_core_config.message_core_storage_prefix + "-image"
    image_characteristic_name = message_core_config.message_core_storage_prefix + "-image-characteristic-" + message_core_config.message_core_characteristic_model
    if await es_cli.indices.exists(index=message_index_name):
        await es_cli.indices.create(index=message_index_name, mappings=MESSAGE_MAPPING_TEMPLATE)
    if await es_cli.indices.exists(index=image_index_name):
        await es_cli.indices.create(index=image_index_name, mappings=IMAGE_MAPPING_TEMPLATE)
    if await es_cli.indices.exists(index=image_characteristic_name):
        await es_cli.indices.create(index=image_characteristic_name, mappings=IMAGE_CHARACTERISTIC_MAPPING)
    if await es_cli.indices.exists(index="vanillabot-temp-image"):
        await es_cli.indices.create(index="vanillabot-temp-image", mappings=IMAGE_TEMP_MAPPING_TEMPLATE)


class ElasticsearchAPI(MessageAPI):
    async def __aenter__(self):
        self.es_cli = es_cli
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.es_cli.close()

    async def index_exists(self, index_name: str):
        return await self.es_cli.indices.exists(index=index_name)

    async def create_index(self, index_name: str):
        return await self.es_cli.indices.create(index=index_name, body={"mappings": MESSAGE_MAPPING_TEMPLATE})

    async def delete_index(self, index_name: str):
        pass

    async def put_document(self, index_name: str, document, **kwargs):
        return await self.es_cli.index(index=index_name, document=document, **kwargs)
    
    async def get_document(self, index_name, condition = None):
        return ""
        return await self.es_cli.get(index=index_name)

    async def delete_document(self, index_name: str, **kwargs):
        return await self.es_cli.delete(index=index_name, **kwargs)

    async def put_image_metadata(self, index_name: str, image_hash: str, **image_data):
        return await self.es_cli.index(index=index_name, document=image_data, id=image_hash)
    
    async def get_image_metadata(self, index_name, image_hash = "", condition = None):
        return {}

    async def update_image_metadata(self, index_name: str, **image_data):
        return await self.es_cli.update(index=index_name, id=image_data["image_hash"], body={"doc": image_data})

    async def delete_image_metadata(self, index_name: str, **image_data):
        return await self.es_cli.delete(index=index_name, id=image_data["image_hash"])






