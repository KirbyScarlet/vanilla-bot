from typing import Generic
from base64 import b64decode
import json
import io

from PIL import Image
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel

from paddleocr import draw_ocr

app = FastAPI()
httpxclient = AsyncClient()

if __name__ == "__main__":
    from main import ocr_async
else:
    from .main import ocr_async

OCR_HELP = {
    "api": "/ocr",
    "method": ["GET", "POST"],
    "params": {
        "image": {
            "desc": "必填，需要识别的图片，可以是本地图片路径、URL或base64编码的图片数据",
            "value": ['/path/to/image.jpg', 'http://example.com/image.jpg', 'base64编码的图片数据==']
        },
        "format": {
            "desc": "必填，用于判断image参数的类型",
            "value": ["file", "url", "base64"],
        },
        "lang": 
        {
            "desc": "可选，识别的语言，默认为 'zh' ",
            "value": ["zh", "jp", "en", "fr", "..."]
        },
        "output": {
            "desc": "可选，指定输出的内容，仅文字内容，或带坐标的json格式，或带框的图片，默认为 'text'",
            "value": ["text", "json", "image"]
        },
        "asynchronous": {
            "desc": "可选，是否异步执行，默认为 'false'。若此项为 'true'，则返回任务ID(通常为图片hash)",
            "value": ["true", "false"]
        },
        "vanilla-bot":{
            "desc": "仅用于vanilla-bot",
            "value": "<session_id>"
        },
        "result": {
            "desc": "可选互斥，此项仅接受任务ID，若此项存在，无视其他参数。返回任务执行结果",
            "value": ["<task_id>"]
        },
        "help": {
            "desc": "可选互斥，若此项存在，无视其他参数。返回帮助信息",
            "value": "{OCR_HELP}"
        }
    },
    "response": {
        "result": {
            "desc": "识别结果是否成功, 若指定async为true, 未完成则返回'pending'",
            "value": ["success", "failed", "pending"]
        },
        "task_id": {
            "desc": "任务id",
            "value": "<image_hash>"
        },
        "data": {
            "desc": "识别结果，根据output参数返回不同的结果，或错误信息",
            "value": [
                {"text": "example"},
                [
                    {"text": "example1", "position": [[0,0], [0,100], [100,0], [100,100]], "score": 0.95},
                    {"text": "example2", "position": [[0,100], [0,200], [100,100], [100,200]], "score": 0.85}
                ],
                {"image": "base64编码的带框识别内容=="},
                {"error": "<exception message>"}
            ]
        },
        "queue": {
            "desc": "仅使用result参数时返回。指定的task_id在队列中还需等待的数量",
            "value": 2
        }
    }
}

OCR_SETTINGS_HELP = {
    "api": "/ocr/settings/*",
    "method": ["GET", "POST", "PUT", "DELETE"],
    "params": {
        "vanilla_bot": {
            "session_id": "example_abcdefghijklmn",
            "message_core_mapping_storage": "elasticsearch",
            "message_core_file_storage": "minio",
            "message_core_storage_prefix": "vanillabot",
            "extra": {
                "elasticsearch": {
                    "host": "https://host:9200",
                    "api_key": "api_key_abcdefghijklmnopqrstuvwxyz",
                },
                "minio": {
                    "host": "host:9000",
                    "access_key": "access_key_abcdefghijklmnopqrstuvwxyz",
                    "secret_key": "secret_key_abcdefghijklmnopqrstuvwxyz",
                    "secure": "false",
                }
            }
        },
        "use_gpu": {
            "desc": "是否使用GPU",
            "value": "true"
        },
        "timeout": {
            "desc": "单张图片识别超时时间，单位为秒。0为不限制",
            "value": [0, 300]
        },
        "method":{
            "desc": "若使用POST方法，此项必填。指定设置参数的动作",
            "value": ["get", "set", "delete"]
        },
        "help": {
            "desc": "可选互斥，若此项存在，无视其他参数。返回帮助信息",
            "value": "{OCR_HELP}"
        }
    },
    "response": {
        "<request_param>": {
            "desc": "若请求方法为get, 返回对应参数的值。否则返回修改结果",
            "value": ["success", "failed", "<value>"],
            "[error]": "<exception message>"
        }
    }
}

class OCRParams(BaseModel):
    image: str | None = None
    format: str | None = ""
    lang: str = "zh"
    output: str = "json"
    asynchronous: bool = False
    vanilla_bot: str = ""
    result: str = ""
    help: bool = False

@app.post("/ocr")
async def ocr(
        params: OCRParams
    ):
    if params.help:
        return OCR_HELP
    if params.result:
        return result ###TODO
    if params.vanilla_bot:
        pass
    if params.format == "base64":
        image_bytes = b64decode(params.image)
    if params.format == "url":
        resp = await httpxclient.get(params.image)
        image_bytes = await resp.aread()

    # PaddleOCR.ocr() 的所有参数 万一以后用得上
    det=True,
    rec=True,
    cls=True,
    bin=False,
    inv=False,
    alpha_color=(255, 255, 255),
    slice={}
    # ================

    result = await ocr_async(image_bytes, det, rec, cls, bin, inv, alpha_color, slice)

    if params.output == "text":
        ret = "\n".join(i[1][0] for i in result[0])
        ret += "\n"
    elif params.output == "image":
        image = Image.open(io.BytesIO(image_bytes))
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]
        im = draw_ocr(image, boxes, txts, scores, font_path="")
        
    else:
        ret = json.dumps(result[0])

    return ret

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8186)