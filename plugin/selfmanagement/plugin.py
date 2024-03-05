# 一个简单的自我管理机器人

from nonebot.adapters.onebot.v11 import Bot as Botv11
from nonebot.adapters.onebot.v11 import Message as Messagev11
from nonebot.adapters.onebot.v11 import Event as Eventv11
from nonebot.adapters.onebot.v11 import MessageSegment as MessageSegmentv11
from nonebot.adapters.onebot.v11 import MessageEvent as MessageEventv11

from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser
from nonebot.matcher import matchers
from nonebot import get_bot, get_driver
from argparse import Namespace

import asyncio

from .main import on_self_shell_command

plugin_parser = ArgumentParser()
plugin_parser.add_argument("plugin_name", nargs="*", help="执行与本插件相同的后端的插件命令")
plugin_parser.add_argument("--list", action="store_true", help="列出所有后端插件")
plugin_parser.add_argument("--off", action="store_true", help="禁用后端插件")
plugin_parser.add_argument("--on", action="store_true", help="启用后端插件")

self_plugin = on_self_shell_command("plugin", parser=plugin_parser)


@self_plugin.handle()
async def handle_self_plugin(
    bot: Botv11,
    event: Eventv11,
    state: T_State,
    msg: Messagev11 = CommandArg(),
    args: Namespace = ShellCommandArgs()
):
    if args.list+args.off+args.on > 1:
        await self_plugin.finish("请检查参数")
    if args.list:
        res = []
        for i in matchers.values():
            for m in i:
                res.append(repr(m))
        await self_plugin.finish("插件列表：\n"+"\n".join(res))
    elif args.off:
        if not args.plugin_name:
            await self_plugin.finish("请输入插件名")
        await self_plugin.finish("测试关闭")
    elif args.on:
        if not args.plugin_name:
            await self_plugin.finish("请输入插件名")
        await self_plugin.finish("测试开启")
    else:
        omessage = event.dict()
        omessage["message"] = msg
        del omessage["original_message"]
        omessage["raw_message"] = msg.extract_plain_text()

        new_message_event = MessageEventv11.parse_obj(omessage)
        new_message_event.__setattr__("convert", True)

        asyncio.create_task(bot.handle_event(new_message_event))
