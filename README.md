# Football Statistics API

A RESTful web API for football statistics built with FastAPI and SQLAlchemy. Supports full CRUD for teams, players, and match results, plus analytical endpoints for league standings, top scorers, team form, and goal summaries. Match data is imported from football-data.co.uk and write access is protected with JWT authentication.

---

## Requirements

- Python 3.10+
- pip

---

## Setup

1. Clone the repository

```bash
git clone https://github.com/RoyalSule/comp3011-courework.git
cd comp3011-courework
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Download the dataset

```bash
mkdir -p data
curl -o data/E0.csv https://www.football-data.co.uk/mmz4281/2425/E0.csv
```

Or paste the URL into your browser — it downloads immediately with no login required.

5. Seed the database

```bash
python seed_data.py
```

6. Run the server

```bash
uvicorn main:app --reload
```

The API is available at http://127.0.0.1:8000

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Docs

| | URL |
|---|---|
| Swagger UI (local) | http://127.0.0.1:8000/docs |
| Swagger UI (live) | https://royalsule.pythonanywhere.com/docs |

API documentation PDF is included in the repository.

---

## Authentication

Read endpoints are public. Write endpoints (POST, PATCH, DELETE) require a JWT token. Register and login via `/auth/register` and `/auth/login`, then pass the token as `Authorization: Bearer <token>`. You can test this in the Swagger UI.

---

## Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/teams/` | No | List teams |
| GET | `/teams/{id}` | No | Get team |
| POST | `/teams/` | Yes | Create team |
| PATCH | `/teams/{id}` | Yes | Update team |
| DELETE | `/teams/{id}` | Yes | Delete team |
| GET | `/players/` | No | List players |
| GET | `/players/{id}` | No | Get player |
| POST | `/players/` | Yes | Create player |
| PATCH | `/players/{id}` | Yes | Update player |
| DELETE | `/players/{id}` | Yes | Delete player |
| GET | `/matches/` | No | List matches |
| GET | `/matches/{id}` | No | Get match |
| POST | `/matches/` | Yes | Record match result |
| PATCH | `/matches/{id}` | Yes | Update match |
| DELETE | `/matches/{id}` | Yes | Delete match |
| GET | `/analytics/standings` | No | League table |
| GET | `/analytics/top-scorers` | No | Top goal scorers |
| GET | `/analytics/team/{id}/form` | No | Recent team form |
| GET | `/analytics/goals-summary` | No | Goal statistics |

---

## Project Structure

```
comp3011-courework/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── auth.py
├── seed_data.py
├── requirements.txt
├── README.md
├── api_documentation.pdf
├── data/
│   └── E0.csv
├── routers/
│   ├── teams.py
│   ├── players.py
│   ├── matches.py
│   └── analytics.py
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_teams.py
    ├── test_matches.py
    └── test_analytics.py
```

---

## Data Source

Match data is sourced from [football-data.co.uk](https://www.football-data.co.uk), used for educational purposes in accordance with their terms.

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | Deleted |
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |
| 409 | Conflict |
| 422 | Validation error |
| 429 | Too many requests |

---

## Deployment

Live at https://royalsule.pythonanywhere.com. Uses a custom ASGI-to-WSGI adapter as PythonAnywhere's free tier only supports WSGI.