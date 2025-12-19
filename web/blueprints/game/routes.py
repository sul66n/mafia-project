import random
from flask import render_template, redirect, url_for, request, flash
from . import game_bp
from models import Game, Player, Vote
from extensions import db


# СОЗДАНИЕ ИГРЫ И ИГРОКОВ
@game_bp.route("/create", methods=["GET", "POST"])
def create_players():
    """
    Создание новой игры и списка игроков
    """
    if request.method == "POST":
        names = request.form.getlist("players")

        # создаём новую игру
        game = Game(
            status="setup",
            phase="day",
            game_length=1,  # номер текущего дня
            sheriff_accuracy=round(random.uniform(0.3, 0.9), 2)
        )
        db.session.add(game)
        db.session.commit()

        # создаём игроков
        for name in names:
            if name.strip():
                db.session.add(Player(
                    name=name.strip(),
                    game_id=game.id,
                    alive=True
                ))

        db.session.commit()
        return redirect(url_for("game.assign_roles", game_id=game.id))

    return render_template("create_players.html")


# РАСПРЕДЕЛЕНИЕ РОЛЕЙ
@game_bp.route("/<int:game_id>/assign")
def assign_roles(game_id):
    game = Game.query.get_or_404(game_id)
    players = Player.query.filter_by(game_id=game_id).all()

    if len(players) != 10:
        flash(f"Ошибка: найдено {len(players)} игроков, нужно ровно 10", "error")
        return redirect(url_for("game.create_players"))

    roles = [
        "don",
        "mafia", "mafia",
        "sheriff",
        "civilian", "civilian", "civilian",
        "civilian", "civilian", "civilian"
    ]

    random.shuffle(roles)

    for i in range(10):
        players[i].role = roles[i]

    game.status = "active"
    db.session.commit()

    return redirect(url_for("game.reveal_roles", game_id=game.id))



# ПОКАЗ РОЛЕЙ
@game_bp.route("/<int:game_id>/roles")
def reveal_roles(game_id):
    """
    Экран показа ролей игрокам
    """
    players = Player.query.filter_by(game_id=game_id).all()
    return render_template("roles.html", players=players)



# НАЧАТЬ НОВУЮ ИГРУ
@game_bp.route("/new")
def new_game():
    """
    Кнопка "Новая игра"
    """
    return redirect(url_for("game.create_players"))

# ход дона
@game_bp.route("/<int:game_id>/night/don", methods=["GET", "POST"])
def night_don(game_id):
    game = Game.query.get_or_404(game_id)

    don = Player.query.filter_by(
        game_id=game_id,
        role="don",
        alive=True
    ).first()

    if not don:
        game.phase = "night_sheriff"
        db.session.commit()
        return redirect(url_for("game.night_sheriff", game_id=game_id))

    players = Player.query.filter(
        Player.game_id == game_id,
        Player.alive == True,
        Player.id != don.id
    ).all()

    if request.method == "POST":
        target_id = int(request.form["target"])
        target = Player.query.get_or_404(target_id)

        if target.role == "sheriff":
            game.don_check_result = f"🔍 {target.name} — ШЕРИФ"
        else:
            game.don_check_result = f"❌ {target.name} — не шериф"

        db.session.commit()

        # ❗ ВАЖНО: НИКАКОГО redirect здесь
        return render_template(
            "night_don.html",
            game=game,
            players=players
        )

    return render_template(
        "night_don.html",
        game=game,
        players=players
    )



# ход шерифа
@game_bp.route("/<int:game_id>/night/sheriff", methods=["GET", "POST"])
def night_sheriff(game_id):
    game = Game.query.get_or_404(game_id)

    sheriff = Player.query.filter_by(
        game_id=game_id,
        role="sheriff",
        alive=True
    ).first()

    # если шерифа нет — сразу утро
    if not sheriff:
        game.phase = "day"
        db.session.commit()
        return redirect(url_for("game.game_view", game_id=game_id))

    players = Player.query.filter(
        Player.game_id == game_id,
        Player.alive == True,
        Player.id != sheriff.id
    ).all()

    if request.method == "POST":
        target_id = int(request.form["target"])
        target = Player.query.get_or_404(target_id)

        if target.role in ("mafia", "don"):
            game.sheriff_check_result = f"🔫 {target.name} — МАФИЯ"
        else:
            game.sheriff_check_result = f"👤 {target.name} — не мафия"

        db.session.commit()

        # ❗ ОСТАЁМСЯ НА ЭКРАНЕ ШЕРИФА
        return render_template(
            "night_sheriff.html",
            game=game,
            players=players
        )

    return render_template(
        "night_sheriff.html",
        game=game,
        players=players
    )



