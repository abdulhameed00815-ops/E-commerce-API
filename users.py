from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

fastapi = FastAPI()

engine = create_engine("postgresql://postgres:1234@localhost/users")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
session = SessionLocal()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String)
    password = Column(String)


Base.metadata.create_all(bind=engine)
    

class UserLogin(BaseModel):
    email:str
    username:str
    password:str


class UserCreate(BaseModel):
    email:str
    username:str
    password:str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@fastapi.post('/signup/')
def user_create(user: UserCreate, db: Session = Depends(get_db)):
    if session.query(User.email).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="user already exists")
    new_user = User(email = user.email, username = user.username, password = user.password)
    db.add(new_user)
    db.commit()
    return {"user successfuly created!"}


@fastapi.post('/signin/')
def user_login(user: UserLogin, db: Session = Depends(get_db)):
    if not session.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="user not found!")
    if not session.query(User.password).filter(User.username == user.username).first() == user.password:
        raise HTTPException(status_code=404, detail="wrong password!")
    user_name = session.query(User.username).filter(User.email == user.email).first()
    return {f"welcome {user_name}!"}