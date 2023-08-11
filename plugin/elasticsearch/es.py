###

from nonebot import get_bot
from nonebot import get_driver
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11 import Bot,Event, MetaEvent

from elasticsearch import AsyncElasticsearch

from .config import es_config

import datetime
from time import time
from pydantic import BaseModel

es_cli = AsyncElasticsearch(
    hosts=es_config.es_hosts, 
    api_key=es_config.es_api_key, 
    verify_certs=False)

driver = get_driver()

@driver.on_bot_connect
async def check_index_exists(bot: Bot):
    exist = await es_cli.indices.exists(index=f"qq-message-{bot.self_id}")
    if not exist:
        await es_cli.indices.create(
            index=f"qq-message-{bot.self_id}",
            mappings=es_config.es_keywords_index_properties
            )

class Document(BaseModel):
    pass

@event_preprocessor
async def upload_es(event: Event):
    #print(event.get_type(), event.get_event_name())
    document = event.dict()
    document["@timestamp"] = datetime.datetime.fromtimestamp(event.time) - datetime.timedelta(hours=8)
    if event.post_type == "meta_event":
        return
    if event.post_type == "message":
        if document.get("original_message"): 
            del document["original_message"]
        if document.get("raw_message"): 
            del document["raw_message"]
        if document.get("reply"):
            document["reply"]["message"] = str(document["reply"]["message"])
        document["message"] = str(document["message"])
        if event.get_type()=="message":
            document["plain_text"] = event.get_plaintext()
        # document["original_message"] = str(document["original_message"])
        # document["raw_message"] = str(document["raw_message"])
    
    # pprint(event.get_message())
    # pprint(event.dict())
    #pprint(document)

    await es_cli.index(
        index=f"qq-message-{event.self_id}",
        document=document
    )