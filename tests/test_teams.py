def test_create_team(client, auth_headers):
    response = client.post("/teams/", json={
        "name": "Arsenal", "country": "England", "league": "Premier League"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Arsenal"


def test_create_team_duplicate(client, auth_headers):
    payload = {"name": "Arsenal", "country": "England", "league": "Premier League"}
    client.post("/teams/", json=payload, headers=auth_headers)
    response = client.post("/teams/", json=payload, headers=auth_headers)
    assert response.status_code == 409


def test_create_team_unauthenticated(client):
    response = client.post("/teams/", json={
        "name": "Arsenal", "country": "England", "league": "Premier League"
    })
    assert response.status_code == 401


def test_list_teams(client, auth_headers):
    client.post("/teams/", json={"name": "Arsenal", "country": "England", "league": "Premier League"}, headers=auth_headers)
    client.post("/teams/", json={"name": "Real Madrid", "country": "Spain", "league": "La Liga"}, headers=auth_headers)
    response = client.get("/teams/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_teams_filter_by_league(client, auth_headers):
    client.post("/teams/", json={"name": "Arsenal", "country": "England", "league": "Premier League"}, headers=auth_headers)
    client.post("/teams/", json={"name": "Real Madrid", "country": "Spain", "league": "La Liga"}, headers=auth_headers)
    response = client.get("/teams/?league=Premier League")
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Arsenal"


def test_get_team(client, auth_headers):
    created = client.post("/teams/", json={
        "name": "Arsenal", "country": "England", "league": "Premier League"
    }, headers=auth_headers).json()
    response = client.get(f"/teams/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Arsenal"


def test_get_team_not_found(client):
    response = client.get("/teams/999")
    assert response.status_code == 404


def test_update_team(client, auth_headers):
    created = client.post("/teams/", json={
        "name": "Arsenal", "country": "England", "league": "Premier League"
    }, headers=auth_headers).json()
    response = client.patch(f"/teams/{created['id']}", json={"wins": 10}, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["wins"] == 10


def test_delete_team(client, auth_headers):
    created = client.post("/teams/", json={
        "name": "Arsenal", "country": "England", "league": "Premier League"
    }, headers=auth_headers).json()
    response = client.delete(f"/teams/{created['id']}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get(f"/teams/{created['id']}").status_code == 404
