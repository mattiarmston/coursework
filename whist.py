import json

import games

WHIST = {}

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
        connected = games.get_websockets(gameID)
        response = {
            "type": "waiting",
            "players": len(connected),
            "players_required": 4
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
