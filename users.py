from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

fastapi = FastAPI()

engine = create_engine("postgresql+asyncpg://postgres:1234@localhost/users")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
session = SessionLocal()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String)
    password = Column(String)


class UserCreate(User):
    pass


class UserLogin(User):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@fastapi.post('/')
async def user_create(user: UserCreate, db: Session = Depends(get_db)):
    if session.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="user already exists")
    new_user = User(User.id == user.id, User.email == user.email, User.username == user.username, User.password == user.password)
    db.commit()
    return {"user successfuly created!"}

@fastapi.post('/')
async def user_login(user: UserLogin, db: Session = Depends(get_db)):
    if not session.query(User).filter(User.email == user.email).first():
        return {"user not found!"}
    if not session.query(User.password).filter(User.username == user.username).first() == user.password:
        return {"wrong password!"}
    user_name = session.query(User.username).filter(User.email == user.email).first()
    return {f"welcome {user_name}!"}