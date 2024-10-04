from flask import Flask, render_template

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
    def create_game_get():
        return render_template("games_new.html")

    @app.get("/games/join/")
    def join_game_get():
        return render_template("games_join.html")

    return app
