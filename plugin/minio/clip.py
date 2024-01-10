# 获取图片的向量信息
# 默认使用OFA-Sys/chinese-clip-vit-large-patch14
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import asyncio
import concurrent.futures
from typing import TypeAlias
from numpy.typing import ArrayLike

IMAGE_FEATURE: TypeAlias = ArrayLike
TEXT_FEATURE: TypeAlias = ArrayLike

from .config import minio_config

pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)

processor = CLIPProcessor.from_pretrained(minio_config.minio_clip_model_path)
model = CLIPModel.from_pretrained(minio_config.minio_clip_model_path)

if minio_config.minio_clip_gpu:
    model = model.cuda()

def feature(image: Image) -> [IMAGE_FEATURE, TEXT_FEATURE]:
    inputs = processor(images=image, return_tensors="pt", padding=True)
    if model.device.type == "cuda":
        inputs = inputs.pixel_values.to("cuda")
    elif model.device.type == "cpu":
        inputs = inputs.pixel_values
    image_feature = model.get_image_features(inputs)
    text_feature = model.get_text_features(inputs)
    image_feature = image_feature / image_feature.norm(dim=-1, keepdim=True)
    text_feature = text_feature / text_feature.norm(dim=-1, keepdim=True)
    return image_feature[0], text_feature[0]

async def get_features_async(image: Image) -> [IMAGE_FEATURE, TEXT_FEATURE]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(pool, feature, image)

if __name__ == "__main__":
    import sys
    img = sys.argv[1]
    imgio = Image.open(img)
    image_feature, text_feature = feature(imgio)
    print(image_feature, text_feature)