# ОСНОВНОЙ ЭКРАН ИГРЫ
@game_bp.route("/<int:game_id>")
def game_view(game_id):
    game = Game.query.get_or_404(game_id)
    players = Player.query.filter_by(game_id=game_id).all()

    # при начале дня очищаем результаты ночных проверок
    if game.phase == "day":
        game.don_check_result = None
        game.sheriff_check_result = None
        db.session.commit()

    if game.status == "finished":
        return redirect(url_for("game.game_result", game_id=game.id))

    if game.phase == "day":
        return render_template("game_day.html", game=game, players=players)

    if game.phase == "night_don":
        return redirect(url_for("game.night_don", game_id=game.id))

    if game.phase == "night_sheriff":
        return redirect(url_for("game.night_sheriff", game_id=game.id))

    return "Неизвестная фаза игры", 500



# голосование
@game_bp.route("/<int:game_id>/vote", methods=["GET"])
def vote_page(game_id):
    game = Game.query.get_or_404(game_id)
    players = Player.query.filter_by(game_id=game_id, alive=True).all()

    return render_template("vote.html", game=game, players=players)

@game_bp.route("/<int:game_id>/vote", methods=["POST"])
def vote(game_id):
    game = Game.query.get_or_404(game_id)

    alive_players = Player.query.filter_by(
        game_id=game_id,
        alive=True
    ).all()

    # если голосовать не за кого — конец игры
    if len(alive_players) <= 1:
        game.status = "finished"
        db.session.commit()
        return redirect(url_for("game.game_result", game_id=game_id))

    target_id = request.form.get("target")

    # если target не пришёл
    if not target_id:
        flash("Никто не выбран для голосования", "error")
        return redirect(url_for("game.game_view", game_id=game_id))

    victim = Player.query.get_or_404(int(target_id))
    victim.alive = False

    if check_game_end(game):
        db.session.commit()
        return redirect(url_for("game.game_result", game_id=game.id))
    
    game.phase = "night_kill"

    db.session.commit()
    return redirect(url_for("game.night_kill", game_id=game_id))



# стрельба
@game_bp.route("/<int:game_id>/night/kill", methods=["GET", "POST"])
def night_kill(game_id):
    game = Game.query.get_or_404(game_id)

    mafia = Player.query.filter(
        Player.game_id == game_id,
        Player.role.in_(["mafia", "don"]),
        Player.alive == True
    ).all()

    # если мафии нет — сразу дон
    if not mafia:
        return redirect(url_for("game.night_don", game_id=game_id))

    # цели — все живые НЕ мафия
    targets = Player.query.filter(
        Player.game_id == game_id,
        Player.alive == True,
        ~Player.role.in_(["mafia", "don"])
    ).all()

    if request.method == "POST":
        target_id = int(request.form["target"])
        target = Player.query.get_or_404(target_id)

        target.alive = False
        game.last_killed = target.name

        if check_game_end(game):
            db.session.commit()
            return redirect(url_for("game.game_result", game_id=game.id))

        game.phase = "night_don"

        db.session.commit()

        return render_template(
            "night_kill.html",
            game=game,
            killed=target
        )

    return render_template(
        "night_kill.html",
        game=game,
        targets=targets
    )



# ПЕРЕХОД НОЧЬ → ДЕНЬ
@game_bp.route("/<int:game_id>/next_day", methods=["POST"])
def next_day(game_id):
    game = Game.query.get_or_404(game_id)

    game.day += 1
    game.phase = "day"

    db.session.commit()
    return redirect(url_for("game.game_view", game_id=game_id))


# конец?
def check_game_end(game):
    alive_players = Player.query.filter_by(
        game_id=game.id,
        alive=True
    ).all()

    alive_black = sum(1 for p in alive_players if p.role in ("mafia", "don"))
    alive_red = sum(1 for p in alive_players if p.role not in ("mafia", "don"))

    # победа красных
    if alive_black == 0:
        game.status = "finished"
        game.winner = "red"
        return True

    # победа чёрных
    if alive_black >= alive_red:
        game.status = "finished"
        game.winner = "black"
        return True

    return False



# ФИНАЛЬНЫЙ ЭКРАН
@game_bp.route("/<int:game_id>/end")
def game_result(game_id):
    game = Game.query.get_or_404(game_id)
    players = Player.query.filter_by(game_id=game_id).all()

    winner_text = (
        "🔴 Победа красных"
        if game.winner == "red"
        else "⚫ Победа мафии"
    )

    return render_template(
        "game_result.html",
        game=game,
        players=players,
        winner_text=winner_text
    )
