from pydantic import BaseSettings

from typing import Optional, Union, Mapping

from nonebot import get_driver

class Config(BaseSettings):
    minio_hosts: str = "127.0.0.1:9000"
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_secure: bool = False

    class Config:
        extra = "ignore"

minio_config = Config.parse_obj(get_driver().config)