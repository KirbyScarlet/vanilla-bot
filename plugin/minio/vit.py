# 获取图片的向量信息
# 默认使用 "google/vit-base-patch16-224"

from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import asyncio
from numpy.typing import ArrayLike
import concurrent.futures

from .config import minio_config

pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

processor = ViTImageProcessor.from_pretrained(minio_config.vit_model_path)
model = ViTForImageClassification.from_pretrained(minio_config.vit_model_path)

def predict(image: Image) -> ArrayLike:
    #image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    vectors = logits.detach().numpy().tolist()[0]
    return vectors

async def predict_async(image_path):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(pool, predict, image_path)
    return result

if __name__ == "__main__":
    import sys
    img = sys.argv[1]
    imgio = Image.open(img)
    print(predict(imgio))
