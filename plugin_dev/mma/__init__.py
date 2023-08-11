from nonebot import on_command
from nonebot.rule import to_me
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    MessageEvent,
    Message,
    MessageSegment,
    Bot
)
from nonebot.params import CommandArg
import aiofiles
from .mathematica import calc
import time

mma = on_command(
    "mma", 
    aliases = {"mathematica"}, 
    priority = 99,
    rule = to_me()
)

@mma.handle()
async def _mma(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    txt = msg.extract_plain_text()
    res = await calc(txt)
    await mma.finish(MessageSegment.reply(event.message_id) + res)
    
