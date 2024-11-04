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
    connected = GAMES[gameID]
    GAMES[gameID] = connected | { websocket }
    print(f"Player {websocket} joined game {gameID}")

async def send_message(gameID_str, eventJSON):
    connected = GAMES[int(gameID_str)]
    for websocket in connected:
        await websocket.send(eventJSON)
    print(f"Sent {eventJSON} to {connected}")

async def main():
    async with websockets.serve(handler, "", 8001):
        # Wait for a promise that will never be fulfilled - run forever
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
