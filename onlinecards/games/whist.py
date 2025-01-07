import random
import json

from typing import Callable, Any

import handlers.utils as utils
from games.censor.whist import get_whist_censor_func

async def broadcast_game_state(
        gameID: int,
        game_state: dict[str, Any],
        censor_variation: str = "",
    ) -> None:
    for userID, websocket in utils.websockets_from_gameID(gameID).items():
        censor_func = get_whist_censor_func(censor_variation)
        game_stateJSON = censor_func(game_state, userID)
        await websocket.send(game_stateJSON)

async def broadcast_scoreboard(
        gameID: int,
        game_state: dict[str, Any],
        censor_variation: str = "",
    ) -> None:
    scoreboard: dict[str, Any] = {
        "teams": [
            {
                "players": [0, 2],
                "score": game_state["players"][0]["points"],
            },
            {
                "players": [1, 3],
                "score": game_state["players"][1]["points"],
            },
        ],
    }
    if censor_variation == "game_end":
        for i, team in enumerate(scoreboard["teams"]):
            if team["players"] == game_state["winner"]:
                scoreboard["winner"] = i
    for team in scoreboard["teams"]:
        for i, player_index in enumerate(team["players"]):
            team["players"][i] = game_state["players"][player_index]
    await broadcast_game_state(gameID, scoreboard, censor_variation="scoreboard")

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

async def initialize_default(
        gameID: int, game_state: dict[str, Any], event: dict[str, Any]
    ) -> None:
    set_partners_default(game_state)
    for player in game_state["players"]:
        player["points"] = 0
    initialize_hand_default(gameID, game_state)
    await broadcast_game_state(gameID, game_state, censor_variation="first_trick")

def initialize_hand_default(
        gameID: int, game_state: dict[str, Any]
    ) -> None:
    game_state["deck"] = create_deck_default()
    deal_hand_default(game_state)
    for player in game_state["players"]:
        player["tricks_won"] = 0
    try:
        game_state["dealer"] += 1
    except KeyError:
        game_state["dealer"] = 0
    set_trump_default(game_state)
    game_state["trick"] = {}
    print("hand initialised")

def get_valid_cards_default(game_state: dict[str, Any], player_index: int) -> list[str]:
    player = game_state["players"][player_index]
    trick = game_state["trick"]
    lead_card = trick["played"][trick["lead"]]
    if lead_card == None:
        return player["hand"]
    lead_suit = lead_card[1]
    valid = []
    for card in player["hand"]:
        if card[1] == lead_suit:
            valid.append(card)
    if valid != []:
        return valid
    return player["hand"]

def play_card_default(
        gameID: int, game_state: dict[str, Any], event: dict[str, Any]
    ) -> None:
    userID = int(event["userID"])
    index = None
    for i, player in enumerate(game_state["players"]):
        if player["userID"] == userID:
            index = i
            break
    if index == None:
        return
    if index != game_state["trick"]["next_player"]:
        return
    card = event["choice"]["chosen"]
    player = game_state["players"][index]
    player["hand"].remove(card)
    game_state["trick"]["played"][index] = card

def get_trick_winner_default(
        gameID: int, game_state: dict[str, Any], event: dict[str, Any]
    ) -> int:
    def get_value(card):
        try:
            value = int(card[0])
        except ValueError:
            value = value_map[card[0]]
        return value

    trick = game_state["trick"]
    lead = trick["played"][trick["lead"]]
    trump_suit = game_state["trump_suit"]
    value_map = {
        "T": 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14,
    }
    winner = trick["lead"]
    winning_card = lead
    for i, card in enumerate(trick["played"]):
        suit = card[1]
        value = get_value(card)
        winning_suit = winning_card[1]
        winning_value = get_value(winning_card)
        if suit == winning_suit and value > winning_value:
            winner = i
            winning_card = card
            continue
        if suit != trump_suit:
            continue
        if winning_suit != trump_suit:
            winner = i
            winning_card = card
            continue
        if value > winning_value:
            winner = i
            winning_card = card
            continue
    return winner

def get_lead_default(gameID: int, game_state: dict[str, Any]) -> int:
    try:
        return game_state["trick"]["prev_winner"]
    except KeyError:
        next = game_state["dealer"] + 1
        if next == len(game_state["players"]):
            next = 0
        return next

def play_trick_default(gameID: int, game_state: dict[str, Any]):
    lead = get_lead_default(gameID, game_state)
    game_state["trick"] = {
        "lead": lead,
        "played": [ None for _ in game_state["players"] ],
        "next_player": lead,
    }

