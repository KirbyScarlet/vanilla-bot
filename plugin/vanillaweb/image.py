# 展示或管理vanilla bot保存的图片
# 难啊
# 写代码可太难了

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import StreamingResponse
from fastapi.responses import Response
from fastapi import Request
from pydantic import BaseModel
from typing import Optional, Mapping, Any
from nonebot import logger
from httpx import AsyncClient

asyncclient = AsyncClient(timeout=30)

from .main import *

from ..elasticsearch import es_cli
from ..elasticsearch.config import es_config
from ..minio import minio_cli
from ..minio.config import minio_config

__all__ = [
    "image_index",
    "image_post",
]

@app.get(PREFIX + "/image", response_class=HTMLResponse)
async def image_index(request: Request):
    return template.TemplateResponse("image.html", {"request": request})

MINIO_IMAGE_URL = "http://" + minio_config.minio_hosts + "/" + minio_config.minio_image_bucket_name + "/"
@app.get(PREFIX + "/image/{localfile_path:path}")
async def get_image(localfile_path: str):
    image_format = localfile_path.split(".")[-1]
    res = await asyncclient.get(MINIO_IMAGE_URL + localfile_path)
    return Response(res.read(), media_type=f"image/{image_format}")
    #return StreamingResponse(res.aiter_raw(), media_type=f"image/{image_format}")
    # 这个返回方法更好，但是要报错，没找到问题出在哪儿


class ImageRequest(BaseModel):
    """
    * 可选参数
    #num 互斥参数
    ===
    method: "unchecked_image"
    * args: 
      * count: number
    ===
    method: "get_image"
    args:
      ids: md5hash
    ===
    method: "knn_search"
    args:
      *#1 query_vector: [...]
      *#1 localfile_path
      *#1 md5hash
    """
    method: str = ""
    args: Optional[Mapping[str, Any]] = {}

@app.post(PREFIX + "/image")
async def image_post(request: ImageRequest):
    match request.method:
        case "unchecked_image":
            return await get_unchecked_image(request.args)
        case "knn_search":
            return await knn_search(request.args)
        case _:
            return {"detail": f"undefined method {request.method}"}
        
UNCHECKED_QUERY = {
    "bool": {
        "must_not": {
            "exists": {
                "field": "checked"
            }
        }
    },
    "sort": [
    {
      "_script": {
        "script": "Math.random()",
        "type": "number",
        "order": "asc"
      }
    }
  ]
}
IMAGEMETA_INDEX = minio_config.minio_es_image_metadata_indice.format(version="*")

async def get_unchecked_image(args: Mapping[str, Any]):
    size = args.get("count", 10)
    try:
        res = await es_cli.search(
            index=IMAGEMETA_INDEX,
            query=UNCHECKED_QUERY,
            size=size
        )
    except Exception as e:
        logger.warning("unchecked image search error: " + str(e))
        return {"detail": "search error"}
    if res["hits"]["total"]["value"] == 0:
        return {"detail": "no unchecked image"}
    return {"detail": "success", "data": res["hits"]["hits"]}

KNN_QUERY = {
    "field": "vit",
    "k": 20,
    "num_candidates": 10000,
    "query_vector": []
}
VIT_INDEX = minio_config.minio_es_vit_indice.format(version="*")

async def knn_search(args: Mapping[str, Any]):
    if q:=args.get("query_vector"):
        query_vector = q
    if localfile_path:=args.get("localfile_path"):
        md5hash = localfile_path.split("/")[-1].split(".")[0]
    elif args.get("md5hash"):
        md5hash = args.get("md5hash")
    if md5hash:
        try:
            res = es_cli.search(VIT_INDEX, query={"match": {"ids": md5hash}})
        except:
            return {"detail": f"{md5hash} not found"}
        if res["hits"]["total"]["value"] == 0:
            return {"detail": f"{md5hash} not found"}
        query_vector = res["hits"]["hits"][0]["_source"]["vit"]

    if not query_vector:
        return {"detail": "no query vector"}
    
    k = args.get("count", 20)

    KNN_QUERY["query_vector"] = query_vector
    KNN_QUERY["k"] = int(k)

    try:
        res = await es_cli.search(
            index=VIT_INDEX,
            knn=KNN_QUERY
        )
    except Exception as e:
        logger.warning("knn search error: \n" + str(e))
    if res["hits"]["total"]["value"] == 0:
        return {"detail": "no result"}
    return {"detail": "success", "data": res["hits"]["hits"]}
