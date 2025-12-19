import pandas as pd
import numpy as np

def generate_mafia_data(n_games=500):
  np.random.seed(42)
  data = []

  for game_id in range(n_games):

    sheriff_accuracy = np.clip(np.random.normal(0.65, 0.15), 0, 1)

    don_checks = np.clip(np.random.normal(0.55, 0.12), 0, 1)

    game_length = int(np.clip(np.random.normal(27, 4), 15, 45))

    fouls = max(0, int(np.random.poisson(1)))


    mafia_prob = (
        0.45  # базовое
        + 0.35 * don_checks
        - 0.55 * sheriff_accuracy
        + 0.02 * (fouls > 2)
    )
    mafia_prob = np.clip(mafia_prob, 0.05, 0.95)
    mafia_win = np.random.rand() < mafia_prob

    data.append({
        "game_id": game_id,
        "mafia_win": int(mafia_win),
        "sheriff_accuracy": sheriff_accuracy,
        "game_length": game_length,
        "fouls": fouls,
        "don_checks": don_checks
    })

  return pd.DataFrame(data)

df = generate_mafia_data(500)
df.to_csv("mafia_data.csv", index=False)
df.head()
