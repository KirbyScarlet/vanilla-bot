# 作为一个合格的一体机
# 一定要有良好的自我管理

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="一体机自我控制",
    description="在机器人端和普通设备同时登录时，可自己发送命令给机器人",
    usage='''\
''',
)

from .main import self_management
from .main import handle_selftest, handle_find_image