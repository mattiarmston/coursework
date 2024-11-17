import json
from websockets.legacy.server import WebSocketServerProtocol
from typing import Any

import games
print(id(games.GAMES))

# CHATROOMS = {
#     gameID: {
#         "message_list": [
#             {"username": str,
#              "message": str,
#             },
#             ...
#         ]
#     }
# }
CHATROOMS: dict[int, dict[str, Any]] = {}

async def handle_chatroom(websocket, event):
    match event["type"]:
        case "create":
            pass
        case "join":
            pass
        case "message":
            await send_message(websocket, event)
        case _:
            await error(websocket, event)

async def create(websocket, event):
    gameID = int(event["gameID"])
    CHATROOMS[gameID] = {
        "message_list": []
    }

async def join(websocket, event):
    gameID = event["gameID"]
    try:
        message_list = CHATROOMS[gameID]["message_list"]
        response = {
            "type": "game_state",
            "message_list": message_list,
        }
    except KeyError:
        print(f"Error could not find {gameID}")
        response = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
    await websocket.send(json.dumps(response))

async def send_message(websocket: WebSocketServerProtocol, event: dict[str, Any]) -> None:
    eventJSON = json.dumps(event)
    gameID = int(event["gameID"])
    try:
        connected = games.GAMES[gameID]["connected"]
        for websocket in connected:
            await websocket.send(eventJSON)
        message = {
            "username": event["username"],
            "message": event["message"],
        }
        CHATROOMS[gameID]["message_list"].append(message)
    except KeyError:
        print(f"Error could not find {gameID}")
        event = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(event))
    return

async def error(websocket, event) -> None:
    print("Error handling event")
