from flask import Flask, render_template

def create_app():
    # Gives current path to flask
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("home.html")

    @app.get("/rules/")
    def rules():
        return render_template("rules.html")

    @app.get("/rules/whist")
    def rules_whist():
        return render_template("rules_whist.html")

    @app.get("/create_game")
    def create_game_get():
        return render_template("create_game.html")

    @app.get("/join_game/")
    def join_game_get():
        return render_template("join_game.html")

    return app
