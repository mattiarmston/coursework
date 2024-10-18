#!/usr/bin/env python

import asyncio, json
import websockets

async def handler(websocket):
    async for eventJSON in websocket:
        print(eventJSON)
        event = json.loads(eventJSON)
        if event["type"] == "message":
            # In future this will be processed and then sent to every connected
            # client
            await websocket.send(eventJSON)

async def main():
    async with websockets.serve(handler, "", 8001):
        # Wait for a promise that will never be fulfilled - run forever
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
