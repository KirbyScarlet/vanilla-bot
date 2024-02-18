#

__all__ = ["es_cli"]

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="ElasticSearch接口",
    description="提供nonebot访问elasticsearch的能力",
    homepage="",
    usage="""\
"""
)

from .es import elasticsearch_client