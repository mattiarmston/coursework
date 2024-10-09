from flask import Flask, render_template, request

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
        return render_template("games_new_post.html", game=game)

    @app.get("/games/join/")
    def games_join_get():
        return render_template("games_join.html")

    return app
