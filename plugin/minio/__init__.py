from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="minio对象存储",
    description="使用minio保存图片",
    usage='''\
静默生效
''',
)

from .m import minio_startup_checker
from .m import minio_self_sender, minio_other_sender
from .m import minio_cli