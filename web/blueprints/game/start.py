from flask import render_template, redirect, url_for, request
from extensions import db
from models import Game, Player
from . import game_bp


@game_bp.route("/start", methods=["GET", "POST"])
def start_game():
    if request.method == "POST":
        names = request.form.getlist("players")

        game = Game(status="playing")
        db.session.add(game)
        db.session.commit()

        for name in names:
            player = Player(name=name, game_id=game.id)
            db.session.add(player)

        db.session.commit()
        return redirect(url_for("game.play", game_id=game.id))

    return render_template("game.html")
