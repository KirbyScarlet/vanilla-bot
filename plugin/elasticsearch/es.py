###

from pydantic import BaseModel
from time import time
import datetime
from .config import es_config
from elasticsearch import AsyncElasticsearch
from nonebot.adapters.onebot.v12 import Event as Eventv12
from nonebot.adapters.onebot.v12 import Bot as Botv12
from nonebot.adapters.onebot.v11 import MetaEvent as MetaEventv11
from nonebot.adapters.onebot.v11 import Event as Eventv11
from nonebot.adapters.onebot.v11 import Bot as Botv11
from nonebot.adapters import Bot
from nonebot.message import event_preprocessor
from nonebot import get_driver
from nonebot import get_bot
from nonebot.typing import T_State

VERSION = "v0.1.1"


es_cli = AsyncElasticsearch(
    hosts=es_config.es_hosts,
    api_key=es_config.es_api_key,
    verify_certs=False
)

driver = get_driver()


@driver.on_bot_connect
async def check_index_exists(bot: Bot):
    index_name = es_config.es_message_indice_name.format(
        self_id=bot.self_id,
        version=VERSION
    )
    exist = await es_cli.indices.exists(index=index_name)
    if not exist:
        await es_cli.indices.create(
            index=index_name,
            mappings=es_config.es_keywords_index_properties
        )


class Document(BaseModel):
    pass


@event_preprocessor
async def upload_es(bot: Botv11, event: Eventv11, state: T_State):
    document = event.dict()
    document["@timestamp"] = datetime.datetime.utcfromtimestamp(event.time)
    if event.post_type == "meta_event":
        return
    if hasattr(event, "convert") or state.get("convert"):
        return
    if event.post_type == "message":
        try:
            if event.get_user_id() == bot.self_id:
                return
        except:
            if str(event.self_id) == bot.self_id:
                return
        if document.get("original_message"):
            del document["original_message"]
        if document.get("raw_message"):
            document["message"] = document["raw_message"]
            del document["raw_message"]
        if document.get("reply"):
            document["reply"]["message"] = str(document["reply"]["message"])
        document["message"] = str(document["message"])
        if event.get_type() == "message":
            document["plain_text"] = event.get_plaintext()
        # document["original_message"] = str(document["original_message"])
        # document["raw_message"] = str(document["raw_message"])

    # pprint(event.get_message())
    # pprint(event.dict())
    # pprint(document)

    await es_cli.index(
        index=es_config.es_message_indice_name.format(
            self_id=bot.self_id,
            version=VERSION
        ),
        document=document
    )
