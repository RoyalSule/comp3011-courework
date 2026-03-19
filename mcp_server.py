"""
MCP (Model Context Protocol) server implementation.

Exposes football statistics tools for AI assistants.
Available at: /mcp
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
import models

router = APIRouter(prefix="/mcp", tags=["MCP"])

TOOLS = [
    {
        "name": "get_standings",
        "description": "Get the current Premier League standings table sorted by points.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "league": {"type": "string", "description": "League name e.g. 'Premier League'"},
                "season": {"type": "string", "description": "Season e.g. '2024/25' (optional)"},
            },
            "required": ["league"],
        },
    },
    {
        "name": "get_top_scorers",
        "description": "Get the top goal scorers in the Premier League.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of players to return (default 10)"},
                "position": {"type": "string", "description": "Filter by position: GK, DEF, MID, FWD (optional)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_team_form",
        "description": "Get a team's recent match results as a form guide.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "team_id": {"type": "integer", "description": "The team's ID"},
                "last_n": {"type": "integer", "description": "Number of recent matches to include (default 5)"},
            },
            "required": ["team_id"],
        },
    },
    {
        "name": "get_teams",
        "description": "List all teams, optionally filtered by league.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "league": {"type": "string", "description": "Filter by league name (optional)"},
            },
            "required": [],
        },
    },
    {
        "name": "get_goals_summary",
        "description": "Get aggregate goal statistics across all recorded matches.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
]


class ToolCall(BaseModel):
    name: str
    arguments: Optional[dict] = {}


@router.get("")
def mcp_manifest():
    """MCP server manifest — describes available tools."""
    return {
        "protocol": "mcp",
        "version": "1.0",
        "name": "football-stats",
        "description": "Football statistics tools for Premier League data.",
        "tools": TOOLS,
    }


@router.post("/tools/call")
def call_tool(tool_call: ToolCall, db: Session = Depends(get_db)):
    """Execute a tool call and return the result."""
    name = tool_call.name
    args = tool_call.arguments or {}

    if name == "get_standings":
        league = args.get("league", "Premier League")
        season = args.get("season")
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
                tg = m.home_score if is_home else m.away_score
                og = m.away_score if is_home else m.home_score
                gf += tg; gc += og
                if tg > og: wins += 1
                elif tg == og: draws += 1
                else: losses += 1
            table.append({
                "team": team.name, "played": wins + draws + losses,
                "wins": wins, "draws": draws, "losses": losses,
                "goals_scored": gf, "goals_conceded": gc,
                "goal_difference": gf - gc, "points": wins * 3 + draws,
            })
        table.sort(key=lambda x: (-x["points"], -x["goal_difference"]))
        for i, e in enumerate(table): e["position"] = i + 1
        return {"tool": name, "result": table}

    elif name == "get_top_scorers":
        limit = args.get("limit", 10)
        position = args.get("position")
        query = db.query(models.Player).order_by(models.Player.goals.desc())
        if position:
            query = query.filter(models.Player.position.ilike(f"%{position}%"))
        players = query.limit(limit).all()
        return {"tool": name, "result": [
            {"rank": i + 1, "name": p.name, "team": p.team.name if p.team else None,
             "goals": p.goals, "assists": p.assists, "appearances": p.appearances}
            for i, p in enumerate(players)
        ]}

    elif name == "get_team_form":
        team_id = args.get("team_id")
        last_n = args.get("last_n", 5)
        team = db.query(models.Team).filter(models.Team.id == team_id).first()
        if not team:
            return {"tool": name, "error": f"Team {team_id} not found"}
        recent = (
            db.query(models.Match)
            .filter((models.Match.home_team_id == team_id) | (models.Match.away_team_id == team_id))
            .order_by(models.Match.match_date.desc())
            .limit(last_n).all()
        )
        results = []
        for m in recent:
            is_home = m.home_team_id == team_id
            ts = m.home_score if is_home else m.away_score
            os_ = m.away_score if is_home else m.home_score
            result = "W" if ts > os_ else "D" if ts == os_ else "L"
            results.append({"opponent": m.away_team.name if is_home else m.home_team.name,
                            "score": f"{ts}-{os_}", "result": result})
        return {"tool": name, "team": team.name,
                "form": "".join(r["result"] for r in results), "matches": results}

    elif name == "get_teams":
        league = args.get("league")
        query = db.query(models.Team)
        if league:
            query = query.filter(models.Team.league.ilike(f"%{league}%"))
        teams = query.all()
        return {"tool": name, "result": [
            {"id": t.id, "name": t.name, "league": t.league, "country": t.country}
            for t in teams
        ]}

    elif name == "get_goals_summary":
        from sqlalchemy import func
        total_matches = db.query(func.count(models.Match.id)).scalar()
        total_goals = db.query(func.sum(models.Match.home_score + models.Match.away_score)).scalar() or 0
        avg = round(total_goals / total_matches, 2) if total_matches else 0
        return {"tool": name, "result": {
            "total_matches": total_matches,
            "total_goals": total_goals,
            "average_goals_per_match": avg,
        }}

    return {"error": f"Unknown tool: {name}"}