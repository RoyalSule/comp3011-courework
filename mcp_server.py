"""
MCP (Model Context Protocol) server implementation.

Exposes football statistics tools for AI assistants.
Available at: /mcp
"""

import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Optional

router = APIRouter(prefix="/mcp", tags=["MCP"])

BASE_URL = "http://127.0.0.1:8000"

# MCP tool definitions
TOOLS = [
    {
        "name": "get_standings",
        "description": "Get the current Premier League standings table sorted by points.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "league": {
                    "type": "string",
                    "description": "League name e.g. 'Premier League'",
                },
                "season": {
                    "type": "string",
                    "description": "Season e.g. '2024/25' (optional)",
                },
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
                "limit": {
                    "type": "integer",
                    "description": "Number of players to return (default 10)",
                },
                "position": {
                    "type": "string",
                    "description": "Filter by position: GK, DEF, MID, FWD (optional)",
                },
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
                "team_id": {
                    "type": "integer",
                    "description": "The team's ID",
                },
                "last_n": {
                    "type": "integer",
                    "description": "Number of recent matches to include (default 5)",
                },
            },
            "required": ["team_id"],
        },
    },
    {
        "name": "get_teams",
        "description": "List all teams in the database, optionally filtered by league.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "league": {
                    "type": "string",
                    "description": "Filter by league name (optional)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_goals_summary",
        "description": "Get aggregate goal statistics across all recorded matches.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
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
async def call_tool(tool_call: ToolCall):
    """Execute a tool call and return the result."""
    name = tool_call.name
    args = tool_call.arguments or {}

    async with httpx.AsyncClient(base_url=BASE_URL) as client:

        if name == "get_standings":
            league = args.get("league", "Premier League")
            season = args.get("season")
            params = {"league": league}
            if season:
                params["season"] = season
            response = await client.get("/analytics/standings", params=params)

        elif name == "get_top_scorers":
            params = {}
            if "limit" in args:
                params["limit"] = args["limit"]
            if "position" in args:
                params["position"] = args["position"]
            response = await client.get("/analytics/top-scorers", params=params)

        elif name == "get_team_form":
            team_id = args.get("team_id")
            last_n = args.get("last_n", 5)
            response = await client.get(f"/analytics/team/{team_id}/form", params={"last_n": last_n})

        elif name == "get_teams":
            params = {}
            if "league" in args:
                params["league"] = args["league"]
            response = await client.get("/teams/", params=params)

        elif name == "get_goals_summary":
            response = await client.get("/analytics/goals-summary")

        else:
            return {"error": f"Unknown tool: {name}"}

    return {
        "tool": name,
        "result": response.json(),
    }
