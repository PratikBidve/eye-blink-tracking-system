from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    consent: bool = False

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class BlinkDataBase(BaseModel):
    blink_count: int
    timestamp: Optional[datetime] = None

class BlinkDataCreate(BlinkDataBase):
    pass

class BlinkDataOut(BlinkDataBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 