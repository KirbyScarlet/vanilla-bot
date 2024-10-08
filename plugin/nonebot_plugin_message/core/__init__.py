#

import asyncio
from nonebot.log import logger
from .config import message_core_config

match message_core_config.message_core_mapping_storage:
    case "elasticsearch":
        try:
            from . import es_api
        except ImportError:
            logger.error("请检查**")
        message_api = asyncio.run(es_api.ElasticsearchAPI().__aenter__())

match message_core_config.message_core_files_storage:
    case "minio":
        try:
            from . import minio_api
        except ImportError:
            logger.error("请检查**")
        file_api = asyncio.run(minio_api.MinioAPI().__aenter__())