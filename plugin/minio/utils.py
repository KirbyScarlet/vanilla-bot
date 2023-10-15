#
from nonebot.log import logger

from nonebot.internal.adapter.bot import Bot
from nonebot.internal.adapter.event import Event
from nonebot.internal.adapter.message import Message, MessageSegment

from pydantic import BaseModel, validator
from typing import Optional, Union

try:
    from nonebot.adapters.onebot.v11.bot import Bot as Botv11
    from nonebot.adapters.onebot.v11.event import Event as Eventv11
    from nonebot.adapters.onebot.v11.message import Message as Messagev11
    from nonebot.adapters.onebot.v11.message import MessageSegment as MessageSegmentv11
except ImportError:
    pass

__all__ = [
    "send_forward_message",
]

class ForwardMessageCQHttp(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    uin: Optional[int] = None
    content: Union[Messagev11, str, list["content"]] = None
    seq: Optional[Union[Messagev11, str]] = None

    @validator("content")
    def content_validator(cls, v):
        if isinstance(v, Messagev11):
            m = [str(s) for s in v]
            return "".join(m)
        else:
            return v

    class Config:
        extra = "ignore"

async def send_forward_message(bot: Bot, event: Event, message: list[ForwardMessageCQHttp]):
    """
    send_forward_message(
        bot: Bot,
        event: Event,
        
    )
    """

