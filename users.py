from fastapi import FastAPI, HTTPException, Depends, Body
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from auth_handler import sign_jwt
import bcrypt
from auth_bearer import JWTBearer, IsAdmin
fastapi = FastAPI()

engine = create_engine("postgresql://postgres:1234@localhost/users")
engine1 = create_engine("postgresql://postgres:1234@localhost/products")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
Base = declarative_base()
session = SessionLocal()
session1 = SessionLocal1()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String)
    password = Column(String)
    role = Column(String, default="user")

Base.metadata.create_all(bind=engine)


class UserLogin(BaseModel):
    email:str
    password:str
    role:str

class UserCreate(BaseModel):
    email:str
    username:str
    password:str
    role:str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db1():
    db = SessionLocal1()
    try:
        yield db
    finally:
        db.close()


@fastapi.post('/signup/')
def user_create(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="user already exists")
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(email = user.email, username = user.username, password = hashed_pw.decode('utf-8'), role = user.role)
#we firstly encode the password given by the user in the create user, and store that encoded thing in a variable (hashed_pw), then when we come to add it to our db we decode it    
    db.add(new_user)
    db.commit()
    return sign_jwt(user_id=user.email, role=user.role)


@fastapi.post('/signin/')
def user_login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="user not found!")
    passkey = db.query(User.password).filter(User.email == user.email).first()
    if bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
#we now take the password entered by the user in the sign in process, then we use the checkpw function by bcrypt to see if the encoded version of the user password matches the encoded version of the password in our db        
        return sign_jwt(user_id=user.email, role=user.role)
#we return the encoded token to the user once he signs up or in, this token will be later used to access secured routes
    else:
        raise HTTPException(status_code=401, detail="incorrect password!")
    

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    price = Column(Integer)    


Base.metadata.create_all(bind=engine1)


class ProductCreate(BaseModel):
    name:str
    description:str
    price:int


class ProductResponse(BaseModel):
    name:str
    description:str
    price:int


@fastapi.post('/addproduct/', dependencies=[Depends(IsAdmin())], tags=["products"])
def product_create(product: ProductCreate, db: Session = Depends(get_db1)):
    if db.query(Product).filter(Product.name == product.name).first():
        raise HTTPException(status_code=404, detail="product already exists!")
    new_product = Product(name = product.name, description = product.description, price = product.price)
    db.add(new_product)
    db.commit()
    return {"product added!"}


@fastapi.get('/displayproducts/{Product.id}', dependencies=[Depends(JWTBearer())], response_model=ProductResponse)
def display_products(product_id:int, db: Session = Depends(get_db1)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="product already exists!")
    return product
#the post and get methods for the products are secured routes, i ll now make the post method only accessible by admin (dk how but will get it)
