from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import auth
import models
import schemas
from database import engine, get_db
from routers import analytics, matches, players, teams

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Football Statistics API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(teams.router)
app.include_router(players.router)
app.include_router(matches.router)
app.include_router(analytics.router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "SportsPulse API", "docs": "/docs"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/auth/register", response_model=schemas.UserOut, status_code=201, tags=["Auth"])
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    user = models.User(username=data.username, hashed_password=auth.hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=schemas.Token, tags=["Auth"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form.username).first()
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": auth.create_access_token({"sub": user.username}), "token_type": "bearer"}
