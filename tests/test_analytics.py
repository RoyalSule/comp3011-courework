import pytest

@pytest.fixture
def season_data(client, auth_headers):
    """Two teams with three matches: home wins 2, draws 1."""
    home = client.post("/teams/", json={
        "name": "Arsenal", "country": "England", "league": "Premier League"
    }, headers=auth_headers).json()
    away = client.post("/teams/", json={
        "name": "Chelsea", "country": "England", "league": "Premier League"
    }, headers=auth_headers).json()

    for home_score, away_score, date in [
        (2, 0, "2024-08-17T15:00:00"),
        (1, 0, "2024-09-14T15:00:00"),
        (1, 1, "2024-10-05T15:00:00"),
    ]:
        client.post("/matches/", json={
            "home_team_id": home["id"],
            "away_team_id": away["id"],
            "home_score": home_score,
            "away_score": away_score,
            "match_date": date,
            "league": "Premier League",
            "season": "2024/25",
        }, headers=auth_headers)

    return home, away

def test_standings(client, season_data):
    response = client.get("/analytics/standings?league=Premier League")
    assert response.status_code == 200
    table = response.json()
    assert table[0]["team_name"] == "Arsenal"
    assert table[0]["points"] == 7  # 2 wins + 1 draw
    assert table[0]["position"] == 1

def test_standings_goal_difference(client, season_data):
    table = client.get("/analytics/standings?league=Premier League").json()
    assert table[0]["goal_difference"] == 3  # scored 4, conceded 1

def test_team_form(client, auth_headers, season_data):
    home, _ = season_data
    response = client.get(f"/analytics/team/{home['id']}/form")
    assert response.status_code == 200
    data = response.json()
    assert data["form"] == "DWW"  # most recent first
    assert data["wins"] == 2
    assert data["draws"] == 1

def test_team_form_not_found(client):
    response = client.get("/analytics/team/999/form")
    assert response.status_code == 404

def test_goals_summary(client, auth_headers, season_data):
    response = client.get("/analytics/goals-summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_matches"] == 3
    assert data["total_goals"] == 5  # 2+0 + 1+0 + 1+1
    assert data["average_goals_per_match"] == round(5 / 3, 2)

def test_top_scorers_empty(client):
    response = client.get("/analytics/top-scorers")
    assert response.status_code == 200
    assert response.json() == []
