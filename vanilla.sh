#!/bin/bash

# 一键环境部署和启动

# 临时记录，还不能用

#========================
#
## 手动开启/停止/重启文字识别和特征提取
# ./vanilla.sh core [start|stop|restart|status]
#
## 自动安装机器人依赖
# ./vanilla.sh install
#
#========================

install() {
docker run --name es8.17_1 --net es8.17 -p 8092:9200 -it -m 8GB -v "/mnt/disk01/es8.17/data:/usr/share/elasticsearch/data" -v "/mnt/disk01/es8.17/logs:/usr/share/elasticsearch/logs" -v "/mnt/disk01/es8.17/plugins:/usr/share/elasticsearch/plugins" docker.elastic.co/elasticsearch/elasticsearch:8.17.0

docker run --name kb8.17 --net es8.17 -p 5601:5601 docker.elastic.co/kibana/kibana:8.17.0

TOKEN=`docker exec -it es8.17_1 /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s node`

docker run --name es8.17_2 --net es8.17 -p 8192:9200 -it -m 8GB -v "/mnt/disk02/es8.17/data:/usr/share/elasticsearch/data" -v "/mnt/disk02/es8.17/logs:/usr/share/elasticsearch/logs" -v "/mnt/disk02/es8.17/plugins:/usr/share/elasticsearch/plugins" -v "/mnt/disk02/es8.17/config:/usr/share/elasticsearch/config" -e ENROLLMENT_TOKEN="eyJ2ZXIiOiI4LjE0LjAiLCJhZHIiOlsiMTcyLjE5LjAuMjo5MjAwIl0sImZnciI6ImJmNmM1ZTlkYWFlMzk0ZmJkMjJhNWQ5YWU3YzYwOWQ0ZWUzNzU4ZGU0ODg4ZDdjZDhiYzIwOWY1MmU3OTNiOTAiLCJrZXkiOiJmeTFvLVpRQlNmX1U5N3FGbS13TjpsU0JxaXNDalNnbVhEOUdiTExnMnRBIn0=" docker.elastic.co/elasticsearch/elasticsearch:8.17.0

docker run -dt                                  \
  -p 8900:9000 -p 8901:8901                     \
  -v /mnt/mdisk01/minio:/data                   \
  -v /home/kirby/.config/minio:/etc/config.env  \
  -e "MINIO_CONFIG_ENV_FILE=/etc/config.env"    \
  --name "minio_local"                          \
  minio/minio:latest server --console-address ":8901"
}

core() {
  python3 vanilla_core/ocr/api.py &
  python3 vanilla_core/characteristic/api.py &
}