##

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name = "nonebot_plugin_message",
    description = "聊天记录整理插件",
    usage = ""
)

from .config import message_config

from .onebotv11 import upload_es_eventv11
