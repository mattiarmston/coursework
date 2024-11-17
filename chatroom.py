import json
from websockets.legacy.server import WebSocketServerProtocol
from typing import Any

import games

async def handle_chatroom(websocket, event):
    match event["type"]:
        case "message":
            await send_message(websocket, event)
        case _:
            await error(websocket, event)

async def send_message(websocket: WebSocketServerProtocol, event: dict[str, Any]) -> None:
    gameID = int(event["gameID"])
    try:
        connected = games.GAMES[gameID]
        eventJSON = json.dumps(event)
        for websocket in connected:
            await websocket.send(eventJSON)
    except KeyError:
        print(f"Error could not find {gameID}")
        event = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(event))

async def error(websocket, event) -> None:
    print("Error handling event")
