#!/bin/python3

__author__ = """
    Kirby Scarlet   (/^w^)/wwwww
    VanillaPartyProject 香草味的糕点屋
    MIT License
    copyright Chenzhou 2022-2024
"""

# 一个香子兰花的字符画，还没想好设计
__icon__ = """vanilla flower"""

__doc__ = """\
  https://vanilla.wiki/
"""

import nonebot

from nonebot.adapters.onebot.v11 import Adapter as Adapterv11

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(Adapterv11)

nonebot.load_plugins("plugin")
nonebot.load_plugins("plugin_dev")

if __name__ == "__main__":
    nonebot.run()