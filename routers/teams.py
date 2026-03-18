from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import models
import schemas
import auth
from database import get_db

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("/", response_model=List[schemas.TeamOut])
def list_teams(
    league: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Team)
    if league:
        query = query.filter(models.Team.league.ilike(f"%{league}%"))
    if country:
        query = query.filter(models.Team.country.ilike(f"%{country}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/{team_id}", response_model=schemas.TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.post("/", response_model=schemas.TeamOut, status_code=status.HTTP_201_CREATED)
def create_team(
    data: schemas.TeamCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.get_current_user),
):
    if db.query(models.Team).filter(models.Team.name == data.name).first():
        raise HTTPException(status_code=409, detail="Team name already exists")
    team = models.Team(**data.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    return team

@router.patch("/{team_id}", response_model=schemas.TeamOut)
def update_team(
    team_id: int,
    data: schemas.TeamUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.get_current_user),
):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(team, field, value)
    db.commit()
    db.refresh(team)
    return team

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.get_current_user),
):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()
