#!/usr/bin/python3

from nonebot import get_driver
from nonebot.drivers.fastapi import Driver
from fastapi import FastAPI
from nonebot.log import logger
from typing import cast
from .config import web_config

driver: Driver = get_driver()
if isinstance(driver, Driver):
    app = driver.server_app
else:
    logger.warning("only fastapi driver is supported now")
    app = None

#cast(FastAPI, app)

PREFIX = web_config.web_prefix

