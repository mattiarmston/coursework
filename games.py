from websockets.legacy.server import WebSocketServerProtocol

# `GAMES` links from a `gameID` to a set of connected `userID`s
# GAMES = {
#     gameID: {
#         userID: int,
#         ...
#     },
#     ...
# }

GAMES: dict[int, set[int]] = {}

# `USERS` links from a `userID` to a websocket connection
# USERS = {
#     userID: Websocket,
#     ...
# }

USERS: dict[int, WebSocketServerProtocol] = {}

def websockets_from_userIDs(userIDs: set[int] | list[int]) -> set[WebSocketServerProtocol]:
    # I wanted to use a list comprehension for this, but it made handling `KeyError`s difficult
    websockets = set()
    for userID in userIDs:
        try:
            websockets.add(USERS[userID])
        except KeyError:
            print(f"Error: could not find userID {userID}")
    return websockets
