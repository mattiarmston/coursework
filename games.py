# `GAMES` is a global dictionary that links a `gameID` to the game's config and
# all connected players.
#
# This is what it might look like:
#
# GAMES = {
#     gameID: {
#         "config": { ... },
#         "connected": { ... },
#     }
# }

GAMES: dict[int, dict[str, dict | set]] = {}
