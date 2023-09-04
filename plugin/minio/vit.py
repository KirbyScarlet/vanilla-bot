# 获取图片的向量信息
# 默认使用 "google/vit-base-patch16-224"

from typing import Literal
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import asyncio
from numpy.typing import ArrayLike
import concurrent.futures

from .config import minio_config

pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

processor = ViTImageProcessor.from_pretrained(minio_config.minio_vit_model_path)
model = ViTForImageClassification.from_pretrained(minio_config.minio_vit_model_path)

def predict_cpu(image: Image) -> ArrayLike:
    #image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    vectors = logits.detach().numpy().tolist()[0]
    return vectors

def predict_gpu(image: Image) -> ArrayLike:
    #image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt").pixel_values
    pixel_values_cuda = inputs.half().cuda()
    outputs = model(pixel_values_cuda)
    logits = outputs.logits
    vectors = logits.cpu().detach().numpy().tolist()[0]
    return vectors

if minio_config.minio_vit_gpu:
    model.half().cuda()
    predict = predict_gpu
else:
    predict = predict_cpu

async def predict_async(image_path):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(pool, predict, image_path)
    return result

if __name__ == "__main__":
    import sys
    img = sys.argv[1]
    imgio = Image.open(img)
    print(predict(imgio))
