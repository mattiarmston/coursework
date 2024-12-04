# Serialisation

Internally the state of every game will need to be recorded and managed, which
means it first must be serialised. This process will vary from game to game (and
some variations may add data that needs to be tracked), so the specifics for
each game type are detailed below.

Once serialised, the game state will be stored using a python dictionary and
updated as the game progresses. To update the game state the server should use a
series of update functions. Some of these will take user input as an argument
and others may use randomness, however these should be mathematically pure
functions wherever possible.

To update the user interface the server must first determine what information
each player should have access to -- for example Player 1 cannot see Player 2's
hand of cards. Once this is done the game state should be converted to JSON and
sent over the internet. Once the front end has received it, client side
JavaScript will convert it into HTML which can be displayed by the browser (this
could be replaced with a tool such as hotwire in the future).

## Client-side guidelines

* `"type"` describes the purpose of a message. Certain types of message have set
meanings that should be respected both by the client and server.
    * `"game_state"` represents a complete state of the game that replaces any
      previous state. The front end should render a new view based only on this
      information. **Note:** this does not have to be a complete description of
      the game, only the information that this player should have access to. If
      a player does not know what cards their opponents have, this information
      should not be part of the game state.
    * `"update"` represents partial information that should be combined with the
      current game state to produce a new game state. In a chatroom, the
      `"game_state"` is the list of all messages but this data does not have to
      be resent with each new message. It is more efficient just to send the new
      message separately as an `"update"`. On the client-side the new message
      can be rendered without having to render all previous messages as well. In
      cases where combining the `"update"` to create a new game state is complex
      it may be preferable to send a new `"game_state"` instead.
* `"gameID"` is only required when sending a message to the server and server
  responses may not include one. A new Websocket connection should be created
  for each game so each socket handles a single game. However, `"gameID"` is
  required when sending messages to the server to improve performance.

## Chatroom serialisation

A chatroom does not have a 'game state' as card games do, however when joining a
user may want to see messages that have been sent before they joined. This could
be done using a game state that stores all previously sent messages. Once a user
has joined and a new message is sent, it is not necessary to resend all previous
messages, so instead an update can be sent that includes only the new message.

JSON Example:

```
{
    "type": "game_state",
    "gameID": 123456,
    "messages": [
        {
            "username": string,
            "message": string
        },
        ...
    ]
}
```

JSON Example:

```
{
    "type": "update",
    "gameID": 123456,
    "message": {
        "username": string,
        "message": string
    }
}
```

## Whist serialisation

Some games require a set number of players, such as whist, and so users will
have to wait for others to join before the game can begin. Whilst waiting, the
UI should inform them of this and they should be able to see how many people
have joined. When a new player joins, an update message will be sent from the
server to all connected clients.

```
{
    "type": "waiting",
    "gameID": 123456,
    "no_players": int,
    "players_required": int
    "players": [
        {
            "username": string,
        },
        ...
    ]
}
```

JSON Example:

```
{
    "type": "game_state",
    "gameID": 123456,
    "players": [
        {
            "name": string,
            "bid": int,
            "tricks_won": int,
            "hand": ["AH", "3C", "8D", "JH", "TC"],
        },
        ...
    ],
    "trump_suit": string
}
```

