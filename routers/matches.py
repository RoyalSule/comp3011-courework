from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import models
import schemas
import auth
from database import get_db

router = APIRouter(prefix="/matches", tags=["Matches"])

def _build_match_out(match: models.Match) -> schemas.MatchOut:
    return schemas.MatchOut(
        id=match.id,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        home_score=match.home_score,
        away_score=match.away_score,
        match_date=match.match_date,
        league=match.league,
        season=match.season,
        stadium=match.stadium,
        attendance=match.attendance,
        home_team_name=match.home_team.name if match.home_team else None,
        away_team_name=match.away_team.name if match.away_team else None,
    )

def _update_team_stats(home: models.Team, away: models.Team, home_score: int, away_score: int):
    home.goals_scored += home_score
    home.goals_conceded += away_score
    away.goals_scored += away_score
    away.goals_conceded += home_score

    if home_score > away_score:
        home.wins += 1
        away.losses += 1
    elif away_score > home_score:
        away.wins += 1
        home.losses += 1
    else:
        home.draws += 1
        away.draws += 1

@router.get("/", response_model=List[schemas.MatchOut])
def list_matches(
    league: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    team_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Match)
    if league:
        query = query.filter(models.Match.league.ilike(f"%{league}%"))
    if season:
        query = query.filter(models.Match.season == season)
    if team_id:
        query = query.filter(
            (models.Match.home_team_id == team_id) | (models.Match.away_team_id == team_id)
        )
    return [_build_match_out(m) for m in query.offset(skip).limit(limit).all()]


@router.get("/{match_id}", response_model=schemas.MatchOut)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return _build_match_out(match)

@router.post("/", response_model=schemas.MatchOut, status_code=status.HTTP_201_CREATED)
def create_match(
    data: schemas.MatchCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.get_current_user),
):
    if data.home_team_id == data.away_team_id:
        raise HTTPException(status_code=400, detail="Home and away teams must differ")

    home = db.query(models.Team).filter(models.Team.id == data.home_team_id).first()
    away = db.query(models.Team).filter(models.Team.id == data.away_team_id).first()

    if not home:
        raise HTTPException(status_code=404, detail="Home team not found")
    if not away:
        raise HTTPException(status_code=404, detail="Away team not found")

    match = models.Match(**data.model_dump())
    db.add(match)
    _update_team_stats(home, away, data.home_score, data.away_score)
    db.commit()
    db.refresh(match)
    return _build_match_out(match)

@router.patch("/{match_id}", response_model=schemas.MatchOut)
def update_match(
    match_id: int,
    data: schemas.MatchUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.get_current_user),
):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(match, field, value)
    db.commit()
    db.refresh(match)
    return _build_match_out(match)

@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.get_current_user),
):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    db.delete(match)
    db.commit()
