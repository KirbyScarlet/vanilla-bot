#

from pydantic import BaseModel
from nonebot import get_driver, get_plugin_config

class Config(BaseModel):
    self_management_prefix: str = "#!/"
    self_management_only: bool = True

    class Config:
        extra = "ignore"

self_management_config = get_plugin_config(Config)