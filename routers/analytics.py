from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/standings", response_model=List[schemas.StandingEntry])
def standings(
    league: str = Query(...),
    season: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """League table sorted by points then goal difference."""
    teams = db.query(models.Team).filter(models.Team.league.ilike(f"%{league}%")).all()

    table = []
    for team in teams:
        query = db.query(models.Match).filter(
            (models.Match.home_team_id == team.id) | (models.Match.away_team_id == team.id),
            models.Match.league.ilike(f"%{league}%"),
        )
        if season:
            query = query.filter(models.Match.season == season)

        wins = draws = losses = gf = gc = 0
        for m in query.all():
            is_home = m.home_team_id == team.id
            team_goals = m.home_score if is_home else m.away_score
            opp_goals = m.away_score if is_home else m.home_score
            gf += team_goals
            gc += opp_goals
            if team_goals > opp_goals:
                wins += 1
            elif team_goals == opp_goals:
                draws += 1
            else:
                losses += 1

        table.append({
            "position": 0,
            "team_id": team.id,
            "team_name": team.name,
            "played": wins + draws + losses,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_scored": gf,
            "goals_conceded": gc,
            "goal_difference": gf - gc,
            "points": wins * 3 + draws,
        })

    table.sort(key=lambda x: (-x["points"], -x["goal_difference"], -x["goals_scored"]))
    for i, entry in enumerate(table):
        entry["position"] = i + 1

    return table


@router.get("/top-scorers", response_model=List[schemas.TopScorer])
def top_scorers(
    limit: int = Query(10, ge=1, le=50),
    position: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Ranked list of players by goals scored."""
    query = db.query(models.Player).order_by(models.Player.goals.desc())
    if position:
        query = query.filter(models.Player.position.ilike(f"%{position}%"))

    return [
        schemas.TopScorer(
            rank=i + 1,
            player_id=p.id,
            player_name=p.name,
            team=p.team.name if p.team else None,
            nationality=p.nationality,
            position=p.position,
            goals=p.goals,
            assists=p.assists,
            appearances=p.appearances,
        )
        for i, p in enumerate(query.limit(limit).all())
    ]


@router.get("/team/{team_id}/form")
def team_form(
    team_id: int,
    last_n: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Recent match results for a team as a W/D/L form string."""
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise ValueError(f"Team {team_id} not found")

    recent = (
        db.query(models.Match)
        .filter(
            (models.Match.home_team_id == team_id) | (models.Match.away_team_id == team_id)
        )
        .order_by(models.Match.match_date.desc())
        .limit(last_n)
        .all()
    )

    results = []
    for m in recent:
        is_home = m.home_team_id == team_id
        team_score = m.home_score if is_home else m.away_score
        opp_score = m.away_score if is_home else m.home_score
        opponent = m.away_team.name if is_home else m.home_team.name

        if team_score > opp_score:
            result = "W"
        elif team_score == opp_score:
            result = "D"
        else:
            result = "L"

        results.append({
            "match_id": m.id,
            "date": m.match_date.isoformat(),
            "opponent": opponent,
            "venue": "H" if is_home else "A",
            "score": f"{team_score}-{opp_score}",
            "result": result,
        })

    return {
        "team_id": team_id,
        "team_name": team.name,
        "form": "".join(r["result"] for r in results),
        "wins": sum(1 for r in results if r["result"] == "W"),
        "draws": sum(1 for r in results if r["result"] == "D"),
        "losses": sum(1 for r in results if r["result"] == "L"),
        "matches": results,
    }


@router.get("/goals-summary")
def goals_summary(db: Session = Depends(get_db)):
    """Aggregate goal statistics across all recorded matches."""
    total_matches = db.query(func.count(models.Match.id)).scalar()
    total_goals = db.query(func.sum(models.Match.home_score + models.Match.away_score)).scalar() or 0
    avg_goals = round(total_goals / total_matches, 2) if total_matches else 0

    top = (
        db.query(models.Match)
        .order_by((models.Match.home_score + models.Match.away_score).desc())
        .first()
    )

    return {
        "total_matches": total_matches,
        "total_goals": total_goals,
        "average_goals_per_match": avg_goals,
        "highest_scoring_match": {
            "match_id": top.id,
            "score": f"{top.home_score}-{top.away_score}",
        } if top else None,
    }
