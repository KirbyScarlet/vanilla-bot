#

import asyncio
from nonebot.log import logger
from .config import message_core_config

match message_core_config.message_core_mapping_storage:
    case "elasticsearch":
        try:
            from .es_api import ElasticsearchAPI
        except ImportError:
            logger.error("请检查**")
        message_api = asyncio.run(ElasticsearchAPI().__aenter__())
    case _:  # 默认使用控制台输出
        try:
            from .localfile_api import ConsoleOutputMessageAPI
        except ImportError:
            logger.error("请检查**")
        message_api = asyncio.run(ConsoleOutputMessageAPI().__aenter__())

match message_core_config.message_core_files_storage:
    case "minio":
        try:
            from . import minio_api
        except ImportError:
            logger.error("请检查**")
        file_api = asyncio.run(minio_api.MinioAPI().__aenter__())
    case "local":
        try:
            from .localfile_api import LocalStorageAPI
        except ImportError:
            logger.error("请检查**")
        file_api = asyncio.run(LocalStorageAPI().__aenter__())
    case _:  # 默认使用控制台输出
        try:
            from .localfile_api import ConsoleOutputStorageAPI
        except ImportError:
            logger.error("请检查**")
        file_api = asyncio.run(ConsoleOutputStorageAPI().__aenter__())