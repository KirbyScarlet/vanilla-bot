##

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name = "nonebot_plugin_webclient",
    description="网页客户端，用于在“一体机”情况下时，可通过网页登录机器人账号进行收发消息",
    usage = "仅网页使用，无指令"
)

from .main import send_message_to_client
from .main import vanilla_client