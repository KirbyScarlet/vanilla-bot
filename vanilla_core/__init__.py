#!/usr/bin/python3

__doc__ = """\
一些启动较慢的密集计算
直接写进nonebot插件会导致启动过于累赘，不利于机器人本身的调试
"""

#!/usr/bin/python3

# 分别以子程序的方式运行

import subprocess
import pathlib
from httpx import Client, ConnectError, ConnectTimeout
from dotenv import dotenv_values
import sys

config = dotenv_values(".env")
client = Client(timeout=1)
pwd = pathlib.Path(__file__).parent.absolute()

if config.get("IMAGE_CHARACTERISTIC_ENABLE", False):
    try:
        resp = client.get(config.get("IMAGE_CHARACTERISTIC_URL"))
        if resp.status_code == 200:
            pass
    except:
        characteristic = subprocess.Popen(["python3", pwd.name+"/characteristic/api.py"], stdin=subprocess.DEVNULL, stdout=sys.stdout, stderr=sys.stderr)

if config.get("IMAGE_OCR_ENABLE", False):
    try:
        resp = client.get(config.get("IMAGE_OCR_URL"))
        if resp.status_code == 200:
            pass
    except:
        ocr = subprocess.Popen(["python3", pwd.name+"/ocr/api.py"], stdin=subprocess.DEVNULL, stdout=sys.stdout, stderr=sys.stderr)

# try:
#     characteristic.wait()
# except KeyboardInterrupt:
#     pass

# try:
#     ocr.wait()
# except KeyboardInterrupt:
#     pass