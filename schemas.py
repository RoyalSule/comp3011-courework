from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# Auth

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str


# Teams

class TeamCreate(BaseModel):
    name: str
    country: str
    league: str
    founded_year: Optional[int] = None
    stadium: Optional[str] = None

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    league: Optional[str] = None
    founded_year: Optional[int] = None
    stadium: Optional[str] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None
    goals_scored: Optional[int] = None
    goals_conceded: Optional[int] = None

class TeamOut(TeamCreate):
    id: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int

    model_config = {"from_attributes": True}


# Players

class PlayerCreate(BaseModel):
    name: str
    nationality: str
    position: str
    age: Optional[int] = None
    shirt_number: Optional[int] = None
    market_value_m: Optional[float] = None
    team_id: Optional[int] = None

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    nationality: Optional[str] = None
    position: Optional[str] = None
    age: Optional[int] = None
    shirt_number: Optional[int] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    appearances: Optional[int] = None
    market_value_m: Optional[float] = None
    team_id: Optional[int] = None

class PlayerOut(PlayerCreate):
    id: int
    goals: int
    assists: int
    appearances: int

    model_config = {"from_attributes": True}


# Matches

class MatchCreate(BaseModel):
    home_team_id: int
    away_team_id: int
    home_score: int = Field(..., ge=0)
    away_score: int = Field(..., ge=0)
    match_date: datetime
    league: str
    season: str
    stadium: Optional[str] = None
    attendance: Optional[int] = None

class MatchUpdate(BaseModel):
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    match_date: Optional[datetime] = None
    attendance: Optional[int] = None

class MatchOut(MatchCreate):
    id: int
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None

    model_config = {"from_attributes": True}


# Analytics

class StandingEntry(BaseModel):
    position: int
    team_id: int
    team_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    goal_difference: int
    points: int

class TopScorer(BaseModel):
    rank: int
    player_id: int
    player_name: str
    team: Optional[str]
    nationality: str
    position: str
    goals: int
    assists: int
    appearances: int
