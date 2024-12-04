import json

import games, server

WHIST = {}

async def handle_whist(websocket, event):
    match event["type"]:
        case "create":
            pass
        case "join":
            await join(websocket, event)
        case _:
            await error(websocket, event)

async def join(websocket, event):
    gameID = int(event["gameID"])
    # 2 players should not be able to join simultaneously so this should work
    if len(games.get_userIDs(gameID)) != 4:
        await waiting(websocket, event)
        return
    await test_game_state(websocket, event)

async def waiting(websocket, event):
    gameID = int(event["gameID"])
    context = server.app.app_context()
    usernames: list[str] = [
        games.get_username(userID, context) for userID in games.get_userIDs(gameID)]
    print(usernames)
    players: list[dict[str, str]] = []
    for username in usernames:
        players.append({"username": username})
    print(players)
    try:
        connected = games.get_websockets(gameID)
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
        connected = games.get_websockets(gameID)
        response = {
            "type": "game_state",
            "players": [
                {
                    "username": "matti",
                    "bid": 4,
                    "tricks_won": 2,
                    "hand": [
                        "2H", "3D", "AC", "JC",
                    ],
                },
                {
                    "username": "test1",
                    "bid": 2,
                    "tricks_won": 0,
                    "hand": [
                        "6H", "JD", "7H", "3S",
                    ],
                },
                {
                    "username": "test2",
                    "bid": 5,
                    "tricks_won": 3,
                    "hand": [
                        "KC", "2C", "8S", "TS",
                    ],
                },
                {
                    "username": "private",
                    "bid": 2,
                    "tricks_won": 1,
                    "hand": [
                        "8D", "9S", "QD", "5C",
                    ],
                }
            ],
            "trump_suit": "H",
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

async def error(websocket, event):
    print("Error handling event")
