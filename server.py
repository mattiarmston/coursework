import random, json, asyncio, websockets

from flask import Flask, render_template, request, redirect

import games

print(id(games.GAMES))

def create_app():
    # Gives current path to flask
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/rules/")
    def rules():
        return render_template("rules.html")

    @app.get("/rules/whist")
    def rules_whist():
        return render_template("rules_whist.html")

    @app.get("/games/new")
    def games_new_get():
        return render_template("games_new.html")

    async def get_gameID():
        while True:
            gameID = random.randint(1, 999999)
            if gameID not in games.GAMES.keys():
                break
        return gameID

    def get_config(game, form):
        match game:
            case "whist":
                return {
                    "game": game,
                    "scoring": form["scoring"],
                    "length": form["length"],
                }
            case _:
                return {"game": game}

    async def ws_create_game(configJSON):
        async with websockets.connect("ws://127.0.0.1:8001") as ws:
            data = {
                "type": "create",
                #"gameID": gameID,
                "config": configJSON,
            }
            await ws.send(json.dumps(data))
            gameID = await ws.recv()
            return gameID

    @app.post("/games/new")
    def games_new_post():
        game = request.form["game"]
        if game not in ["chatroom", "whist"]:
            return "Unsupported game {}".format(game), 400
        config = get_config(game, request.form)
        configJSON = json.dumps(config)
        gameID = asyncio.run(ws_create_game(configJSON))
        return redirect(f"/games/join/{gameID}")

    @app.get("/games/join/")
    def games_join_get(error_msg=""):
        return render_template("games_join.html", error=error_msg)

    async def config_from_gameID(gameID):
        async with websockets.connect("ws://127.0.0.1:8001") as ws:
            data = {
                "type": "get_config",
                "gameID": gameID,
            }
            await ws.send(json.dumps(data))
            configJSON = await ws.recv()

    @app.get("/games/join/<gameID>")
    def games_join_ID_get(gameID):
        if gameID not in games.GAMES.keys():
            error_msg = f"Error: game {gameID} cannot be found"
            return games_join_get(error_msg=error_msg)
        config = games.GAMES[gameID]["config"]
        assert isinstance(config, dict)
        configJSON = json.dumps(config)
        match config["game"]:
            case "chatroom":
                return render_template(
                    "chatroom.html", gameID=gameID, config=configJSON
                )
            case "whist":
                return render_template(
                    "whist.html", gameID=gameID, config=configJSON
                )
            case _:
                return render_template(
                    "games_join_post.html", gameID=gameID, config=configJSON
                )

    return app

#import ws_server
#from multiprocessing import Process
#
#flask_process = Process(target=create_app)
#flask_process.start()
#ws_process = Process(target=ws_server.main)
#ws_process.start()
#flask_process.join()
#ws_process.join()

app = create_app()
