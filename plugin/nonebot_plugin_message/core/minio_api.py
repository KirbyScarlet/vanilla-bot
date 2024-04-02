##

from io import BytesIO
from os import PathLike
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

from .base_api import ObjectStorageAPI

IMAGE_BUCKET_NAME = message_core_config.message_core_storage_prefix + "-image"
FILES_BUCKET_NAME = message_core_config.message_core_storage_prefix + "-files"

@get_driver().on_startup()
async def check_bucket_exists():
    if not await minio_cli.bucket_exists(IMAGE_BUCKET_NAME):
        await minio_cli.make_bucket(IMAGE_BUCKET_NAME)
    if not await minio_cli.bucket_exists(FILES_BUCKET_NAME):
        await minio_cli.make_bucket(FILES_BUCKET_NAME)

class MinioAPI(ObjectStorageAPI):
    async def __aenter__(self):
        self.minio_cli = minio_cli
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def upload_file_data(self, file_name: str, file_path: PathLike, file_data: bytes|BytesIO, storage="minio"):
        return await self.minio_cli.put_object(storage, file_name, file_data)

    async def delete_file_data(self, file_name: str, file_path: PathLike, storage: str = "minio", *args, **kwargs) -> bool:
        return await self.minio_cli.remove_object(storage, file_name)
