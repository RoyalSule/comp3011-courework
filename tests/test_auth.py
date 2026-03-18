def test_register(client):
    response = client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    assert response.status_code == 201
    assert response.json()["username"] == "alice"

def test_register_duplicate(client):
    client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    response = client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    assert response.status_code == 409

def test_login(client):
    client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    response = client.post("/auth/login", data={"username": "alice", "password": "pass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "alice", "password": "pass123"})
    response = client.post("/auth/login", data={"username": "alice", "password": "wrong"})
    assert response.status_code == 401
