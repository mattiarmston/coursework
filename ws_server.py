
import websockets, asyncio, json, random

import games
print(id(games.GAMES))
from chatroom import handle_chatroom
from whist import handle_whist

async def handler(websocket):
    async for eventJSON in websocket:
        print(eventJSON)
        event = json.loads(eventJSON)
        match event["type"]:
            case "create":
                gameID = await create(websocket, event)
                event["gameID"] = str(gameID)
            case "join":
                await join(websocket, event)
            case "get_config":
                await get_config(websocket, event)
        # This allows each game type to run its own code when a game is created
        # or a player joins
        gameID = int(event["gameID"])
        try:
            config = games.GAMES[gameID]["config"]
            assert isinstance(config, dict)
            game_handler = await get_game_handler(config["game"])
            game_handler(websocket, event)
        except KeyError:
            # This should probably return an error or something
            pass

async def get_game_handler(game_type):
    async def error(*_):
        print(f"Could not find handler for {game_type}")

    map = {
        "chatroom": handle_chatroom,
        "whist": handle_whist,
    }
    try:
        return map[game_type]
    except KeyError:
        return error

async def create(websocket, event):
    config = json.loads(event["config"])
    game_data = {
        "config": config,
        "connected": set(),
    }
    while True:
        gameID = random.randint(1, 999999)
        if gameID not in games.GAMES.keys():
            break
    games.GAMES[gameID] = game_data
    print(f"Created Game {gameID}")
    await websocket.send(str(gameID))
    return gameID

async def join(websocket, event):
    gameID = int(event["gameID"])
    try:
        connected = games.GAMES[gameID]["connected"]
        assert isinstance(connected, set)
        games.GAMES[gameID]["connected"] = connected | { websocket }
        print(f"New player joined game {gameID}")
    except KeyError:
        print(f"Error could not find {gameID}")
        event = {
            "type": "error",
            "message": f"Game {gameID} does not exist",
        }
        await websocket.send(json.dumps(event))

async def get_config(websocket, event):
    pass

async def main():
    async with websockets.serve(handler, "", 8001):
        # Wait for a promise that will never be fulfilled - run forever
        print("Websocket server running")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
