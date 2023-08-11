#!/bin/python3
# @KirbyScarlet
# @VanillaPartyProject 香子兰蛋糕屋

# 公主连结机器人

import nonebot

from nonebot import on_command
from nonebot import on_message
from nonebot.rule import to_me
from nonebot.rule import T_State
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment

import sqlite3

HELP_TEXT = """\
使用说明：
=========================
合刀 血量1 血量2 血量3
自动识别boss剩余血量
计算补偿秒数，并计算满补需垫刀伤
=========================
合刀 血量1 血量2
自动识别boss剩余血量
尽可能计算满补所需垫刀
========================="""

def comp(h1, maxhp) -> float:
    h1persecond = h1/90
    h1realsecond = maxhp/h1persecond
    return 110-h1realsecond
    

def rebate(h1, h2, maxhp) -> float:
    return comp(h1, maxhp-h2)

def decomp(h1, maxhp):
    return maxhp-7*h1/30

pair = on_command("合刀")

@pair.handle()
async def _pair(bot: Bot, event: MessageEvent, msg: Message = CommandArg()):
    error = False
    try:
        nums = list(map(int, map(float, msg.extract_plain_text().split())))
        if not 2<=len(nums)<=3:
            error = True
    except:
        error = True
    
    if error:
        await pair.finish(HELP_TEXT)

    reply = MessageSegment.reply(event.message_id)
    text = lambda x: MessageSegment.text(x)
    message = Message()
    message.append(reply)
    
    if len(nums) == 3:
        nums.sort()
        a, b, c = nums
        if a+b<c:
            await pair.finish(reply + text(f"不够，还差{c-a-b+1}，进一刀{int((c-a-b)*30/7)+1}吃满补"))
        elif a+b==c:
            await pair.finish(reply + text(f"正好收了"))
        else:
            message.append(text(f"{a}先出，"))
            if (r:=rebate(b,a,c))>89:
                message.append(text(f"{b}返{r:.2f}秒\n"))
            else:
                message.append(text(f"{b}返{r:.2f}秒，再垫{int(decomp(b,c-a))+1}满补\n"))
            message.append(text(f"{b}先出，"))
            if (r:=rebate(a,b,c))>89:
                message.append(text(f"{a}返{r:.2f}秒"))
            else:
                message.append(text(f"{a}返{r:.2f}秒，再垫{int(decomp(a,c-b))+1}满补"))
            await pair.finish(message)
    else:
        nums.sort()
        a, b = nums
        if comp(b,a)>89:
            message.append(text(f"剩余血量{a}，刀伤{b}，满补\n"))
        else:
            message.append(text(f"剩余血量{a}，刀伤{b}，补偿{comp(b,a):.2f}秒，再垫{int(decomp(b,a))+1}满补\n"))
        message.append(text("==========\n"))
        message.append(text(f"剩余血量{b}，刀伤{a}，还差{b-a}\n第二刀砍{int(decomp(a,b)+1)}，刀伤{a}吃满补"))
        if (b-a)*30/7+1<b:
            message.append(text(f"\n刀伤{a}先出，第二刀超过{int((b-a)*30/7)+1}可满补"))
        await pair.finish(message)
        
                

                        
        
