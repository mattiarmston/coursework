# Serialisation

Internally the state of every game will need to be recorded and managed. This
will be done using a python dictionary that can be converted to JSON and sent
over the internet. Once the front end has received it, client side JavaScript
will convert it into HTML (this could be replaced with a tool such as hotwire in
the future).

When updating the game state, this should be done using a series of update
functions. Some of these will take user input as an argument and others may use
randomness, however these should be mathematically pure functions wherever
possible.

In order to store the game state, it must first be serialised. This will vary
from game to game (and some variations may add attributes) so the specific
requirements for each game are listed below.

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
    "config": { ... },
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
    "type": "message",
    "gameID": 123456,
    "config": { ... },
    "username": string,
    "message": string
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
    "config": { ... },
    "players": int,
    "players_required": int
}
```

JSON Example:

```
{
    "type": "game_state",
    "gameID": 123456,
    "config": { ... },
    "players": [
        {
            "name": string,
            "bid": int,
            "tricks_won": int,
            "hand": ["AH", "3C", "8D", "JH", "TC"],
        },
        ...
    ]
}
```

