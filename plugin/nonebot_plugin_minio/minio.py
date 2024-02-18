#

from miniopy_async import Minio

from .config import minio_config

minio_cli = Minio(
    minio_config.minio_hosts,
    access_key=minio_config.minio_access_key,
    secret_key=minio_config.minio_secret_key,
    secure=minio_config.minio_secure
)