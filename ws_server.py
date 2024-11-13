
import websockets, asyncio, json

import games
from chatroom import handle_chatroom

async def handler(websocket):
    async for eventJSON in websocket:
        print(eventJSON)
        event = json.loads(eventJSON)
        match event["type"]:
            case "create":
                await create(websocket, event["gameID"])
            case "join":
                await join(websocket, event["gameID"])
            case _:
                config = json.loads(event["config"])
                match config["game"]:
                    case "chatroom":
                        await handle_chatroom(websocket, eventJSON)

async def create(websocket, gameID):
    games.GAMES[gameID] = set()
    print(f"Created Game {gameID}")

async def join(websocket, gameID_str):
    gameID = int(gameID_str)
    try:
        connected = games.GAMES[gameID]
        games.GAMES[gameID] = connected | { websocket }
        print(f"New player joined game {gameID}")
    except KeyError:
        print(f"Error could not find {gameID}")
        event = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(event))

async def main():
    async with websockets.serve(handler, "", 8001):
        # Wait for a promise that will never be fulfilled - run forever
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
