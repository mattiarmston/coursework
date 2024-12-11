import json
import random

import games, server

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
            await error(websocket, event)

def create(websocket, event):
    gameID = int(event["gameID"])
    game_state = {
        "players": [
        ],
    }
    WHIST[gameID] = game_state

def random_card() -> str:
    suit = random.choice(["C", "D", "H", "S"])
    rank = random.choice([str(i) for i in range(2, 10) ] + ["T", "J", "Q", "K", "A"])
    return rank + suit

async def join(websocket, event):
    gameID = int(event["gameID"])
    userID = int(event["userID"])
    try:
        connected: set[WebSocketServerProtocol] = set(games.get_websockets(gameID).values())
    except KeyError:
        print(f"Error could not find {gameID}")
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
    if not exists:
        player = {
            "userID": userID,
        }
        game_state["players"].append(player)
    # 2 players should not be able to join simultaneously so this should work
    if len(games.get_userIDs(gameID)) != 4:
        await waiting(websocket, event)
        return
    await test_game_state(websocket, event)

async def waiting(websocket, event):
    gameID = int(event["gameID"])
    usernames: list[str] = [
        games.get_username(userID, server.app) for userID in games.get_userIDs(gameID)]
    print(usernames)
    players: list[dict[str, str]] = []
    for username in usernames:
        players.append({"username": username})
    print(players)
    try:
        connected: set[WebSocketServerProtocol] = set(games.get_websockets(gameID).values())
        response = {
            "type": "waiting",
            "no_players": len(connected),
            "players_required": 4,
            "players": players,
        }
        responseJSON = json.dumps(response)
        for websocket in connected:
            await websocket.send(responseJSON)
    except KeyError:
        print(f"Error could not find {gameID}")
        response = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(response))

def game_state_for_user(game_state: dict[str, Any], userID: int) -> str:
    copy: dict[str, Any] = {"type": "game_state"}
    for key, value in game_state.items():
        if key != "players":
            copy[key] = value
            continue
        if key == "players":
            copy["players"] = []
            for player in game_state["players"]:
                copy_player = {}
                for k, v in player.items():
                    if k not in ["hand", "userID"]:
                        copy_player[k] = v
                        continue
                    if k == "userID":
                        copy_player["username"] = games.get_username(v, server.app)
                        continue
                    if player["userID"] == userID:
                        copy_player["hand"] = player["hand"]
                        copy["current_user"] = game_state["players"].index(player)
                    else:
                        copy_player["hand"] = [ "" for _ in player["hand"] ]
                    copy["players"].append(copy_player)
    print(f"{userID} {copy}")
    return json.dumps(copy)

async def broadcast_game_state(gameID: int) -> None:
    game_state = WHIST[gameID]
    print(f"{game_state}")
    for userID, websocket in games.get_websockets(gameID).items():
        game_stateJSON = game_state_for_user(game_state, userID)
        await websocket.send(game_stateJSON)

async def test_game_state(websocket, event):
    gameID = int(event["gameID"])
    try:
        connected: set[WebSocketServerProtocol] = set(games.get_websockets(gameID).values())
    except KeyError:
        print(f"Error could not find {gameID}")
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
    await broadcast_game_state(gameID)

async def error(websocket, event):
    print("Error handling event")
