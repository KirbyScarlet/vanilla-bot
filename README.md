
<p align="center">
    <img src="vanillabot-line.png" alt="vanilla-bot" width="200" height="200">
</p>

<div align="center">

# vanilla-bot

</div>

此项目基于 `nonebot2` 开发

## 0. 叠甲&怨念

**本项目具有特殊性，可能随时跑路**

**本项目存储的所有数据没有任何防伪手段，仅被动接收所有信息并进行整理。任何在使用本项目过程中造成的法律后果，与本项目无关**

**本项目存储的所有信息不具有任何法律效力，禁止用于任何法律途径**

**本项目仅用于学习目的，禁止用于商业用途**

## 1. 这是什么\xbf\xbf\xbf

因为手机或电脑的聊条记录过于累赘，动辄占用大几十G空间，所以考虑开发一个能收集整理聊天记录的机器人。

由于[OneBot标准](https://onebot.dev)中各种消息段定义的多样性，放弃使用结构化数据库保存聊天记录。综合考虑后，决定使用 [elasticsearch](https://elastic.co) 保存所有 `nonebot.adapters.Event` 上报的事件内容（聊天记录，进退群等），使用对象存储 [minio](https://min.io) 保存所有的图片、视频、语音等二进制文件内容。

## 2. 这能干啥\xbf\xbf\xbf

#### 已实现：

- 收集并保存聊天记录
- 图片信息使用对象存储保存
- 图片内容的文字识别
- 图片生成向量信息并保存
- ...

#### 打算实现：

- 聊天记录词云
- 模糊搜索聊天记录
- 图片内容搜索，图片向量搜索
- 一个管理界面，可以手动分类图片或搜索图片
- 更多adapter的聊天记录适配
- plugin.elasticsearch 和 plugin.minio 作为独立模块单独发布
- ...

#### 不会实现：

- 会实现的功能

## 3. 这怎么用\xbf\xbf\xbf （后续再写完整的安装命令，绝不是因为我自己还没测）

#### （1）安装 elasticsearch (>8.0) [官网链接](https://www.elastic.co/guide/en/elasticsearch/reference/8.9/install-elasticsearch.html) 此处更推荐docker安装。kibana 非必须，但推荐安装。

__若使用 docker 方式安装 elasticsearch，推荐将配置文件和数据目录映射至本地__

__kibana 不产生应用数据，可不映射目录__

本地局域网环境可以不开启安全验证，修改配置文件<br>
`/path/to/your/elasticsearch/config/elasticsearch.yml`

```ini
xpack.security.enabled: false
xpack.security.enrollment.enabled: false
```

机器人配置文件 `.env` 添加配置

```ini
ES_HOSTS = ["http://127.0.0.1:9200"]
```

如果<b>开启安全验证</b>，则需要获取 api key，用于机器人连接 elasticsearch<br>
若已安装 kibana ，可在 kibana 的 Dev Tools - Console 执行以下命令获取 api key

elasticsearch 的首次启动日志打印了默认密码，默认kibana使用的apikey，请妥善保管第一份日志

```DSL
POST _security/api_key
{
    "name": "nonebot"
}
```

若未安装 kibana ，则需要输入命令获取 api key，其中 `elastic` 的密码可在第一次启动 elasticsearch 时获取

```shell
$ curl -u elastic:YOUR_PASSOWRD -XPOST -k -H 'Content-Type: application/json' https://127.0.0.1:9200/_security/api_key -d "{\"name\": \"nonebot\"}"
```

以上方法返回的 json 如下：__此处仅为示例，请根据实际返回数据做后续修改__

```json
{
    "id": "H91v3YkBHZt5o7qfE_nW",
    "name": "nonebot",
    "api_key": "SbYGR5PuQcKBWTlPBUTacA",
    "encoded": "SDkxdjNZa0JIWnQ1bzdxZkVfblc6U2JZR1I1UHVRY0tCV1RsUEJVVGFjQQ=="
}
```

将上述 json 中 `"encoded"` 字段的值填入 .env 的 ES_API_KEY 字段

```ini
ES_HOSTS = ["https://127.0.0.1:9200"]
ES_API_KEY = "SDkxdjNZa0JIWnQ1bzdxZkVfblc6U2JZR1I1UHVRY0tCV1RsUEJVVGFjQQ=="
```

还需要安装[中文分词器](https://github.com/medcl/elasticsearch-analysis-ik)，比较傻瓜，跟着页面很快就能装好

#### （2）安装 minio [官网链接](https://min.io/download) 此处依然推荐使用docker安装

__若使用 docker 方式安装，推荐将配置文件和数据目录映射至本地__

安装完成后需要手动生成 minio 的 access_key。

浏览器访问 minio 的控制台后端，点击 `Access Keys` - `Create access key`，新界面中点击 `Create`。

请根据提示妥善保管 `secretKey` __此处仅为示例，请根据实际返回数据做后续修改__

```json
{
    "url":"http://127.0.0.1:9000",
    "accessKey":"9qY52HV8DvJaO7pGPLjx",
    "secretKey":"SMaG5VxBNUSlsXnhtEbIwZdZWZAy8PhyRR9y5MuW",
    "api":"s3v4",
    "path":"auto"
}
```

其中 `accessKey` 字段和 `secretKey` 字段的内容添加进 `.env`

```ini
MINIO_HOST = "127.0.0.1:9000"
MINIO_ACCESS_KEY = "YOUR_MINIO_ACCESS_KEY"
MINIO_SECRET_KEY = "YOUR_MINIO_SECRET_KEY"
```

再进入 `buckets` 页签，选择图片buckets，修改访问权限为public，则后续可直接使用网页链访问存储内容。

#### (3) 安装依赖并启动机器人

```shell
$ pip3 install -r requirements.txt
$ python3 vanilla.py
```

QQ客户端 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 配置文件的 `service` 项添加ws连接

支持多个qq客户端连接同一个后端。文字消息会根据 `bot.self_id` 区分记录

图片消息不区分发送人，hash相同的图片仅保存一份

```yaml
  - ws-reverse:
      universal: ws://127.0.0.1:8083/onebot/v11/ws/
```

## 4. 怎么找消息\xbf\xbf\xbf

#### （1）机器人命令

已经实现了一个最基本的文字找图，受限于图片格式，暂时对png和gif的识别还有点问题。<br>
机器人一体机发送命令：

```
#!/image 为了我们的友谊干杯
#!/image 几万 电脑 玩这个
```

机器人将会以识别的ocr文本中查找最小字数匹配并随后发送。

#### （2）基于kibana搜索 [kibana文档](https://www.elastic.co/guide/en/kibana/current/index.html)

如果你安装了 `kibana` ，可在kibana界面内添加 `data view`, 索引过滤 `vanillabot-message-*`，查找文字信息。

索引过滤 `vanillabot-image-metadata-*`, 可手动添加脚本字段，并根据 `filepath` 字段的值，从本地minio请求图片数据。

```
URL template:
    http://192.168.1.6:9000/vanillabot-image/{{rawValue}}
script:
    field('filepath').get(null)
```
（minio的图片bucket需要设置访问权限为public）

#### （3）机器人自己的网页

由于 `nonebot2` 的特性，可以直接将nonebot当作网络服务的后端，可直接无缝对接网络服务。

浏览器直接访问 `http://127.0.0.1:8083/vanilla/bot` 进入机器人后端主页。此处的端口为 `.env` 文件中定义的 `PORT` 参数。

__由于nonebot2官方的[管理页面](https://nb2.baka.icu/docs/next/ospp/2023#nonebot-%E9%A1%B9%E7%9B%AE%E7%AE%A1%E7%90%86%E5%9B%BE%E5%BD%A2%E5%8C%96%E9%9D%A2%E6%9D%BF)项目还咕着，我这儿先就这么用，后续官方网页发布后，将做后续兼容处理。__

## 5. 后续计划\xbf\xbf\xbf

写一行算一行呗，还能有啥计划，又不是说鸽就鸽。

## 6. 特别感谢！

[@DiaoDaiaChan](https://github.com/DiaoDaiaChan) 第一个尝试我的机器人，我很佩服第一个发现蘑菇能吃的人，说不定是有毒的呢！

## EOF