from pydantic import BaseSettings

from typing import Optional, Union, Mapping
from elasticsearch._async.client.utils import _TYPE_HOSTS
from nonebot import get_driver

class Config(BaseSettings):
    es_client_parameters: Optional[Mapping] = None
    es_verify_certs: bool = False
    es_api_key: Optional[Union[str, tuple[str, str]]] = None
    es_hosts: list[_TYPE_HOSTS] = ["http://127.0.0.1:9200"]

    class Config:
        extra = "ignore"

es_config = Config.parse_obj(get_driver().config)
