# 本地保存文件 & 测试

from io import BytesIO
import pathlib
import asyncio
import aiofiles
from typing import Mapping
import sys

from nonebot.log import logger

from .base_api import MessageAPI, ObjectStorageAPI
from .config import message_core_config

class ConsoleOutputAPI(MessageAPI):
    """
    仅打印所有记录到控制台
    """
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def index_exists(self, index_name: str):
        return True
    
    async def create_index(self, index_name: str):
        return True
    
    async def delete_index(self, index_name: str):
        return True
    
    async def put_document(self, index_name: str, event: Mapping):
        logger.info("put_document: " + "\033[7m" + str(event) + "\033[0m")
        return True
    
    async def get_document(self, index_name: str, condition: Mapping = None):
        return {}
    
    async def put_image_metadata(self, index_name: str, image_hash: str, image_data: Mapping) -> bool:
        logger.info("put_image_metadata: " + "\033[7m" + str(image_data) + "\033[0m")
        return True
    
    async def get_image_metadata(self, index_name: str, image_hash: str = "", condition: Mapping = ...) -> Mapping:
        return {}
    
    async def delete_image_metadata(self, index_name: str, image_hash: str = "", condition: Mapping = ...) -> bool:
        return True
    
class ConsoleOutputStorageAPI(ObjectStorageAPI):
    """
    仅打印所有记录到控制台
    """
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def upload_file_data(self, file_path: pathlib.PathLike, file_data: bytes | BytesIO, storage: str = "local", *args, **kwargs) -> bool:
        logger.info("upload_file_data: " + "\033[7m" + str(file_path) + f" {len(file_data)} bytes" + "\033[0m")
        return True

    async def delete_file_data(self, file_path: pathlib.PathLike, storage: str = "local", *args, **kwargs) -> bool:
        return True
    
    async def get_file_data(self, file_path: pathlib.PathLike, storage: str = "local", *args, **kwargs) -> bytes | BytesIO:
        return b""
    

class LocalStorageAPI(ObjectStorageAPI):
    """
    本地文件存储
    """
    async def __aenter__(self):
        if message_core_config.message_core_files_local_path:
            self.path_prefix = pathlib.Path(message_core_config.message_core_files_local_path / message_core_config.message_core_storage_prefix / "files" )
        else:
            self.path_prefix = pathlib.Path(sys.path[0] / "data" / message_core_config.message_core_storage_prefix / "files")

        if pathlib.Path.is_dir(self.path_prefix):
            try:
                self.path_prefix.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning("LocalStorageAPI: 本地路径创建失败 " + str(e))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def upload_file_data(self, file_path: pathlib.PathLike, file_data: bytes | BytesIO, storage: str = "local", *args, **kwargs) -> bool:
        try:
            async with aiofiles.open(self.path_prefix / file_path , "wb") as f:
                await f.write(file_data)
        except Exception as e:
            logger.warning("LocalStorageAPI: 文件上传失败 " + str(e))
            return False
        return True
    
    async def delete_file_data(self, file_path: pathlib.PathLike, storage: str = "local", *args, **kwargs) -> bool:
        if pathlib.Path.is_file(self.path_prefix / file_path ):
            try:
                pathlib.Path.unlink(self.path_prefix / file_path)
            except Exception as e:
                logger.warning("LocalStorageAPI: 文件删除失败 " + str(e))
                return False
            return True
        else:
            logger.warning("LocalStorageAPI: 文件不存在 ")
            return False
        
    async def get_file_data(self, file_path: pathlib.PathLike, storage: str = "local", *args, **kwargs) -> bytes | BytesIO:
        if pathlib.Path.is_file(self.path_prefix / file_path):
            try:
                async with aiofiles.open(self.path_prefix / file_path , "rb") as f:
                    fileio = await f.read()
                return fileio
            except Exception as e:
                logger.warning("LocalStorageAPI: 文件读取失败 " + str(e))
                return b""
        else:
            logger.warning("LocalStorageAPI: 文件不存在 ")
            return b""