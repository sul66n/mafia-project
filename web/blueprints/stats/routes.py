from flask import render_template, send_file
from . import stats_bp
import pandas as pd
import matplotlib.pyplot as plt
import io


@stats_bp.route("/")
def Stats():
    return render_template("stats.html")


@stats_bp.route("/mafia-length-plot")
def mafia_length_plot():
    df = pd.read_csv("data/mafia_data.csv")

    plt.figure(figsize=(6, 4))
    plt.scatter(df["game_length"], df["mafia_win"], alpha=0.3)
    plt.xlabel("Длительность игры")
    plt.ylabel("Победа мафии (1 = да)")
    plt.title("Влияние длительности игры на победу мафии")

    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format="png")
    plt.close()
    img.seek(0)

    return send_file(img, mimetype="image/png")
