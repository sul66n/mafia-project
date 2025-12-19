from extensions import db
from datetime import datetime


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.String(20), nullable=False)   # setup / active / finished
    phase = db.Column(db.String(20), default="day")    # day / night
    day = db.Column(db.Integer, default=1, nullable=False)

    winner = db.Column(db.String(10))                   # red / black
    game_length = db.Column(db.Integer)                 # итоговая длина

    sheriff_accuracy = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    don_check_result = db.Column(db.String(50), nullable=True)
    sheriff_check_result = db.Column(db.String(50), nullable=True)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20))
    alive = db.Column(db.Boolean, default=True)

    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    from_player_id = db.Column(db.Integer)
    to_player_id = db.Column(db.Integer)

    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)
