import random
import json

from typing import Callable, Any

import server
import handlers.utils as utils

def censor_game_state(game_state: dict[str, Any], userID: int) -> str:
    def default(
        censored_state: dict[str, Any],
        game_state: dict[str, Any],
        key: str,
        userID: int,
    ) -> None:
        censored_state[key] = game_state[key]

    def censor_hand(
        censored_player: dict[str, Any],
        player: dict[str, Any],
        hand: str,
        userID: int,
    ) -> None:
        if player["userID"] == userID:
            censored_player[hand] = player[hand]
        else:
            censored_player[hand] = [ "" for _ in player[hand] ]

    def censor_userID(
        censored_player: dict[str, Any],
        player: dict[str, Any],
        userID: str,
        current_userID: int,
    ) -> None:
        censored_player["username"] = utils.get_username(player[userID], server.app)

    def censor_player(
        censored_players: list[dict[str, Any]],
        player: dict[str, Any],
        _,
        userID: int,
    ) -> None:
        censored_player: dict[str, Any] = {}
        censor: dict[str, Callable] = {
            "hand": censor_hand,
            "userID": censor_userID,
        }
        key: str
        for key in player:
            if key not in censor:
                default(censored_player, player, key, userID)
                continue
            func = censor[key]
            func(censored_player, player, key, userID)
        censored_players.append(censored_player)

    def censor_players(
        censored_state: dict[str, Any],
        game_state: dict[str, Any],
        players: str,
        userID: int,
    ) -> None:
        censored_state["players"] = []
        player: dict[str, Any]
        for player in game_state[players]:
            censor_player(censored_state["players"], player, "", userID)
            if player["userID"] == userID:
                censored_state["current_user"] = game_state["players"].index(player)

    censored_state: dict[str, Any] = {"type": "game_state"}
    censor: dict[str, Callable] = {
        "players": censor_players,
    }
    key: str
    for key in game_state:
        if key not in censor:
            default(censored_state, game_state, key, userID)
            continue
        func = censor[key]
        func(censored_state, game_state, key, userID)
    print()
    print(f"{userID} {censored_state}")
    return json.dumps(censored_state)

def set_partners_default(players: list[dict[str, Any]]) -> None:
    partner_index: int = random.randint(1, 3)
    players[0]["partner"] = partner_index
    players[partner_index]["partner"] = 0
    remaining: list[int] = [1, 2, 3]
    remaining.remove(partner_index)
    players[remaining[0]]["partner"] = remaining[1]
    players[remaining[1]]["partner"] = remaining[0]

def initialize_default(players: list[dict[str, Any]]):
    set_partners_default(players)
    return

def method_default(game_state):
    players = game_state["players"]
    initialize_default(players)
    print(game_state)
    return

def get_whist_method() -> Callable:
    return method_default
