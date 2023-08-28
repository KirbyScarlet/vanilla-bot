from pydantic import BaseSettings

from typing import Optional, Union, Tuple, Mapping, Dict
from elasticsearch._async.client.utils import _TYPE_HOSTS
from nonebot import get_driver


class Config(BaseSettings):
    es_client_parameters: Optional[Mapping] = None
    es_verify_certs: bool = False
    es_api_key: Optional[Union[str, Tuple[str, str]]] = None
    es_hosts = ["http://127.0.0.1:9200"]
    es_keywords_index_properties = {
        "properties": {
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
    es_message_indice_name: str = "vanillabot-message-{self_id}-{VERSION}"

    class Config:
        extra = "ignore"


es_config = Config.parse_obj(get_driver().config)
