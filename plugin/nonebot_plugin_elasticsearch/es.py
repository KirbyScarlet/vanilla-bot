#
__all__ = ["es_cli"]


from elasticsearch import AsyncElasticsearch
from .config import es_config

from nonebot import get_driver
from nonebot import on_command

elasticsearch_client = AsyncElasticsearch(
    hosts = es_config.es_hosts,
    api_key = es_config.es_api_key,
    verify_certs = es_config.es_verify_certs,
    **es_config.es_client_parameters
)

@get_driver().on_shutdown
async def es_shutdown():
    """
    为什么要多此一举把一个客户端封装成插件？
    因为总是忘记关
    如果不关，python进程不会真正的退出，需要等这逼玩意儿释放
    """
    await elasticsearch_client.close()

es_cli = on_command("es", aliases={"elasticsearch"})

class ESArguments():
    pass

@es_cli.handle()
async def es_cli_handle():
    pass