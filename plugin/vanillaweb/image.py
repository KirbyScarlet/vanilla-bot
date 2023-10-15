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
from nonebot import require
from httpx import AsyncClient

asyncclient = AsyncClient(timeout=30)

from .main import *

require("elasticsearch")
from ..elasticsearch import es_cli
from ..elasticsearch.config import es_config
require("minio")
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
    if len(localfile_path)==32:
        r = await es_cli.search(index=IMAGEMETA_INDEX, query={"ids": {"values": [localfile_path]}})
        if r["hits"]["total"]:
            localfile_path = r["hits"]["hits"][0]["_source"]["localfile_path"]
        else:
            localfile_path = ""
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
      ids: md5sum
    ===
    method: "similar_image"
    args:
      *#1 query_vector: [...]
      *#1 localfile_path
      *#1 md5sum
      * k: number
    """
    method: str = ""
    args: Mapping[str, Any] | None

@app.post(PREFIX + "/image")
async def image_post(request: ImageRequest):
    match request.method:
        case "unchecked_image":
            return await get_unchecked_image(request.args)
        case "similar_image":
            return await similar_image(request.args)
        case _:
            return {"detail": f"undefined method {request.method}"}
        
UNCHECKED_QUERY = {
    "bool": {
        "must_not": {
            "exists": {
                "field": "checked"
            }
        }
    }
}
IMAGEMETA_INDEX = minio_config.minio_es_image_metadata_indice.format(version="*")

async def get_unchecked_image(args: Mapping[str, Any]|None):
    if args:
        size = args.get("count", 10)
    else:
        size = 20
    try:
        res = await es_cli.search(
            index=IMAGEMETA_INDEX,
            query=UNCHECKED_QUERY,
            sort=[{"_script": {"script": "Math.random()","type": "number","order": "asc"}}],
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
    "num_candidates": 1000,
    "query_vector": []
}
VIT_INDEX = minio_config.minio_es_vit_indice.format(version="*")

async def similar_image(args: Mapping[str, Any]|None):
    logger.info("similar image args: " + str(args))
    if not args:
        return {"detail": "no args"}
    if q:=args.get("query_vector"):
        query_vector = q
    if localfile_path:=args.get("localfile_path"):
        md5sum = localfile_path.split("/")[-1].split(".")[0]
    elif args.get("md5sum", None):
        md5sum = args.get("md5sum")
    else:
        return {"detail": "check your args", "args": args}
    if md5sum:
        try:
            query_image = await es_cli.search(index=VIT_INDEX, query={"ids": {"values": [md5sum]}})
        except Exception as e:
            return {"detail": "image found error", "error": str(e)}
        if query_image["hits"]["total"]["value"] == 0:
            return {"detail": f"{md5sum} not found"}
        query_vector = query_image["hits"]["hits"][0]["_source"]["vit"]

    if not query_vector:
        return {"detail": "no query vector"}
    
    k = args.get("count", 20)

    KNN_QUERY["query_vector"] = query_vector
    KNN_QUERY["k"] = int(k)
    #logger.info("knn_query: "+str(KNN_QUERY))

    try:
        # res = await es_cli.search(
        #     index=VIT_INDEX,
        #     knn={
        #         "field": "vit",
        #         "k": k,
        #         "num_candidates": 10000,
        #         "query_vector": query_vector
        #     },
        #     timeout="20s",
        #     size=k
        # )
        res = await es_cli.search(
            index=VIT_INDEX,
            query={
                "script_score": {
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'vit') + 1.0",
                        "params": {
                            "query_vector": query_vector
                        }
                    },
                    "query": {
                        "match_all": {}
                    }
                }
            },
            size=20
        )
        logger.info(res["hits"]["total"])
        md5sums = [{"_id":hit["_id"]} for hit in res["hits"]["hits"]]
        logger.info("hits: "+str(len(md5sums)))
        return {"detail": "success", "data": md5sums}
    except Exception as e:
        logger.warning("knn search error: " + str(e))
        return {"detail": "knn search error", "error": str(e)}
    try:
        im_res = await es_cli.search(
            index=IMAGEMETA_INDEX,
            query={"ids":{"values": md5sums}},
            size=k
        )
    except Exception as e:
        logger.warning("image meta search error: " + str(e))
        return {"detail": "image meta search error", "error": str(e)}
    if im_res["hits"]["total"]["value"] == 0:
        return {"detail": "no result"}
    return {"detail": "success", "data": im_res["hits"]["hits"]}
