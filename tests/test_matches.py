import pytest


@pytest.fixture
def two_teams(client, auth_headers):
    home = client.post("/teams/", json={
        "name": "Arsenal", "country": "England", "league": "Premier League"
    }, headers=auth_headers).json()
    away = client.post("/teams/", json={
        "name": "Chelsea", "country": "England", "league": "Premier League"
    }, headers=auth_headers).json()
    return home, away


def test_create_match(client, auth_headers, two_teams):
    home, away = two_teams
    response = client.post("/matches/", json={
        "home_team_id": home["id"],
        "away_team_id": away["id"],
        "home_score": 2,
        "away_score": 1,
        "match_date": "2024-09-22T15:00:00",
        "league": "Premier League",
        "season": "2024/25",
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["home_score"] == 2


def test_create_match_same_team(client, auth_headers, two_teams):
    home, _ = two_teams
    response = client.post("/matches/", json={
        "home_team_id": home["id"],
        "away_team_id": home["id"],
        "home_score": 2,
        "away_score": 1,
        "match_date": "2024-09-22T15:00:00",
        "league": "Premier League",
        "season": "2024/25",
    }, headers=auth_headers)
    assert response.status_code == 400


def test_create_match_invalid_team(client, auth_headers, two_teams):
    home, _ = two_teams
    response = client.post("/matches/", json={
        "home_team_id": home["id"],
        "away_team_id": 999,
        "home_score": 1,
        "away_score": 0,
        "match_date": "2024-09-22T15:00:00",
        "league": "Premier League",
        "season": "2024/25",
    }, headers=auth_headers)
    assert response.status_code == 404


def test_match_updates_team_stats(client, auth_headers, two_teams):
    home, away = two_teams
    client.post("/matches/", json={
        "home_team_id": home["id"],
        "away_team_id": away["id"],
        "home_score": 3,
        "away_score": 0,
        "match_date": "2024-09-22T15:00:00",
        "league": "Premier League",
        "season": "2024/25",
    }, headers=auth_headers)
    home_updated = client.get(f"/teams/{home['id']}").json()
    away_updated = client.get(f"/teams/{away['id']}").json()
    assert home_updated["wins"] == 1
    assert home_updated["goals_scored"] == 3
    assert away_updated["losses"] == 1
    assert away_updated["goals_conceded"] == 3


def test_list_matches_filter_by_team(client, auth_headers, two_teams):
    home, away = two_teams
    client.post("/matches/", json={
        "home_team_id": home["id"],
        "away_team_id": away["id"],
        "home_score": 1,
        "away_score": 0,
        "match_date": "2024-09-22T15:00:00",
        "league": "Premier League",
        "season": "2024/25",
    }, headers=auth_headers)
    response = client.get(f"/matches/?team_id={home['id']}")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_delete_match(client, auth_headers, two_teams):
    home, away = two_teams
    match = client.post("/matches/", json={
        "home_team_id": home["id"],
        "away_team_id": away["id"],
        "home_score": 1,
        "away_score": 1,
        "match_date": "2024-09-22T15:00:00",
        "league": "Premier League",
        "season": "2024/25",
    }, headers=auth_headers).json()
    response = client.delete(f"/matches/{match['id']}", headers=auth_headers)
    assert response.status_code == 204
