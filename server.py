import sqlite3, random, json

from flask import Flask, render_template, request, g, current_app

def get_db():
    database = "dev.sqlite3"
    if "db" not in g:
        g.db = sqlite3.connect(
            database,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Return rows that behave like python dicts
        g.db.row_factory = sqlite3.Row
    return g.db

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

    @app.post("/games/new")
    def games_new_post():
        game = request.form["game"]
        if game not in ["chatroom", "whist"]:
            return "Unsupported game {}".format(game), 400
        db = get_db()
        cursor = db.cursor()
        while True:
            gameID = random.randint(1, 999999)
            existing_game = cursor.execute(
                "SELECT gameID FROM games WHERE gameID = ?",
                [gameID]
            ).fetchone()
            if existing_game == None:
                break
        config_dict = {}
        if game == "chatroom":
            config_dict = {"game": game}
        elif game == "whist":
            scoring = request.form["scoring"]
            length = request.form["length"]
            config_dict = {
                "game": game,
                "scoring": scoring,
                "length": length,
            }
        config = json.dumps(config_dict)
        cursor.execute(
            "insert into games(gameID, config) values (?, ?)",
            [gameID, config]
        )
        domain = "localhost:5000"
        db.commit()
        return render_template(
            "games_new_post.html", gameID=gameID, domain=domain, config=config
        )

    @app.get("/games/join/")
    def games_join_get(error_msg=""):
        return render_template("games_join.html", error=error_msg)

    @app.get("/games/join/<gameID>")
    def games_join_ID_get(gameID):
        db = get_db()
        cursor = db.cursor()
        result = cursor.execute(
            "SELECT * FROM games WHERE gameID = ?",
            [gameID]
        ).fetchone()
        if result == None:
            # Not sure this is the correct solution, potentially a redirect
            # could be better. However the address is the same, only the
            # protocol would change, from POST to GET
            error_msg = f"Error game {gameID} cannot be found"
            return games_join_get(error_msg=error_msg)
        configJSON = result["config"]
        config = json.loads(configJSON)
        if config["game"] == "chatroom":
            return render_template(
                "chatroom.html", gameID=gameID
            )
        return render_template(
            "games_join_post.html", gameID=gameID, config=configJSON
        )

    return app
