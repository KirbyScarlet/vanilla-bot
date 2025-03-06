###

from functools import cache
from pydantic import BaseModel
from time import time
import datetime

from nonebot.adapters.onebot.v11 import MetaEvent as MetaEventv11
from nonebot.adapters.onebot.v11 import Event as Eventv11
from nonebot.adapters.onebot.v11 import MessageEvent as MessageEventv11
from nonebot.adapters.onebot.v11 import Bot as Botv11

from nonebot.adapters import Bot
from nonebot.message import event_preprocessor
from nonebot import get_driver
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.exception import IgnoredException

from .message import put_message

driver = get_driver()

class Document(BaseModel):
    pass

@event_preprocessor
async def upload_es_eventv11(bot: Botv11, event: Eventv11, state: T_State):
    if isinstance(event, MetaEventv11):
        return
    event_dict = event.model_dump()
    logger.debug(str(type(event_dict))+str(event_dict))
    if event_dict.get("original_message"):
        del event_dict["original_message"]
    if event_dict.get("raw_message"):
        event_dict["raw_message"] = str(event_dict["raw_message"])
    if event_dict.get("reply"):
        #event_dict["reply"] = event_dict["reply"].dict()
        for key in event_dict["reply"]:
            if key.endswith("id"):
                event_dict["reply"][key] = str(event_dict["reply"][key])
        event_dict["reply"]["message"] = str(event_dict["reply"]["message"])
    # try:
    if isinstance(event, MessageEventv11):
        message = event.get_message()
    else:
        message = None 
    await put_message(event_dict, message, "onebotv11", bot.self_id)
    # except LookupError as e:
    #     logger.error(f"upload_es_v11: {e}")
    #     logger.warning(f"event type: [{type(event)}] + {str(event.dict())}")
    #     #raise IgnoredException("不匹配的事件")

