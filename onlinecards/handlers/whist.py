import json
import random

import handlers.utils as utils
from games.whist import broadcast_game_state, get_whist_func

from typing import Any
from websockets import WebSocketServerProtocol

# from .. import games.whist

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
            await error(websocket, event)

def create(websocket, event):
    gameID = int(event["gameID"])
    func = get_whist_func()
    game_state = {
        "players": [
        ],
        "func": func,
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
    if exists:
        await broadcast_game_state(gameID, game_state)
        return
    player = {
        "userID": userID,
    }
    game_state["players"].append(player)
    # 2 players should not be able to join simultaneously so this should work
    if len(utils.get_userIDs(gameID)) != 4:
        await waiting(websocket, event)
        return
    func = game_state["func"]
    await func(gameID, game_state)

async def waiting(websocket, event):
    gameID = int(event["gameID"])
    try:
        players: list[dict[str, Any]] = WHIST[gameID]["players"]
        response = {
            "type": "waiting",
            "no_players": len(players),
            "players_required": 4,
            "players": players,
        }
        await broadcast_game_state(gameID, response)
    except KeyError:
        print(f"Error could not find whist game {gameID}")
        response = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(response))

def random_card() -> str:
    suit = random.choice(["C", "D", "H", "S"])
    rank = random.choice([str(i) for i in range(2, 10) ] + ["T", "J", "Q", "K", "A"])
    return rank + suit

async def test_game_state(websocket, event):
    gameID = int(event["gameID"])
    try:
        connected: set[WebSocketServerProtocol] = set(utils.websockets_from_gameID(gameID).values())
    except KeyError:
        print(f"Error could not find whist game {gameID}")
        response = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(response))
    game_state = WHIST[gameID]
    for player in game_state["players"]:
        player["bid"] = random.randint(0, 10)
        player["tricks_won"] = random.randint(1, 5)
        player["hand"] = [ random_card() for _ in range(5) ]
    await broadcast_game_state(gameID, game_state)

async def error(websocket, event):
    print("Error handling event")
