import random, json, asyncio, websockets

from flask import Flask, render_template, request, redirect, make_response
from sqlite3 import Connection

import database

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

    def new_gameID(cursor):
        while True:
            gameID = random.randint(1, 999999)
            existing_game = cursor.execute(
                "SELECT gameID FROM games WHERE gameID = ?",
                [gameID]
            ).fetchone()
            if existing_game == None:
                break
        return gameID

    def get_config(game_type, form):
        match game_type:
            case "whist":
                return {
                    "game_type": game_type,
                    "scoring": form["scoring"],
                    "length": form["length"],
                }
            case _:
                return {"game_type": game_type}

    async def ws_create_game(gameID):
        async with websockets.connect("ws://127.0.0.1:8001") as ws:
            data = {
                "type": "create",
                "gameID": gameID,
            }
            await ws.send(json.dumps(data))

    @app.post("/games/new")
    def games_new_post():
        game_type = request.form["game_type"]
        if game_type not in ["chatroom", "whist"]:
            return "Unsupported game {}".format(game_type), 400
        db = database.get_db()
        cursor = db.cursor()
        gameID = new_gameID(cursor)
        config = get_config(game_type, request.form)
        configJSON = json.dumps(config)
        cursor.execute(
            "INSERT INTO games(gameID, config) VALUES (?, ?)",
            [gameID, configJSON]
        )
        db.commit()
        if game_type in ["chatroom", "whist"]:
            asyncio.run(ws_create_game(gameID))
            return redirect(f"/games/join/{gameID}")
        domain = "localhost:5000"
        return render_template(
            "games_new_post.html", gameID=gameID, domain=domain, config=configJSON
        )

    @app.get("/games/join/")
    def games_join_get(error_msg=""):
        return render_template("games_join.html", error=error_msg)

    def add_userID(userID: str, db: Connection) -> None:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users(userID) VALUES (?)",
            [userID]
        )
        db.commit()
        return

    def new_userID(db: Connection) -> str:
        cursor = db.cursor()
        while True:
            userID = random.randint(1, 999999)
            existing_user = cursor.execute(
                "SELECT userID FROM users WHERE userID = ?",
                [userID]
            ).fetchone()
            if existing_user == None:
                break
        userID = str(userID)
        add_userID(userID, db)
        return userID

    def get_userID(request, db: Connection) -> str:
        userID = request.cookies.get("userID")
        if userID != None:
            return userID
        else:
            return new_userID(db)

    def get_game_template(game_type, gameID, configJSON=""):
        match game_type:
            case "chatroom":
                return render_template(
                    "chatroom.html", gameID=gameID
                )
            case "whist":
                return render_template(
                    "whist.html", gameID=gameID
                )
            case _:
                return render_template(
                    # This should be removed / replaced later with an error message
                    "games_join_post.html", gameID=gameID, config=configJSON
                )

    @app.get("/games/join/<gameID>")
    def games_join_ID_get(gameID):
        db = database.get_db()
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM games WHERE gameID = ?",
            [gameID]
        ).fetchone()
        if result == None:
            return games_join_get(error_msg=f"Error: game {gameID} cannot be found")
        configJSON = result["config"]
        config = json.loads(configJSON)
        userID = get_userID(request, db)
        response = make_response(
            get_game_template(config["game_type"], gameID, configJSON)
        )
        response.set_cookie("userID", userID)
        return response

    database.init_db(app)

    return app

app = create_app()
