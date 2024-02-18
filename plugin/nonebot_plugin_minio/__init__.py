#

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name = "minio接口",
    description = "minio对接nonebot插件"
)

from .minio import minio_cli