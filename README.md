# SportsPulse API

## Overview

SportsPulse is a RESTful web API for football statistics, built as part of COMP3011 Web Services and Web Data at the University of Leeds. It provides a structured interface for storing and querying football data — including teams, players, and match results — backed by a SQLite database and exposed through a clean set of HTTP endpoints.

The API is built with FastAPI and SQLAlchemy, and ships with a data importer that loads real 2024/25 Premier League match results directly from football-data.co.uk. Alongside standard CRUD operations, it offers analytical endpoints that compute live league standings, top scorer rankings, team form guides, and goal summaries. Write access is protected with JWT authentication, while all read endpoints are publicly accessible.

---

## Requirements

- Python 3.10+
- pip

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/your-username/sportspulse-api.git
cd sportspulse-api
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Download the dataset**
```bash
mkdir -p data
curl -o data/E0.csv https://www.football-data.co.uk/mmz4281/2425/E0.csv
```
> Or paste the URL into your browser — it downloads immediately with no login required.

**5. Seed the database**
```bash
python seed_data.py
```

**6. Set your secret key (recommended)**
```bash
# macOS / Linux
export SECRET_KEY="your-secret-key-here"

# Windows
set SECRET_KEY=your-secret-key-here
```
> If not set, the app falls back to a default key. Always set this in production.

**7. Run the server**
```bash
uvicorn main:app --reload
```

The API is now available at `http://127.0.0.1:8000`

---

## Interactive Docs

| Interface | URL |
|-----------|-----|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| API Documentation PDF | `api_documentation.pdf` in this repo |

---

## Authentication

Read endpoints are public. Write endpoints (POST, PATCH, DELETE) require a JWT token.

**Register**
```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret123"}'
```

**Login**
```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=admin&password=secret123"
```

**Use the token**
```bash
curl -X POST http://127.0.0.1:8000/teams/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Everton", "country": "England", "league": "Premier League"}'
```

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
sportspulse-api/
├── main.py             # App entry point, auth routes
├── database.py         # DB engine and session
├── models.py           # SQLAlchemy models
├── schemas.py          # Pydantic schemas
├── auth.py             # JWT authentication
├── seed_data.py        # CSV importer
├── requirements.txt
├── README.md
├── api_documentation.pdf
├── data/
│   └── E0.csv          # Downloaded dataset (not committed to git)
└── routers/
    ├── teams.py
    ├── players.py
    ├── matches.py
    └── analytics.py
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
| 409 | Conflict (duplicate) |
| 422 | Validation error |

---

## Author

Royal Sule  
University of Leeds  
2026
