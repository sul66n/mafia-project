import random


def assign_roles(players):
    roles = ["mafia", "mafia", "sheriff"] + \
            ["civilian"] * (len(players) - 3)
    random.shuffle(roles)

    for player, role in zip(players, roles):
        player.role = role





