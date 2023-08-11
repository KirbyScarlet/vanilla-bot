from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="ElasticSearch聊天记录",
    description="使用ElasticSearch处理聊天记录",
    usage='''\

暂时没有用法\
''',
)

from .es import upload_es
from .es import es_cli