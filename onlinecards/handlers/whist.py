import json
import random

import handlers.utils as utils
from games.whist import broadcast_game_state, get_whist_event_handler, get_whist_state_handler

from typing import Any
from websockets import WebSocketServerProtocol

# `WHIST` links from a gameID to a whist game state
# WHIST = {
#     gameID: {
#         "players": [ ... ]
#         "trump_suit": str,
#         ...
#     },
#     ...
# }
WHIST: dict[int, dict[str, Any]] = {}

async def handle_whist(websocket, event):
    match event["type"]:
        case "create":
            create(websocket, event)
        case "join":
            await join(websocket, event)
        case _:
            gameID = int(event["gameID"])
            game_state = WHIST[gameID]
            event_handler = game_state["event_handler"](event["type"])
            state_handler = game_state["state_handler"]
            await event_handler(gameID, game_state, event)
            await state_handler(gameID, game_state, event)

def create(websocket, event):
    gameID = int(event["gameID"])
    event_handler = get_whist_event_handler()
    state_handler = get_whist_state_handler()
    game_state = {
        "players": [
        ],
        "event_handler": event_handler,
        "state_handler": state_handler,
        "state": None,
    }
    WHIST[gameID] = game_state

async def join(websocket, event):
    gameID = int(event["gameID"])
    userID = int(event["userID"])
    try:
        connected: set[WebSocketServerProtocol] = set(utils.websockets_from_gameID(gameID).values())
    except KeyError:
        print(f"Error could not find whist game {gameID}")
        response = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(response))
        return
    exists = False
    game_state = WHIST[gameID]
    for player in game_state["players"]:
        if player["userID"] == userID:
            exists = True
            break
    # I need a better system for rejoining games / reloading the page
    if exists:
        await broadcast_game_state(gameID, game_state)
        return
    player = {
        "userID": userID,
    }
    game_state["players"].append(player)
    # 2 players should not be able to join simultaneously so this should work
    if len(utils.get_userIDs(gameID)) != 4:
        waiting_event = {
            "type": "waiting",
            "gameID": gameID,
        }
        await handle_whist(websocket, waiting_event)
        return
    start_event = {
        "type": "start",
        "gameID": gameID,
    }
    await handle_whist(websocket, start_event)

async def error(websocket, event):
    print("Error handling whist event")
