from sqlalchemy.orm import Session
from . import models, schemas, auth
from typing import List

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password, consent=user.consent)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_blink_data(db: Session, user_id: int, blink: schemas.BlinkDataCreate):
    db_blink = models.BlinkData(user_id=user_id, blink_count=blink.blink_count, timestamp=blink.timestamp)
    db.add(db_blink)
    db.commit()
    db.refresh(db_blink)
    return db_blink

def get_blinks_for_user(db: Session, user_id: int) -> List[models.BlinkData]:
    return db.query(models.BlinkData).filter(models.BlinkData.user_id == user_id).order_by(models.BlinkData.timestamp.desc()).all() 