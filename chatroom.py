#!/usr/bin/env python

import websockets, asyncio, json

GAMES: dict[int, set] = {}

async def handler(websocket):
    async for eventJSON in websocket:
        print(eventJSON)
        event = json.loads(eventJSON)
        if event["type"] == "create":
            await create(websocket, event["gameID"])
        elif event["type"] == "join":
            await join(websocket, event["gameID"])
        elif event["type"] == "message":
            await send_message(event["gameID"], eventJSON)

async def create(websocket, gameID):
    GAMES[gameID] = set()
    print(f"Created Game {gameID}")

async def join(websocket, gameID_str):
    gameID = int(gameID_str)
    try:
        connected = GAMES[gameID]
        GAMES[gameID] = connected | { websocket }
        print(f"New player joined game {gameID}")
    except KeyError:
        print(f"Error could not find {gameID}")

async def send_message(gameID_str, eventJSON):
    gameID = int(gameID_str)
    try:
        connected = GAMES[gameID]
        for websocket in connected:
            await websocket.send(eventJSON)
    except KeyError:
        print(f"Error could not find {gameID}")

async def main():
    async with websockets.serve(handler, "", 8001):
        # Wait for a promise that will never be fulfilled - run forever
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
