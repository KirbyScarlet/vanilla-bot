#!/usr/bin/python3

from nonebot import get_driver
from nonebot.drivers.fastapi import Driver
from .config import web_config

driver: Driver = get_driver()
app = driver.server_app
PREFIX = web_config.web_prefix

