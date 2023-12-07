from pydantic import BaseSettings
import aiofiles
from nonebot import get_driver

from typing import List, Optional, Literal, TypeAlias, Union
from urllib3.util.url import Url

Json: TypeAlias = dict


class Config(BaseSettings):
    minio_hosts: str = "127.0.0.1:9000"
    # minio 默认地址
    minio_access_key: str = ""
    minio_secret_key: str = ""
    # 连接 minio 服务器需要的key
    minio_secure: bool = False
    # 是否开启https访问minio，一般不开

    minio_image_bucket_name = "vanillabot-image"
    # 默认图片桶
    minio_es_ocr_indice = "vanillabot-image-ocr"
    # 图片内文字信息在elasticsearch中的索引名称
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
    } # 索引初始化，一般别动，除非自定义分词器
    minio_es_vit_indice = "vanillabot-image-vit-{version}"
    # 图片特征值索引名称
    minio_es_vit_mapping: Json = {
        "properties": {
            "vit": {
                "type": "dense_vector",
                "dims": 1000,
                "index": True,
                "similarity": "l2_norm"
            }
        }
    } # 特征值向量索引初始化，可根据特征模型维度数修改，dims推荐不超过1024
    minio_es_image_metadata_indice = "vanillabot-image-metadata-{version}"
    # 图片元信息索引名称
    minio_es_image_mapping: Json = {
        "properties": {
            "localfile_path": {"type": "text"},
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
            },
            "vit": {
                "type": "dense_vector",
                "dims": 1000,
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
    } # 除了分词器，其他的尽量别改，跟着代码走的，改了容易崩
    minio_vit_model_path: str = "google/vit-base-patch16-224"
    # 默认特征模型，默认使用 https://huggingface.co/google/vit-base-patch16-224
    minio_vit_gpu: bool = False
    # 提取特征是否使用cuda加速计算，还没测过，先别开
    minio_ocr_url: str = "http://127.0.0.1:8089/api/tr-run/"
    # 提取图片文字使用的ocr链接，暂时用的外部链接，以后想办法写进来
    minio_ocr_gpu: bool = False
    # 占坑用，暂时无效选项

    class Config:
        extra = "ignore"


minio_config = Config.parse_obj(get_driver().config)

# 有点新想法，先占坑，暂时用不着
class ESData(BaseSettings):
    shasum: str = None
    url: Union[str, Url, None] = None
    keyword: Optional[str] = ""
