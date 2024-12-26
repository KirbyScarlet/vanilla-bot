from nonebot import on_command, on_shell_command, on_message, on_startswith
from nonebot.adapters import Bot, Event
from nonebot.rule import Rule, StartswithRule
from nonebot.typing import T_State
from nonebot.message import event_preprocessor
from nonebot.log import logger

from string import whitespace
from functools import partial

import asyncio

from .config import self_management_config

#由于不同的适配器，获取自己发送的消息的方式不同，需要单独写适配，此处仅做示例
@event_preprocessor
async def self_management_template(bot: Bot, event: Event, state: T_State):
    """
    判断是否时自己发送的消息
    如果是，根据适配器的消息类型，修改event的内容
    例如onebotv11需要将message_sent类型修改为message类型再重新发送给事件处理器
    satori则不需要进行额外处理消息类型，只需判断发送消息的sender_id和bot_id是否相同即可
    """
    if event.dict().get("message_type"):
        try:
            if event.dict().get("post_type") == "message_sent":
                return True
            if event.get_user_id() == bot.self_id:  #此处event不一定有sender id
                return True
        except Exception as e:
            logger.error(f"获取用户id失败: {e}")
    return False
    

PREFIX = self_management_config.self_management_prefix

async def _is_self_message(bot: Bot, event: Event, state: T_State):
    """
    判断是否时自己发送的消息
    """
    try:
        if event.dict().get("post_type") == "message_sent":
            return True
        if event.get_user_id() == bot.self_id:  #此处event不一定有sender id
            return True
    except Exception as e:
        # 在nonebot标准中，event.get_user_id() 必须由适配器重写该方法，但不排除有屎山
        logger.error(f"获取用户id失败: {e}")

is_self_message = Rule(_is_self_message)

on_self_command = partial(on_command, rule=is_self_message&StartswithRule(PREFIX, False))
on_self_shell_command = partial(on_shell_command, rule=is_self_message&StartswithRule(PREFIX, False))

test = on_self_command("test")
@test.handle()
async def _test(bot: Bot, event: Event, state: T_State):
    await test.finish("vanilla~(/^▽^)/~")




