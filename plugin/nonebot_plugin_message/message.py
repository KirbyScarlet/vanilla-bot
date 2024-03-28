#

from functools import cache
from datetime import datetime
from re import compile

from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment
from nonebot.log import logger

from .config import message_config, NONEBOT_PLUGIN_MESSAGE_VERSION
from .core import message_api
from .image import put_image

@cache
def build_index_name(adapter: str = "", botid: str = ""):
    return message_config.message_index_name.format({
        "adapter": adapter,
        "botid": botid,
        "version": NONEBOT_PLUGIN_MESSAGE_VERSION
    })

MD5_STRING = compile(r"[a-fA-F\d]{32}")
def get_md5_from_string(s: str) -> str:
    e = MD5_STRING.match(s)
    if e:
        return e.group()
    else:
        return ""

async def put_message(event: dict, message: Message, adapter: str = "", botid: str = ""):
    index_name = build_index_name(adapter, botid)
    if not await message_api.index_exists(index_name):
        await message_api.create_index(index_name)

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
        match message_segment.type:
            case "image":
                try:
                    try:
                        image_md5 = get_md5_from_string(message_segment.data["file"])
                    except:
                        image_md5 = ""
                    try:
                        image_url = message_segment.data["url"]
                    except:
                        image_url = ""
                    await put_image(image_hash=image_md5, image_url=image_url)
                except:
                    pass
            case "video":
                pass
            case _:
                pass

    event["message"] = message_original
    event["message_plain_text"] = message_plain_text

    try:
        await message_api.put_document(index_name, event)
    except Exception as e:
        logger.error(f"聊条记录保存失败：{e}\n" + str(event))


        

