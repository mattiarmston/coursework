import database

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

def init_game(gameID: int) -> None:
    GAMES[gameID] = set()

def get_userIDs(gameID: int) -> set[int]:
    return GAMES[gameID]

def set_userIDs(gameID: int, userIDs: set[int]) -> None:
    GAMES[gameID] = userIDs
    return

def get_websockets(gameID: int) -> set[WebSocketServerProtocol]:
    websockets = set()
    for userID in get_userIDs(gameID):
        try:
            websockets.add(USERS[userID])
        except KeyError:
            print(f"Error: could not find userID {userID}")
    return websockets

def set_websocket(userID: int, websocket) -> None:
    USERS[userID] = websocket

def get_username(userID: int, context) -> str:
    with context:
        cursor = database.get_db().cursor()
        result = cursor.execute(
            "SELECT username FROM users WHERE userID = ?",
            [userID]
        ).fetchone()
        username = result["username"]
        return username

