import json
from websockets.legacy.server import WebSocketServerProtocol
from typing import Any

import handlers.utils as utils

# `CHATROOMS` links from a gameID to a list of messages
# CHATROOMS = {
#     gameID: [
#         {"username": str,
#          "message": str},
#         ...
#     ],
#     ...
# }
CHATROOMS = {}

async def handle_chatroom(websocket, event):
    match event["type"]:
        case "create":
            create(websocket, event)
        case "join":
            await join(websocket, event)
        case "message":
            await send_message(websocket, event)
        case _:
            await error(websocket, event)

def create(websocket, event):
    gameID = int(event["gameID"])
    CHATROOMS[gameID] = []

async def join(websocket: WebSocketServerProtocol, event):
    gameID = int(event["gameID"])
    try:
        message_list = CHATROOMS[gameID]
        response = {
            "type": "game_state",
            "message_list": message_list,
        }
        await websocket.send(json.dumps(response))
    except KeyError:
        print(f"Error could not find chatroom {gameID}")

async def send_message(websocket: WebSocketServerProtocol, event: dict[str, Any]) -> None:
    gameID = int(event["gameID"])
    userID = int(event["userID"])
    message = {
        "username": utils.get_username(userID),
        "message": event["message"]
    }
    try:
        CHATROOMS[gameID].append(message)
    except KeyError:
        print(f"Error could not find chatroom {gameID}")
    try:
        connected: list[WebSocketServerProtocol] = list(
            utils.websockets_from_gameID(gameID).values()
        )
        response = {
            "type": "update",
            "message": message
        }
        for websocket in connected:
            await websocket.send(json.dumps(response))
    except KeyError:
        print(f"Error could not find game {gameID}")
        event = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(event))

async def error(websocket, event) -> None:
    print("Error handling event")
