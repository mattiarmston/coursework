import random
import json

from typing import Callable, Any

import server
import handlers.utils as utils

async def broadcast_game_state(gameID: int, game_state: dict[str, Any]) -> None:
    for userID, websocket in utils.get_websockets(gameID).items():
        game_stateJSON = censor_game_state(game_state, userID)
        await websocket.send(game_stateJSON)

def censor_game_state(game_state: dict[str, Any], userID: int) -> str:
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
        censored_state: dict[str, Any],
        game_state: dict[str, Any],
        key: str,
        userID: int,
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

    def censor_userIDs(
        censored_state: dict[str, Any],
        game_state: dict[str, Any],
        key: str,
        userID: int,
    ) -> None:
        for i, player in enumerate(game_state["players"]):
            censored_player = censored_state["players"][i]
            username: str = utils.get_username(player["userID"], server.app)
            censored_player["username"] = username

    def censor_players(
        censored_state: dict[str, Any],
        game_state: dict[str, Any],
        _: str,
        userID: int,
    ) -> None:
        censored_state["players"] = [ {} for _ in game_state["players"] ]
        # Assuming that all players have identical keys
        for key in game_state["players"][0]:
            censor: dict[str, Callable] = {
                "hand": censor_hands,
                "userID": censor_userIDs,
            }
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
        # There may be a more efficient approach for this
        player: dict[str, Any]
        for player in game_state["players"]:
            if player["userID"] == userID:
                censored_state["current_user"] = game_state["players"].index(player)

    censored_state: dict[str, Any] = {"type": "game_state"}
    censor: dict[str, Callable] = {
        "players": censor_players,
        "func": ignore,
        "deck": ignore,
    }
    key: str
    for key in game_state:
        if key not in censor:
            default(censored_state, game_state, key, userID)
            continue
        func = censor[key]
        func(censored_state, game_state, key, userID)
    return json.dumps(censored_state)

def create_deck_default(shuffle=True) -> list[str]:
    deck: list[str] = []
    for suit in ["C", "D", "H", "S"]:
        for i in range(1, 14):
            if i in range(2, 10):
                card = str(i) + suit
                deck.append(card)
                continue
            match(i):
                case 1:
                    card = "A" + suit
                case 10:
                    card = "T" + suit
                case 10:
                    card = "T" + suit
                case 11:
                    card = "J" + suit
                case 12:
                    card = "Q" + suit
                case 13:
                    card = "K" + suit
                case _:
                    raise ValueError
            deck.append(card)
    if shuffle:
        random.shuffle(deck)
    return deck

def set_partners_default(game_state: dict[str, Any]) -> None:
    players = game_state["players"]
    random.shuffle(players)
    partners = [2, 3, 0, 1]
    for i, player in enumerate(players):
        player["partner"] = partners[i]

def deal_hand_default(game_state: dict[str, Any]) -> None:
    deck = game_state["deck"]
    players = game_state["players"]
    while len(deck) != 0:
        for player in players:
            try:
                player["hand"].append(deck.pop())
            except KeyError:
                player["hand"] = [ deck.pop() ]

def set_trump_default(game_state: dict[str, Any]) -> None:
    dealer = game_state["players"][game_state["dealer"]]
    last_card = dealer["hand"][-1]
    suit = last_card[-1]
    game_state["trump_suit"] = suit

def initialize_default(game_state: dict[str, Any]) -> None:
    game_state["deck"] = create_deck_default()
    set_partners_default(game_state)
    deal_hand_default(game_state)
    game_state["dealer"] = 0
    set_trump_default(game_state)

async def func_default(gameID: int, game_state: dict[str, Any]) -> None:
    initialize_default(game_state)
    await broadcast_game_state(gameID, game_state)
    print(game_state)

def get_whist_func() -> Callable:
    return func_default
