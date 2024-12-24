import random

from typing import Callable, Any

import handlers.utils as utils
from games.censor.whist import get_censor_func

async def broadcast_game_state(gameID: int, game_state: dict[str, Any]) -> None:
    for userID, websocket in utils.get_websockets(gameID).items():
        game_stateJSON = get_censor_func("default")(game_state, userID)
        await websocket.send(game_stateJSON)

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
