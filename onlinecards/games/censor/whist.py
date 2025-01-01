import json

from typing import Any, Callable

from server import app
import handlers.utils as utils

def default(
    censored_state: dict[str, Any],
    game_state: dict[str, Any],
    key: str,
    userID: int,
) -> None:
    """
    Copy the key / value pair to censored_state from game_state.
    """
    censored_state[key] = game_state[key]

def default_list(
    censored_state: list[dict[str, Any]],
    game_state: list[dict[str, Any]],
    key: str,
    userID: int,
) -> None:
    """
    Given 2 lists, copy the key / value pair for every item.
    """
    for i, item in enumerate(game_state):
        censored_item = censored_state[i]
        censored_item[key] = item[key]

def ignore(
    *_
) -> None:
    return

def censor_hands(
    censored_state: dict[str, Any],
    game_state: dict[str, Any],
    key: str,
    userID: int,
) -> None:
    for i, player in enumerate(game_state["players"]):
        censored_player = censored_state["players"][i]
        if player["userID"] == userID:
            censored_player["hand"] = player["hand"]
        else:
            censored_player["hand"] = [ "" for _ in player["hand"] ]

def censor_hands_first_trick(
    censored_state: dict[str, Any],
    game_state: dict[str, Any],
    key: str,
    userID: int,
) -> None:
    """
    Deal the final card to the dealer face up.
    """
    for i, player in enumerate(game_state["players"]):
        censored_player = censored_state["players"][i]
        if player["userID"] == userID:
            censored_player["hand"] = player["hand"]
        elif i == game_state["dealer"]:
            censored_player["hand"] = [ "" for _ in player["hand"] ]
            censored_player["hand"].pop()
            censored_player["hand"].append(player["hand"][-1])
        else:
            censored_player["hand"] = [ "" for _ in player["hand"] ]

def censor_userIDs(
    censored_state: dict[str, Any],
    game_state: dict[str, Any],
    key: str,
    userID: int,
) -> None:
    for i, player in enumerate(game_state["players"]):
        censored_player = censored_state["players"][i]
        username: str = utils.get_username(player["userID"], app)
        censored_player["username"] = username

def create_players_func(
        censor: dict[str, Callable],
        add_funcs: list[Callable]
    ) -> Callable:

    def censor_players(
        censored_state: dict[str, Any],
        game_state: dict[str, Any],
        _: str,
        userID: int,
    ) -> None:
        censored_state["players"] = [ {} for _ in game_state["players"] ]
        # Assuming that all players have identical keys
        for key in game_state["players"][0]:
            if key not in censor:
                default_list(
                    censored_state["players"],
                    game_state["players"],
                    key,
                    userID
                )
                continue
            func = censor[key]
            func(censored_state, game_state, key, userID)
        for func in add_funcs:
            func(censored_state, game_state, userID)
        # There may be a more efficient approach for this
        player: dict[str, Any]
        for player in game_state["players"]:
            if player["userID"] == userID:
                censored_state["current_user"] = game_state["players"].index(player)
    return censor_players

def set_event_type(event_type: str) -> Callable:
    def event_type_setter(
        censored_state: dict[str, Any],
        *_,
    ) -> None:
        censored_state["type"] = event_type
    return event_type_setter

def create_trick_func(
        censor: dict[str, Callable],
        add_funcs: list[Callable]
    ) -> Callable:

    def censor_trick(
            censored_state: dict[str, Any],
            game_state: dict[str, Any],
            _: str,
            userID: int,
        ) -> None:
        censored_state["trick"] = {}
        key: str
        for key in game_state["trick"]:
            if key not in censor:
                default(censored_state["trick"], game_state["trick"], key, userID)
                continue
            func = censor[key]
            func(censored_state, game_state, key, userID)
        for func in add_funcs:
            func(censored_state, game_state, userID)

    return censor_trick

def create_main_func(
        censor: dict[str, Callable],
        add_funcs: list[Callable]
    ) -> Callable:

    def censor_main(game_state: dict[str, Any], userID: int) -> str:
        censored_state: dict[str, Any] = {}
        key: str
        for key in game_state:
            if key not in censor:
                default(censored_state, game_state, key, userID)
                continue
            func = censor[key]
            func(censored_state, game_state, key, userID)
        for func in add_funcs:
            func(censored_state, game_state, userID)
        return json.dumps(censored_state)

    return censor_main

def get_whist_censor_func(variation: str) -> Callable:
    match variation:
        case "first_trick":
            censor: dict[str, Callable] = {
                "hand": censor_hands_first_trick,
                "userID": censor_userIDs,
            }
            add_funcs: list[Callable] = []
            censor_players = create_players_func(censor, add_funcs)
            censor: dict[str, Callable] = {
                "lead": ignore,
                "next_player": ignore,
            }
            add_funcs: list[Callable] = []
            censor_trick = create_trick_func(censor, add_funcs)
            censor: dict[str, Callable] = {
                "players": censor_players,
                "trick": censor_trick,
                "event_handler": ignore,
                "state_handler": ignore,
                "deck": ignore,
            }
            add_funcs: list[Callable] = [set_event_type("game_state")]
            return create_main_func(censor, add_funcs)
        case _:
            censor: dict[str, Callable] = {
                "hand": censor_hands,
                "userID": censor_userIDs,
            }
            add_funcs: list[Callable] = []
            censor_players = create_players_func(censor, add_funcs)
            censor: dict[str, Callable] = {
                "lead": ignore,
                "next_player": ignore,
            }
            add_funcs: list[Callable] = []
            censor_trick = create_trick_func(censor, add_funcs)
            censor: dict[str, Callable] = {
                "players": censor_players,
                "trick": censor_trick,
                "event_handler": ignore,
                "state_handler": ignore,
                "deck": ignore,
            }
            add_funcs: list[Callable] = [set_event_type("game_state")]
            return create_main_func(censor, add_funcs)
