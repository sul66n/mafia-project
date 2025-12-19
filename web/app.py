from flask import Flask
from extensions import db


def create_app():
    app = Flask(__name__)

    app.secret_key = "super-secret-key"
    app.config["SECRET_KEY"] = "super-secret-key-change-me"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mafia.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from blueprints.main import main_bp
    from blueprints.stats import stats_bp
    from blueprints.game import game_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(stats_bp, url_prefix="/stats")
    app.register_blueprint(game_bp, url_prefix="/game")

    with app.app_context():
        from models import Game
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
