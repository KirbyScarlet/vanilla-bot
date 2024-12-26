#

from pydantic import BaseModel
from nonebot import get_driver

class Config(BaseModel):
    self_management_prefix: str = "#!/"
    self_management_only: bool = True

    class Config:
        extra = "ignore"

self_management_config = Config.parse_obj(get_driver().config)