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
from .main import handle_selftest
from .main import is_self_message
from .main import on_self_command, on_self_shell_command
from .main import handle_self_plugin