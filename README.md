<div style="text-align:center;">

<!-- <img src="" alt="" width="200" height="200"> -->
$$
\begin{matrix}
  & \wedge & & \wedge &  \\
  & & & & \\
  & \geq & & \leq & \\
\equiv & & & & \equiv \\
  & & \omega & & \\
\end{matrix}
$$

# vanilla bot

</div>

此项目基于 `nonebot2` 开发

完整文档请参考 https://vanilla.wiki (如果无法访问，那就是还没施工完毕)

## 0xFF 叠甲

**考虑到一些不可明说的原因，可能随时跑路。**

**本项目涉及存储机器人的记录信息，[作者本人](https://github.com/KirbyScarlet)不会以任何方式收集机器人数据。**

**本项目存储的数据请勿用于非法用途。使用本项目造成的法律后果，与本项目无关。**

**本项目的数据没有任何加密手段，请勿用于法律目的。**

**本项目仅用于学习目的，使用本项目造成的损失，与本项目无关。**

## 0x00 这是什么\xbf\xbf\xbf

保存机器人产生的所有聊天记录信息，包括文字，图片等。并添加了聊天记录分析，图片整理等功能。

使用 [ElasticSearch](https://elastic.co/) 保存聊天记录，以及图片的元数据和特征向量。可选用 [MinIO](https://min.io) 或本地直接保存图片，视频等二进制文件。

## 0x01 这能干啥\xbf\xbf\xbf

#### 打算实现或已实现

- 收集并保存聊天记录
- 图片信息使用对象存储保存
- 图片内容的文字识别
- 图片生成向量信息并保存
- 聊天记录词云
- 模糊搜索聊天记录
- 图片内容搜索，图片向量搜索
- 一个管理界面，可以手动分类图片或搜索图片
- 更多adapter的聊天记录适配
- ...

#### 不打算实现

- 抢红包等一切和现金有关的操作
- 批量发送消息等可能导致误封的操作
- ...

## 0x02 这怎么装\xbf\xbf\xbf

#### 0b00 要装哪些？

- [python3.10+](https://www.python.org/downloads/)
- [nonebot2](https://github.com/nonebot/nonebot2)
- [elasticsearch](https://elastic.co)
- [minio](https://min.io) (可选)
- [nvidia driver](https://www.youtube.com/watch?v=MShbP3OpASA&t=2997s) (看情况)
<!-- so nvidia f*** you -->

#### 0b01 python3

请根据您的操作系统类型安装 `3.10` 以上的python版本。`conda`也可以。`pypy`未测试。

推荐使用 `venv` 或 `conda` 管理虚拟环境。

```shell
# 克隆代码
git clone https://github.com/KirbyScarlet/vanilla-bot.git
cd vanilla-bot
```

```powershell
## 根据操作系统类型激活虚拟环境
# windows
python -m venv venv
py -3.x -m venv venv  # 此处根据windows的环境变量，可能会有不同的命令
.\venv\Script\Activate.bat
# linux
python3 -m venv venv
source venv/bin/activate
```

```shell
(venv) pip install -r requirements.txt
```

#### 0b02 elastic search

参考 [官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html) 安装。

推荐使用 `docker` 安装。

根据作者的个人测试，一年份20个活跃群的聊天记录事件消息总量约5G，图片约110万张，累计700G。图片向量库占用约17G。请根据自身情况控制存储空间。

#### 0b03 minio

参考 [官方文档](https://docs.min.io/docs/minio-client-complete-guide) 安装。

推荐使用 `docker` 安装。

## 0x03 这怎么用\xbf\xbf\xbf

详细文档在这里 https://vanilla.wiki (如果无法访问，那就是还没施工完毕)

#### 0b00 机器人配置

要改的配置文件不多，我尽量做到一条配置不改能直接一键启动。

#### 0b01 机器人命令

考虑到机器人需要处理自己发送的消息，默认使用的命令前缀建议增加复杂度，避免因意外导致自发消息递归触发。如默认为字符串 `#!/`。以下命令不考虑命令前缀。

- nonebot-plugin-message 相关命令

```shell
message blacklist [@群成员] [--del]
# 查看不收集列表 [不收集某成员消息，用于该成员同时也是机器人等情况] [从不收集列表中移除某成员]
message at [@群成员] [数量]
# 查看群成员最近[几次]被@的记录
message reply [回复消息]
# 查看某回复消息的回复树
message search [关键词] [--asc] [--desc] [--limit=3]
# 查找谁[最先][最后]讲过某关键词
```
```shell
image [关键词] 
# 以关键词模糊搜图
image [-e] [关键词]
# 衣蛾关键字精确搜图
image --knn [图片|回复消息]
# 以图搜图
image --ocr [图片|回复消息]
# 文字识别，直接返回文字
```

- nonebot-plugin-self-management 相关命令

```shell
plugin list
# 已启动的插件
plugin enable|disable [插件名]
# 启用或禁用插件
```
```shell
status [cpu|gpu|mem|disk|sensor]
# 机器人后端系统状态
```

- nonebot-plugin-elasticsearch 和 nonebot-plugin-minio 相关命令

```shell
es [url] [json|kql]
# 以json格式向elasticsearch发送请求 
# 例如 es /index/search {"query": {"match_all": {}}, "limit": 1}
```

```shell
## 暂时先这么写着，应该不会这样实现，或者不放开接口
minio get [桶名] [对象名]
# 直接上传到群文件或发送文件
minio put [桶名] [对象名] [reply id]
# 从回复消息的文件上传到minio
```

- nonebot-plugin-webclient 相关命令

```shell
## 给webclient发弹窗 （狗头）
webclient [消息]
```

#### 0b02 后台管理界面

bot启动完成后，访问 `http://127.0.0.1:8086/vanilla/bot` 可进入后台管理界面。端口和uri可在配置文件中修改。

不用文档，看了界面就懂了。

##  0x04 特别感谢

- [@DiaoDaiaChan](https://github.com/DiaoDaiaChan) 第一个尝试我的机器人，我很佩服第一个发现蘑菇能吃的人，说不定是有毒的呢！


### EOF