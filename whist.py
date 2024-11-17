import json

import games

async def handle_whist(websocket, eventJSON):
    event = json.loads(eventJSON)
    match event["type"]:
        case "create":
            pass
        case "join":
            pass
        case _:
            await error(websocket, eventJSON)

async def waiting(websocket, eventJSON):
    gameID = int(json.loads(eventJSON)["gameID"])
    try:
        connected = games.GAMES[gameID]
        for websocket in connected:
            event = {
                "type": "waiting",
                "players": len(connected),
                "players_required": 4
            }
            await websocket.send(eventJSON)
    except KeyError:
        print(f"Error could not find {gameID}")
        event = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(event))
    return

async def error(websocket, eventJSON):
    print("Error handling event")
