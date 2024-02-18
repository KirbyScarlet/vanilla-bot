##

from typing import TypeAlias, TypeVar
from functools import cache

from nonebot import require
from nonebot.log import logger

from .config import message_core_config

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

@cache
async def check_index_exists(index_name: str):
    return await es_cli.indices.exists(index=index_name)

async def create_index(index_name: str):
    return await es_cli.indices.create(index=index_name, body={"mappings": MESSAGE_MAPPING_TEMPLATE})

async def put_document(index_name: str, document, **kwargs):
    return await es_cli.index(index=index_name, document=document, **kwargs)




