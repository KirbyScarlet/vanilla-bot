##

from io import BytesIO
from typing import TypeAlias, TypeVar
from functools import cache

from nonebot import require
from nonebot.log import logger

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
        "localfile_exists": {"type": "boolean"},
        "characteristic": {
            "type": "dense_vector",
            "dims": 1024,
            "index": True,
            "similarity": "l2_norm"
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
    }
}


class ElasticsearchAPI(MessageAPI):
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @cache
    async def check_index_exists(index_name: str):
        return await es_cli.indices.exists(index=index_name)

    async def create_index(index_name: str):
        return await es_cli.indices.create(index=index_name, body={"mappings": MESSAGE_MAPPING_TEMPLATE})

    async def put_document(index_name: str, document, **kwargs):
        return await es_cli.index(index=index_name, document=document, **kwargs)

    async def put_image_metadata(index_name: str, **image_data):
        pass

    async def update_image_metadata(index_name: str, **image_data):
        pass

    async def delete_image_metadata(index_name: str, **image_data):
        pass






