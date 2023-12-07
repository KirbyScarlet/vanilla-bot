#

import nonebot
from nonebot import on_command, on_message, on_shell_command
from nonebot.rule import startswith

from nonebot.adapters import Bot, Event
from nonebot.params import CommandArg
from nonebot.rule import Rule

try:
    from nonebot.adapters.onebot.v11 import Bot as Botv11
    from nonebot.adapters.onebot.v11 import Event as Eventv11
    from nonebot.adapters.onebot.v11 import MessageEvent as MessageEventv11
    from nonebot.adapters.onebot.v11 import Message as Messagev11
    from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegmentv11
    from nonebot.adapters.onebot.v12 import Bot as Botv12
    from nonebot.adapters.onebot.v12 import Event as Eventv12
except ImportError:
    pass
    # Botv11 = None
    # Botv12 = None
    # Eventv11 = None
    # Eventv12 = None

from nonebot.typing import T_State
from nonebot.message import event_preprocessor
from nonebot import require
from nonebot.log import logger

from string import whitespace

import asyncio

from .config import self_management_config


@event_preprocessor
async def self_management(bot: Botv11, event: Eventv11, state: T_State):
    if (event.get_event_name() == "message_sent") and event.raw_message.startswith(self_management_config.self_management_prefix):
        event_dict = event.dict()
        event_dict["post_type"] = "message"
        event_dict["to_me"] = True
        state["convert"] = True

        new_event = MessageEventv11.parse_obj(event_dict)
        new_event.__setattr__("convert", True)
        asyncio.create_task(bot.handle_event(new_event))

PREFIX = self_management_config.self_management_prefix

async def _is_self_message(bot: Botv11, event: Eventv11, state: T_State):
    try:
        if event.get_user_id() == bot.self_id:
            return True
    except Exception as e:
        logger.warning(f"v11 error event type: [{type(event)}] errors: {e}")
    
is_self_message = Rule(_is_self_message)

def on_self_command(cmd: str, rule: Rule = None, **kwargs):
    if cmd in whitespace:
        raise ValueError("cmd is required")
    return on_command(PREFIX+cmd, rule=is_self_message&rule, **kwargs)

def on_self_shell_command(cmd, rule=None, **kwargs):
    if cmd in whitespace:
        raise ValueError("cmd is required")
    return on_shell_command(PREFIX+cmd, rule=is_self_message&rule, **kwargs)


status = on_self_command("test")

@status.handle()
async def handle_selftest(bot: Bot, event: Event, state: T_State):
    await status.finish("test03")

    

