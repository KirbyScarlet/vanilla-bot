import torch
import cn_clip.clip as clip

from PIL import Image

import asyncio
from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor(max_workers=1)

model, preprocess = clip.load_from_name("ViT-L-14",device="cpu")

def _predict(image: Image, device="cpu"):
    input = preprocess(image).unsqueeze(0).to(device)
    image_features = model.encode_image(input)
    return image_features.tolist()[0]

def _text_to_image_features(text: str, device="cpu"):
    input = clip.tokenize([text]).to(device)
    text_features = model.encode_text(input)
    return text_features.tolist()[0]

async def predict(image: Image = None, text: str = None, device="cpu"):
    if image:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(pool, _predict, image, device)
    elif text:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(pool, _text_to_image_features, text, device)
    else:
        raise ValueError("image或text需要指定一个")
    return result