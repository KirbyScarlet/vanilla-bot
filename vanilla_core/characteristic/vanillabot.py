#!/usr/bin/python3

__doc__ = """\
当该模块作为vanilla-bot的subprocess启动时，则使用该文件作为入口
负责独立处理vanilla-bot产生的图片信息"""

import asyncio
from io import BytesIO
import httpx
import elasticsearch
import pathlib
import dotenv
from PIL import Image

# vanilla core 的路径，要从这里找elasticsearch的配置
# 先这么写，到时候改成可动态修改的
PWD = pathlib.Path(__file__).parent.resolve()
ENVFILE = PWD.parent.parent / ".env"

config = dotenv.dotenv_values(ENVFILE)

try:
    es_cli = elasticsearch.AsyncElasticsearch(
        hosts = config.get("ES_HOSTS", "http://127.0.0.1:9200"),
        api_key = config.get("ES_API_KEY", None),
        verify_certs = config.get("ES_VERIFY_CERTS", None),
        **config.get("ES_CLIENT_PARAMETERS",{})
    )
    asyncio.get_running_loop().create_task(es_cli.info())
except Exception as e:
    print("\033[31m elasticsearch client init failed \033[0m")
    es_cli = None

if __name__ == "__main__":
    from main import predict, predict_lock
else:
    from .main import predict, predict_lock

httpxclient = httpx.AsyncClient(timeout=1)
#predict_queue = asyncio.PriorityQueue()

async def vanillabot_predict():
    if es_cli is None:
        return
    while True:
        if predict_lock.locked():
            await asyncio.sleep(0.1)
            continue
        try:
            res = es_cli.search(
                index="vanillabot-temp-image", 
                size=1, 
                sort={"create_time":"asc"},
                query={
                    "bool": {
                        "must": {
                            "characteristic": False
                        }
                    }
                })
            if image_meta:=res["hits"]["hits"]:
                
                try:
                    res = es_cli.search(
                        index = "vanillabot-image-*",
                        query = {"ids": {"values": image_meta[0]["_id"]}}
                    )
                except Exception as e:
                    print(f"\033[31m get image meta failed: {e} \033[0m")
                    return None
                
                if image_meta := res["hits"]["hits"]:
                    image_hash = image_meta[0]["_id"]
                    match image_meta[0]["_source"]["localfile_storage"]:
                        case "local":
                            image_url = f"""http://127.0.0.1:{config.get("PORT")}{config.get("WEB_URI_PREFIX", "/vanilla/bot")}/image/{image_hash}"""
                            req = await httpxclient.get(image_url)
                            image_bytes = await req.aread()
                            image_io = BytesIO(image_bytes)
                            image = Image.open(image_io)
                        case "minio":
                            pass

                characteristic = await predict(image)

                image.close()
                image_io.close()

                if characteristic:
                    es_cli.update(
                        index=f"""vanillabot-image-{image_meta[0]["_source"]["version"]}""",
                        id=image_meta[0]["_id"],
                        doc={
                            "characteristic": characteristic
                        }
                    )
        except Exception as e:
            print(e)
            asyncio.sleep(0.1)
            continue
            
        