#

#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import sys
# from paddleocr.paddleocr import main
from PIL import Image

from paddleocr import PaddleOCR, draw_ocr

import asyncio
from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor(max_workers=1)

ocr = PaddleOCR(use_angle_cls=True)

async def ocr_async(*args):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(pool, ocr.ocr, *args)
    return result


