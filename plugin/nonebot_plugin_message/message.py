#

from functools import cache
from datetime import datetime
from re import compile

from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment
from nonebot.log import logger

from .config import message_config, NONEBOT_PLUGIN_MESSAGE_VERSION
from .core import message_api
from .core import message_core_config
from .image import put_image

@cache
def build_index_name(adapter: str = "", botid: str = ""):
    return message_config.message_index_name.format(**{
        "bot_name": message_core_config.message_core_storage_prefix,
        "driver_name": adapter,
        "bot_id": botid,
        "version": NONEBOT_PLUGIN_MESSAGE_VERSION
    })

MD5_STRING = compile(r"[a-fA-F0-9]{32}")
def get_md5_from_string(s: str) -> str:
    e = MD5_STRING.match(s)
    if e:
        return e.group()
    else:
        return ""

async def put_message(event: dict, message: Message = None, adapter: str = "", botid: str = ""):
    index_name = build_index_name(adapter, botid)
    if not await message_api.index_exists(index_name):
        await message_api.create_index(index_name)

    event["time"] = datetime.fromtimestamp(event["time"])

    for k in event:
        if k.endswith("id"):
            # 频道号，频道用户的id全是字符串类型，保证统一
            event[k] = str(event[k])
    
    if message:
        message_original = []
        
        try: # 按照nonebot标准，Message类的这个方法一定会返回纯文本，但有些适配器好像没做到
            message_plain_text = message.extract_plain_text()
            event["plain_text"] = message_plain_text
        except Exception as e:
            logger.warning("extract_plain_text error: " + str(e))

        for message_segment in message:
            if isinstance(message_segment, MessageSegment):
                message_original.append({message_segment.type: message_segment.data})
                message_segment_type = message_segment.type
            elif isinstance(message_segment, dict):
                message_original.append(message_segment)
                message_segment_type = message_segment.get("type")

            match message_segment_type:
                case "image":
                    #logger.info("image meta: " + str(message_segment))
                    try:
                        if file_unique:=message_segment.get("data").get("file_unique"):
                            image_md5 = get_md5_from_string(file_unique)
                        elif file_name:=message_segment.get("data").get("file"):
                            image_md5 = get_md5_from_string(file_name)
                        else:
                            image_md5 = ""
                    except:
                        image_md5 = ""
                    try:
                        image_url = message_segment.get("data").get("url")
                    except:
                        image_url = ""
                    await put_image(image_hash=image_md5, image_url=image_url)
                case "video":
                    pass
                case "forward":
                    pass
                case _:
                    pass
            message_original.append(str(message_segment))

    try:
        await message_api.put_document(index_name, event)
    except Exception as e:
        logger.error(f"聊条记录保存失败：{e}\n" + str(event))


            

