#!/usr/bin/env python

import json

import games

async def handle_chatroom(websocket, eventJSON):
    event = json.loads(eventJSON)
    match event["type"]:
        case "message":
            await send_message(websocket, eventJSON)
        case _:
            await error(websocket, eventJSON)

async def send_message(websocket, eventJSON) -> None:
    gameID = int(json.loads(eventJSON)["gameID"])
    try:
        connected = games.GAMES[gameID]
        for websocket in connected:
            await websocket.send(eventJSON)
    except KeyError:
        print(f"Error could not find {gameID}")
        event = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(event))
    return

async def error(websocket, eventJSON) -> None:
    print("Error handling event")
    return