def check_trick_end_default(
        gameID: int, game_state: dict[str, Any], event: dict[str, Any]
    ) -> bool:
    trick = game_state["trick"]
    if None in trick["played"]:
        next = trick["next_player"] + 1
        if next == len(game_state["players"]):
            next = 0
        trick["next_player"] = next
        return False
    else:
        winner = get_trick_winner_default(gameID, game_state, event)
        game_state["players"][winner]["tricks_won"] += 1
        trick["prev_winner"] = winner
        return True

def check_hand_end_default(
        gameID: int, game_state: dict[str, Any]
    ) -> bool:
    player = game_state["players"][0]
    if len(player["hand"]) == 0:
        return True
    else:
        return False

def update_points_default(
        gameID: int, game_state: dict[str, Any]
    ) -> None:
    points: list[int] = [0, 0]
    for i in [0, 1]:
        player = game_state["players"][i]
        points[i] += player["tricks_won"]
        partner = game_state["players"][player["partner"]]
        points[i] += partner["tricks_won"]
    points_copy = [0, 0]
    for i in [0, 1]:
        diff: int = points[i] - points[i - 1]
        diff = max(0, diff)
        points_copy[i] = diff
    points = points_copy
    for i in [0, 1]:
        player = game_state["players"][i]
        player["points"] += points[i]
        partner = game_state["players"][player["partner"]]
        partner["points"] += points[i]

def check_game_end_default(
        gameID: int, game_state: dict[str, Any]
    ) -> bool:
    players = game_state["players"]
    for i in [0, 1]:
        player = players[i]
        if player["points"] >= 5:
            game_state["winner"] = [i, player["partner"]]
            return True
    return False

async def ask_card_default(gameID: int, game_state: dict[str, Any]):
    player_index = game_state["trick"]["next_player"]
    event = {
        "type": "choice",
        "choice": {
            "type": "play_card",
            "options": get_valid_cards_default(game_state, player_index),
        },
    }
    player = game_state["players"][player_index]
    websocket = utils.get_websocket(player["userID"])
    await websocket.send(json.dumps(event))

async def choice_default(
        gameID: int, game_state: dict[str, Any], event: dict[str, Any]
    ) -> None:
    match event["choice"]["type"]:
        case "play_card":
            play_card_default(gameID, game_state, event)
            return
        case _:
            return

async def waiting_default(
        gameID: int, game_state: dict[str, Any], event: dict[str, Any]
    ) -> None:
    players: list[dict[str, Any]] = game_state["players"]
    response = {
        "type": "waiting",
        "no_players": len(players),
        "players_required": 4,
        "players": players,
    }
    await broadcast_game_state(gameID, response)

def get_whist_state_handler() -> Callable:
    async def state_handler_default(
        gameID: int, game_state: dict[str, Any], event: dict[str, Any]
    ) -> None:
        # Call setup and teardown functions after each event
        match event["type"]:
            case "waiting":
                return

            case "start":
                play_trick_default(gameID, game_state)
                await ask_card_default(gameID, game_state)

            case "choice":
                match event["choice"]["type"]:
                    case "play_card":
                        end = check_trick_end_default(gameID, game_state, event)
                        await broadcast_game_state(gameID, game_state)
                        if not end:
                            await ask_card_default(gameID, game_state)
                        else:
                            event["type"] = "end_trick"
                            print('event["type"]', event["type"])
                            await state_handler_default(gameID, game_state, event)

                    case _:
                        return

            case "end_trick":
                end = check_hand_end_default(gameID, game_state)
                if not end:
                    play_trick_default(gameID, game_state)
                    await broadcast_game_state(gameID, game_state)
                    await ask_card_default(gameID, game_state)
                else:
                    event["type"] = "end_hand"
                    print('event["type"]', event["type"])
                    await state_handler_default(gameID, game_state, event)

            case "end_hand":
                update_points_default(gameID, game_state)
                await broadcast_scoreboard(gameID, game_state)
                end = check_game_end_default(gameID, game_state)
                if not end:
                    print("game not done")
                    initialize_hand_default(gameID, game_state)
                    play_trick_default(gameID, game_state)
                    await broadcast_game_state(gameID, game_state)
                    print("trick initialised")
                    await ask_card_default(gameID, game_state)
                    print("asked card")
                else:
                    event["type"] = "end_game"
                    print('event["type"]', event["type"])
                    await state_handler_default(gameID, game_state, event)

            case "end_game":
                print('event["type"]', event["type"])
                await broadcast_scoreboard(
                    gameID, game_state, "game_end"
                )

            case _:
                return

    return state_handler_default

def get_whist_event_handler() -> Callable:
    def error(event):
        return lambda *_: print(f"Error could find handler for event {event}")

    def func_default(event: str) -> Callable:
        try:
            return events[event]
        except KeyError:
            return error(event)

    events: dict[str, Callable] = {
        "start": initialize_default,
        "waiting": waiting_default,
        "choice": choice_default,
    }

    return func_default
