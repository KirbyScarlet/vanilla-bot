from pydantic import BaseSettings
import aiofiles
from nonebot import get_driver

from typing import List, Optional, Literal, TypeAlias, Union
from urllib3.util.url import Url

Json: TypeAlias = dict


class Config(BaseSettings):
    minio_hosts: str = "127.0.0.1:9000"
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_secure: bool = False
    minio_image_bucket_name = "vanillabot-image"
    minio_es_ocr_indice = "vanillabot-image-ocr"
    minio_es_ocr_mapping: Json = {
        "properties": {
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
            }
        }
    }
    minio_es_vit_indice = "vanillabot-image-vit-{version}"
    minio_es_vit_mapping: Json = {
        "properties": {
            "vit": {
                "type": "dense_vector",
                "dims": 1000,
                "index": True,
                "similarity": "l2_norm"
            }
        }
    }
    minio_es_image_metadata_indice = "vanillabot-image-metadata-{version}"
    minio_es_image_mapping: Json = {
        "properties": {
            "localfile_path": {"type": "text", "index": False},
            "origin_url": {"type": "text", "index": False},
            "image_format": {"type": "keyword"},
            "size": {"type": "integer"},
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
            }
        }
    }
    vit_model_path: str = "google/vit-base-patch16-224"

    class Config:
        extra = "ignore"


minio_config = Config.parse_obj(get_driver().config)


class ESData(BaseSettings):
    shasum: str = None
    url: Union[str, Url, None] = None
    keyword: Optional[str] = ""
