"""
Imports Premier League player stats from Kaggle dataset.

Dataset: English Premier League Player Stats 2024/25
Source:  https://www.kaggle.com/datasets/aesika/english-premier-league-player-stats-2425

Setup:
    Place the CSV at: data/epl_player_stats_24_25.csv
    Run: python seed_players.py
"""

import csv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "data", "epl_player_stats_24_25.csv")

if not os.path.exists(CSV_PATH):
    print(f"CSV not found at {CSV_PATH}")
    print("Download from: https://www.kaggle.com/datasets/aesika/english-premier-league-player-stats-2425")
    print("Place at: data/epl_player_stats_24_25.csv")
    sys.exit(1)

sys.path.insert(0, SCRIPT_DIR)
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

inserted = skipped = 0

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        name = row["Player Name"].strip()
        club_name = row["Club"].strip()

        team = db.query(models.Team).filter(models.Team.name == club_name).first()
        if not team:
            print(f"Team not found.")
            skipped += 1
            continue

        existing = db.query(models.Player).filter(
            models.Player.name == name,
            models.Player.team_id == team.id,
        ).first()
        if existing:
            skipped += 1
            continue

        try:
            goals = int(row["Goals"]) if row["Goals"].strip() else 0
            assists = int(row["Assists"]) if row["Assists"].strip() else 0
            appearances = int(row["Appearances"]) if row["Appearances"].strip() else 0
        except ValueError:
            skipped += 1
            continue

        db.add(models.Player(
            name=name,
            nationality=row["Nationality"].strip(),
            position=row["Position"].strip(),
            goals=goals,
            assists=assists,
            appearances=appearances,
            team_id=team.id,
        ))
        inserted += 1

db.commit()
db.close()

print(f"Done. Inserted {inserted} players, skipped {skipped}.")