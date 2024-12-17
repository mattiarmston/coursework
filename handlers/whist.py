import json
import random

import handlers.games as games
import server

from typing import Any, Callable
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

def censor_game_state(game_state: dict[str, Any], userID: int) -> str:
    def default(
        censored_state: dict[str, Any],
        game_state: dict[str, Any],
        key: str,
        userID: int,
    ) -> None:
        censored_state[key] = game_state[key]

    def censor_hand(
        censored_player: dict[str, Any],
        player: dict[str, Any],
        hand: str,
        userID: int,
    ) -> None:
        if player["userID"] == userID:
            censored_player[hand] = player[hand]
        else:
            censored_player[hand] = [ "" for _ in player[hand] ]

    def censor_userID(
        censored_player: dict[str, Any],
        player: dict[str, Any],
        userID: str,
        current_userID: int,
    ) -> None:
        censored_player["username"] = games.get_username(player[userID], server.app)

    def censor_player(
        censored_players: list[dict[str, Any]],
        player: dict[str, Any],
        _,
        userID: int,
    ) -> None:
        censored_player: dict[str, Any] = {}
        censor: dict[str, Callable] = {
            "hand": censor_hand,
            "userID": censor_userID,
        }
        key: str
        for key in player:
            if key not in censor:
                default(censored_player, player, key, userID)
                continue
            func = censor[key]
            func(censored_player, player, key, userID)
        censored_players.append(censored_player)

    def censor_players(
        censored_state: dict[str, Any],
        game_state: dict[str, Any],
        players: str,
        userID: int,
    ) -> None:
        censored_state["players"] = []
        player: dict[str, Any]
        for player in game_state[players]:
            censor_player(censored_state["players"], player, "", userID)
            if player["userID"] == userID:
                censored_state["current_user"] = game_state["players"].index(player)

    censored_state: dict[str, Any] = {"type": "game_state"}
    censor: dict[str, Callable] = {
        "players": censor_players,
    }
    key: str
    for key in game_state:
        if key not in censor:
            default(censored_state, game_state, key, userID)
            continue
        func = censor[key]
        func(censored_state, game_state, key, userID)
    print()
    print(f"{userID} {censored_state}")
    return json.dumps(censored_state)

async def broadcast_game_state(gameID: int) -> None:
    game_state = WHIST[gameID]
    print(f"{game_state}")
    for userID, websocket in games.get_websockets(gameID).items():
        game_stateJSON = censor_game_state(game_state, userID)
        await websocket.send(game_stateJSON)

async def waiting(websocket, event):
    gameID = int(event["gameID"])
    usernames: list[str] = [
        games.get_username(userID, server.app) 
        for userID in games.get_userIDs(gameID)
    ]
    players: list[dict[str, Any]] = []
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
