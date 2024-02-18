#

from nonebot.log import logger
from .config import message_core_config

match message_core_config.message_core_mapping_storage:
    case "elasticsearch":
        try:
            from . import es_api
        except ImportError:
            logger.error("请检查**")
        index_exists = es_api.check_index_exists
        create_index = es_api.create_index
        put_document = es_api.put_document

