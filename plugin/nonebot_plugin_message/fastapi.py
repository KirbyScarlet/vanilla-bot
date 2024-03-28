#!/usr/bin/python3

from nonebot import get_driver
from nonebot.drivers.fastapi import Driver

driver: Driver = get_driver()
app = driver.server_app

