##

from nonebot import require
from nonebot.log import logger
from nonebot import get_driver

from .config import message_core_config

if message_core_config.message_core_files_storage == "minio":
    try:
        miniomodule = require("nonebot_plugin_minio")
        minio_cli = miniomodule.minio_cli
    except RuntimeError as e:
        try:
            from ...nonebot_plugin_minio import minio_cli
        except ImportError:
            logger.error("请检查 nonebot_plugin_minio 是否安装，或该插件路径与 nonebot_plugin_message 位于统一路径。")
            raise

IMAGE_BUCKET_NAME = message_core_config.message_core_storage_prefix + "-image"
FILES_BUCKET_NAME = message_core_config.message_core_storage_prefix + "-files"

get_driver().on_startup()
async def check_bucket_exists():
    pass


