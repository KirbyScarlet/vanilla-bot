#!/bin/python3

__author__ = """
    Kirby Scarlet   (/^w^)/wwwww
    VanillaPartyProject 香草味的糕点屋
"""

__doc__ = """\
一点一点写吧。
目前的想法是注重聊天记录的收集和使用
尽量保证开箱即用
尽量保证插件直接复制到别的机器人立马能用"""

import nonebot

from nonebot.adapters.onebot.v11 import Adapter

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(Adapter)

nonebot.load_plugins("./plugin")
nonebot.load_plugins("./plugin_dev")

if __name__ == "__main__":
    nonebot.run(host="0.0.0.0", port=8083)