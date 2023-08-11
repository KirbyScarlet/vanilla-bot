#

import nonebot

from nonebot import on_fullmatch
from nonebot.adapters.onebot.v11 import MessageSegment

yuyue = on_fullmatch("预约表")

json = """{"app":"com.tencent.structmsg"&#44;"desc":"新闻"&#44;"bizsrc":""&#44;"view":"news"&#44;"ver":"0.0.0.1"&#44;"prompt":"&#91;分享&#93;公会战分刀预约表"&#44;"meta":{"news":{"action":""&#44;"android_pkg_name":""&#44;"app_type":1&#44;"appid":101458937&#44;"ctime":1687629954&#44;"desc":"腾讯文档-在线表格"&#44;"jumpUrl":"https:\/\/docs.qq.com\/sheet\/DTUJzcW5FYUZacURl"&#44;"preview":"https:\/\/docs.idqqimg.com\/tim\/docs\/docs-design-resources\/mobile\/png@3x\/file_sheet_64@3x-28f87b2076.png"&#44;"source_icon":"https:\/\/p.qpic.cn\/qqconnect\/0\/app_101458937_1596103559\/100?max-age=2592000&amp;t=0"&#44;"source_url":""&#44;"tag":"腾讯文档"&#44;"title":"公会战分刀预约表"&#44;"uin":1991598742}}&#44;"config":{"ctime":1687629954&#44;"forward":true&#44;"token":"02eee743627a6f7b1bdc08ba8d728082"&#44;"type":"normal"}}"""

@yuyue.handle()
async def _yuyue():
    await yuyue.finish(MessageSegment.json(json))