##

from nonebot import get_driver
from nonebot.message import event_preprocessor
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.log import logger
from fastapi import FastAPI, WebSocket
from fastapi import WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Mapping, cast
from asyncio import Queue
from pathlib import Path
import json

driver = get_driver()

app: FastAPI = driver.server_app
PWD = Path(__file__).parent
PREFIX = "/vanilla/bot"

#cast(FastAPI, app)
app.mount(
    PREFIX + "/static",
    StaticFiles(directory=PWD / "web" / "static"), 
    name="static"
    )

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[WebSocket, str] = {}
        self.message_queue: dict[str, Queue[str]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if not self.have_active_connection(user_id):
            self.message_queue.update({user_id: Queue()})
        self.active_connections.update({websocket: user_id})

    def disconnect(self, websocket):
        user_id = self.active_connections.pop(websocket, None)
        if not self.have_active_connection(user_id):
            self.message_queue.pop(user_id, None)

    def have_active_connection(self, user_id: str = None):
        if user_id:
            return user_id in self.active_connections.values()
        else:
            return len(self.active_connections) > 0

manager = ConnectionManager()

@event_preprocessor
async def send_message_to_client(bot: Bot, event: Event, state: T_State):
    if manager.have_active_connection(bot.self_id):
        await manager.message_queue[bot.self_id].put(event.json())

@app.get(PREFIX + "/client")
async def homepage():
    return FileResponse(PWD / "web" / "index.html")

@app.websocket(PREFIX + "/client/{user_id}")
async def vanilla_client(ws: WebSocket, user_id: str):
    bots = driver.bots.values()
    if user_id in [bot.self_id for bot in bots]:
        await manager.connect(user_id, ws)
    else:
        return await ws.close(code=1008, reason="User not found")
    try:
        while True:
            event = await manager.message_queue[user_id].get()
            print(manager.active_connections)
            await ws.send_json(json.loads(event))
    except WebSocketDisconnect:
        manager.disconnect(ws)

@app.post(PREFIX + "/client/{user_id}/{method}")
async def bot_api(user_id: str, method: str, data: Mapping = None):
    bots = driver.bots.values()
    if user_id not in [bot.self_id for bot in bots]:
        return {"result": "User not found"}
    bot = driver.bots[user_id]
    try:
        if data is None:
            result = await getattr(bot, method)()
        else:
            result = await getattr(bot, method)(**data)
    except Exception as e:
        logger.error(f"Error while calling {method}: {e}")
        return {"result": "Error"}
    return {"result": result}

@app.post(PREFIX + "/client/active_connections")
async def get_active_connections():
    c = manager.active_connections.values()
    return {"result": list(c)}
