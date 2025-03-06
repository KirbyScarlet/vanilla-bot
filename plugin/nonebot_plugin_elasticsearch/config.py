
from pydantic import BaseModel

from typing import Optional, Union, Mapping
#from elasticsearch._async.client.utils import _TYPE_HOSTS
from nonebot import get_driver, get_plugin_config

class Config(BaseModel):
    es_client_parameters: Optional[Mapping] = {}
    es_verify_certs: bool = False
    es_api_key: Optional[str] = None
    es_hosts: str|list[str] = "http://127.0.0.1:9200"

    class Config:
        extra = "ignore"

es_config = get_plugin_config(Config)
