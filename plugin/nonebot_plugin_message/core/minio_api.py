##

from io import BytesIO
from os import PathLike
from nonebot import require
from nonebot.log import logger
from nonebot import get_driver
from miniopy_async import Minio

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

@get_driver().on_startup
async def check_bucket_exists():
    if not await minio_cli.bucket_exists(IMAGE_BUCKET_NAME):
        await minio_cli.make_bucket(IMAGE_BUCKET_NAME)
    if not await minio_cli.bucket_exists(FILES_BUCKET_NAME):
        await minio_cli.make_bucket(FILES_BUCKET_NAME)

class MinioAPI(ObjectStorageAPI):
    async def __aenter__(self):
        self.minio_cli: Minio = minio_cli
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def file_exists(self, file_path: PathLike, storage="minio"):
        return await self.minio_cli.object_exists(IMAGE_BUCKET_NAME, file_path)

    async def upload_file_data(self, file_path: PathLike, file_data: BytesIO, storage="minio"):
        file_data.seek(0)
        return await self.minio_cli.put_object(IMAGE_BUCKET_NAME, file_path, file_data, file_data.getvalue().__len__())

    async def delete_file_data(self, file_path: PathLike = "", storage: str = "minio", *args, **kwargs) -> bool:
        return await self.minio_cli.remove_object(IMAGE_BUCKET_NAME, file_path)

    async def get_file_data(self, file_path: PathLike = "", storage: str = "minio", *args, **kwargs) -> bytes: 
        try:
            resp = await self.minio_cli.get_object(IMAGE_BUCKET_NAME, file_path)
            return await resp.content.read()
        except Exception as e:
            logger.error(f"获取文件 {file_path} 失败，错误信息：{e}")
            return b""