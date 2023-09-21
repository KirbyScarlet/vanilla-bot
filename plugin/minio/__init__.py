from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="minio对象存储",
    description="使用minio保存图片",
    usage='''\
静默生效
''',
)

from .main import minio_startup_checker
from .main import minio_self_sender, minio_other_sender
from .main import minio_cli
from .search import find_image