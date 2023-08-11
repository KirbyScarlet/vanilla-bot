from wolframclient.evaluation import WolframLanguageAsyncSession
from wolframclient.language import wl,wlexpr
import asyncio
import time
import pathlib
from nonebot.adapters.onebot.v11 import MessageSegment


async def calc(code):
    sess = WolframLanguageAsyncSession("/home/kirby/Mathematica/Executables/MathKernel")
    await sess.evaluate('Clear["Global`*"];Remove["Global`*"];')
    compute = await sess.evaluate_future(code)
    res = await compute.result(timeout=60)
    print(res)
    #if "Graphics" in res.__str__():
    fname = f"{pathlib.Path.cwd()}/data/mathematica/img{time.time_ns()}.png"
    await sess.evaluate(wl.Export(fname, res, "PNG"))
    if pathlib.Path(fname).exists():
        res = MessageSegment.image("file://"+fname)
    else :
        res = MessageSegment.text(str(res))
    #await sess.terminate()
    await sess.stop()
    return res


