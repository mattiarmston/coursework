import json

import games
from games import websockets_from_userIDs

async def handle_whist(websocket, event):
    match event["type"]:
        case "create":
            pass
        case "join":
            pass
        case _:
            await error(websocket, event)

async def waiting(websocket, event):
    gameID = int(event["gameID"])
    try:
        connected = websockets_from_userIDs(games.GAMES[gameID])
        for websocket in connected:
            response = {
                "type": "waiting",
                "players": len(connected),
                "players_required": 4
            }
            await websocket.send(json.dumps(response))
    except KeyError:
        print(f"Error could not find {gameID}")
        response = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(response))

async def error(websocket, event):
    print("Error handling event")
