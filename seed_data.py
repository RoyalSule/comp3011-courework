"""
Imports Premier League match data from football-data.co.uk into the database.

Dataset: 2024/25 Premier League season
Source:  https://www.football-data.co.uk/mmz4281/2425/E0.csv

Setup:
    mkdir -p data
    curl -o data/E0.csv https://www.football-data.co.uk/mmz4281/2425/E0.csv
    python seed_data.py
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "data", "E0.csv")

if not os.path.exists(CSV_PATH):
    print(f"CSV not found at {CSV_PATH}")
    print("Download it with:")
    print("  mkdir -p data")
    print("  curl -o data/E0.csv https://www.football-data.co.uk/mmz4281/2425/E0.csv")
    sys.exit(1)

sys.path.insert(0, SCRIPT_DIR)
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

LEAGUE = "Premier League"
SEASON = "2024/25"
COUNTRY = "England"

def parse_date(date_str: str) -> datetime:
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: {date_str}")

# Read CSV, skip rows with no result (future fixtures)
rows, team_names = [], set()
with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        home = row.get("HomeTeam", "").strip()
        away = row.get("AwayTeam", "").strip()
        if home and away and row.get("FTHG", "").strip() and row.get("FTAG", "").strip():
            team_names.update([home, away])
            rows.append(row)

print(f"Found {len(team_names)} teams and {len(rows)} completed matches.")

# Insert teams, skip any that already exist
team_map = {}
for name in sorted(team_names):
    team = db.query(models.Team).filter(models.Team.name == name).first()
    if not team:
        team = models.Team(name=name, country=COUNTRY, league=LEAGUE)
        db.add(team)
        db.flush()
    team_map[name] = team
db.commit()

# Accumulate stats in memory, then bulk-update once at the end
stats = defaultdict(lambda: dict(wins=0, draws=0, losses=0, goals_scored=0, goals_conceded=0))

inserted = skipped = 0
for row in rows:
    home_name = row["HomeTeam"].strip()
    away_name = row["AwayTeam"].strip()

    try:
        home_score = int(row["FTHG"])
        away_score = int(row["FTAG"])
        match_date = parse_date(row.get("Date", "").strip())
    except ValueError:
        skipped += 1
        continue

    home_team = team_map.get(home_name)
    away_team = team_map.get(away_name)
    if not home_team or not away_team:
        skipped += 1
        continue

    # Skip duplicates so the script is safe to re-run
    exists = db.query(models.Match).filter(
        models.Match.home_team_id == home_team.id,
        models.Match.away_team_id == away_team.id,
        models.Match.match_date == match_date,
    ).first()
    if exists:
        skipped += 1
        continue

    db.add(models.Match(
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        home_score=home_score,
        away_score=away_score,
        match_date=match_date,
        league=LEAGUE,
        season=SEASON,
    ))

    stats[home_name]["goals_scored"] += home_score
    stats[home_name]["goals_conceded"] += away_score
    stats[away_name]["goals_scored"] += away_score
    stats[away_name]["goals_conceded"] += home_score

    if home_score > away_score:
        stats[home_name]["wins"] += 1
        stats[away_name]["losses"] += 1
    elif away_score > home_score:
        stats[away_name]["wins"] += 1
        stats[home_name]["losses"] += 1
    else:
        stats[home_name]["draws"] += 1
        stats[away_name]["draws"] += 1

    inserted += 1

db.commit()

for name, s in stats.items():
    team = team_map.get(name)
    if team:
        for field, value in s.items():
            setattr(team, field, value)
db.commit()
db.close()

print(f"Done. Inserted {inserted} matches, skipped {skipped}.")
