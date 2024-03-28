#

from functools import cache
from abc import ABC, ABCMeta, abstractmethod
from io import BytesIO
from os import PathLike
from typing import Mapping

class MessageAPI(ABC):
    @abstractmethod
    async def __aenter__(self) -> "MessageAPI":
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    @cache
    async def index_exists(
        self, 
        index_name: str
    ) -> bool:
        """
        检查存放文本记录的数据库是否已创建相应的表
        参数：
            index_name: 表名
        返回值类型：
            bool
        """
        raise NotImplementedError
    
    @abstractmethod
    async def create_index(
        self, 
        index_name: str, 
    ) -> bool:
        """
        创建数据表
        参数：
            index_name: 表名
        """
        # 
        raise NotImplementedError
    
    @abstractmethod
    async def delete_index(
        self, 
        index_name: str
        ) -> bool:
        """
        删除数据表【危】
        """
        raise NotImplementedError
    
    @abstractmethod
    async def put_document(
        self, 
        index_name: str, 
        event: Mapping
    ) -> bool:
        """
        插入新记录
        参数：
            index_name: 数据表
            doc_id: 主键（可选值）默认为空字符串
            doc_body: 数据键值对
        返回值类型：
            type[bool]：数据插入是否成功
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_document(
        self, 
        index_name: str, 
        condition: Mapping = {}
    ) -> Mapping:
        """
        条件查找记录
        参数：
            index_name: 数据表
            condition: 查询条件
        """
        raise NotImplementedError
    
    @abstractmethod
    async def put_image_metadata(
        self, 
        index_name: str, 
        image_hash: str, 
        image_data: Mapping
    ) -> bool:
        """
        上传图片信息，不包括图片数据
        参数：
            index_name: 数据表
            image_hash: 图片的hash值，
            image_data: 图片信息数据，详见image.py
        """
        raise NotImplementedError
    
    @abstractmethod
    async def update_image_metadata(
        self, 
        index_name: str, 
        image_hash: str, 
        image_data: Mapping
    ) -> bool:
        """
        上传图片信息，不包括图片数据
        参数：
            index_name: 数据表
            image_hash: 图片的hash值，
            image_data: 图片信息数据
        """
        raise NotImplementedError
    
    @abstractmethod
    async def get_image_metadata(
        self,
        index_name: str,
        image_hash: str = "",
        condition: Mapping = {}
    ) -> Mapping:
        """
        根据条件查找图片
        参数：
            index_name: 数据表
            image_hash: 图片hash值，可选参数
            condition: 图片查询条件
        """
        raise NotImplementedError
    
    @abstractmethod
    async def delete_image_metadata(
        self,
        index_name: str,
        condition: Mapping = {}
    ) -> bool:
        """
        【危】
        """
        raise NotImplementedError


class ObjectStorageAPI(ABC):
    @abstractmethod
    async def __aenter__(self) -> "ObjectStorageAPI":
        raise NotImplementedError
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def upload_file_data(
        self, 
        file_name: str, 
        file_path: PathLike, 
        file_data: bytes|BytesIO
    ) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    async def delete_file_data(
        self,
        file_name: str,
        file_path: PathLike
    ) -> bool:
        raise NotImplementedError