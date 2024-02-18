#

from functools import cache
from datetime import datetime

from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment
from nonebot.log import logger

from .config import message_config, NONEBOT_PLUGIN_MESSAGE_VERSION
from .core import index_exists, create_index, put_document

@cache
def build_index_name(adapter: str = "", botid: str = ""):
    return message_config.message_index_name.format({
        "adapter": adapter,
        "botid": botid,
        "version": NONEBOT_PLUGIN_MESSAGE_VERSION
    })

async def put_message(event: dict, message: Message, adapter: str = "", botid: str = ""):
    index_name = build_index_name(adapter, botid)
    if not await index_exists(index_name):
        await create_index(index_name)

    event["@timestamp"] = datetime.fromtimestamp(event["time"])

    for k in event:
        if k.endswith("id"):
            # 频道号，频道用户的id全是字符串类型，保证统一
            event[k] = str(event[k])
    
    message_original = []
    message_plain_text = message.extract_plain_text()

    for message_segment in message:
        if isinstance(message_segment, MessageSegment):
            message_original.append({message_segment.type: message_segment.data})
        else:
            message_original.append(str(message_segment))
        try:
            if message_segment.type == "image":
                pass
        except:
            pass

    event["message"] = message_original
    event["message_plain_text"] = message_plain_text

    try:
        await put_document(index_name, event)
    except Exception as e:
        logger.error(f"聊条记录保存失败：{e}\n" + str(event))


        

