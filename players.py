from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import models
import schemas
import auth
from database import get_db

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("/", response_model=List[schemas.PlayerOut])
def list_players(
    position: Optional[str] = Query(None),
    team_id: Optional[int] = Query(None),
    nationality: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Player)
    if position:
        query = query.filter(models.Player.position.ilike(f"%{position}%"))
    if team_id:
        query = query.filter(models.Player.team_id == team_id)
    if nationality:
        query = query.filter(models.Player.nationality.ilike(f"%{nationality}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/{player_id}", response_model=schemas.PlayerOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.post("/", response_model=schemas.PlayerOut, status_code=status.HTTP_201_CREATED)
def create_player(
    data: schemas.PlayerCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.get_current_user),
):
    if data.team_id:
        if not db.query(models.Team).filter(models.Team.id == data.team_id).first():
            raise HTTPException(status_code=404, detail="Team not found")
    player = models.Player(**data.model_dump())
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@router.patch("/{player_id}", response_model=schemas.PlayerOut)
def update_player(
    player_id: int,
    data: schemas.PlayerUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.get_current_user),
):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(player, field, value)
    db.commit()
    db.refresh(player)
    return player


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.get_current_user),
):
    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    db.delete(player)
    db.commit()
