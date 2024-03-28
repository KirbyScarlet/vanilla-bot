#!/usr/bin/python3

__doc__ = """\
当该模块作为vanilla-bot的subprocess启动时，则使用该文件作为入口
负责独立处理vanilla-bot产生的图片信息"""

import asyncio
import httpx

import api
import main

httpxclient = httpx.AsyncClient(timeout=1)

