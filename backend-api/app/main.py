"""
Main FastAPI app for Wellness at Work backend.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from . import models, schemas, database, crud, auth
from .database import SessionLocal, engine
from typing import List

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"msg": "Wellness at Work API is running."}

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get JWT token."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/blinks/upload", response_model=schemas.BlinkDataOut)
def upload_blink(blink: schemas.BlinkDataCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Upload blink data for the current user."""
    return crud.create_blink_data(db, user_id=current_user.id, blink=blink)

@app.get("/blinks/user", response_model=List[schemas.BlinkDataOut])
def get_user_blinks(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Get all blink data for the current user."""
    return crud.get_blinks_for_user(db, user_id=current_user.id) 