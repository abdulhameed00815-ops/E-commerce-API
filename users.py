from fastapi import FastAPI, HTTPException, Depends, Body, Request 
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship 
from pydantic import BaseModel
import bcrypt
from fastapi.responses import JSONResponse
from fastapi_jwt_auth2 import AuthJWT
from fastapi_jwt_auth2.exceptions import AuthJWTException
from decouple import config
from fastapi.middleware.cors import CORSMiddleware
import re

email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

fastapi = FastAPI()

from fastapi.openapi.utils import get_openapi

origins = [
        "http://localhost:5500"
]

fastapi.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)


engine_users = create_engine("postgresql://postgres:1234@localhost/users")
engine_products = create_engine("postgresql://postgres:1234@localhost/products")
engine_carts = create_engine("postgresql://postgres:1234@localhost/carts")

SessionLocal_users = sessionmaker(autocommit=False, autoflush=False, bind=engine_users)
SessionLocal_products = sessionmaker(autocommit=False, autoflush=False, bind=engine_products)
SessionLocal_carts = sessionmaker(autocommit=False, autoflush=False, bind=engine_carts)

Base = declarative_base()
session_users = SessionLocal_users()
session_products = SessionLocal_products()
session_carts = SessionLocal_carts()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String)
    password = Column(String)
    role = Column(String, default="user")


Base.metadata.create_all(bind=engine_users)
JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


class Settings(BaseModel):
    authjwt_secret_key: str = JWT_SECRET


@AuthJWT.load_config
def get_config():
    return Settings()


@fastapi.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
        )


class UserLogin(BaseModel):
    email:str
    password:str

class UserCreate(BaseModel):
    email:str
    username:str
    password:str

def get_db_users():
    db = SessionLocal_users()
    try:
        yield db
    finally:
        db.close()


def get_db_products():
    db = SessionLocal_products()
    try:
        yield db
    finally:
        db.close()



def get_db_carts():
    db = SessionLocal_carts()
    try:
        yield db
    finally:
        db.close()


@fastapi.post('/signup/')
def user_create(user: UserCreate, db: Session = Depends(get_db_users), Authorize: AuthJWT = Depends()):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="user already exists")
    if not re.fullmatch(email_regex, user.email):
        raise HTTPException(status_code=400, detail="invalid email")
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(email = user.email, username = user.username, password = hashed_pw.decode('utf-8'))
#we firstly encode the password given by the user in the create user, and store that encoded thing in a variable (hashed_pw), then when we come to add it to our db we decode it    
    db.add(new_user)
    db.commit()
    email1 = user.email
    user_id = db.query(User.id).filter(User.email == user.email).scalar()
    role1 = db.query(User.role).filter(User.email == user.email).scalar() 
    access_token = Authorize.create_access_token(subject=user_id, user_claims={"email": email1, "role": role1})
    refresh_token = Authorize.create_refresh_token(subject=user_id, user_claims={"email": email1, "role": role1})
    return {"access_token": access_token, "refresh_token": refresh_token}

@fastapi.post('/signin/')
def user_login(user: UserLogin, db: Session = Depends(get_db_users), Authorize: AuthJWT = Depends()):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="user not found!")
    passkey = db.query(User.password).filter(User.email == user.email).first()
    if bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
#we now take the password entered by the user in the sign in process, then we use the checkpw function by bcrypt to see if the encoded version of the user password matches the encoded version of the password in our db        
        user_id = db.query(User.id).filter(User.email == user.email).scalar()
        role1 = db.query(User.role).filter(User.email == user.email).scalar() 
        role1 = str(role1).strip()
        access_token = Authorize.create_access_token(subject=user_id, user_claims={"email": user.email, "role": role1})
        refresh_token = Authorize.create_refresh_token(subject=user_id, user_claims={"email": user.email, "role": role1})
        return {"access_token": access_token, "refresh_token": refresh_token}
#we return the encoded token to the user once he signs up or in, this token will be later used to access secured routes
    else:
        raise HTTPException(status_code=401, detail="incorrect password!")
    
#requires a token of type "refresh", if handed to it properly, you ll get a brand new fresh access token everytime
@fastapi.post('/refresh/')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    claims = Authorize.get_raw_jwt()
    email = claims.get("email")
    role = claims.get("role")
    new_access_token = Authorize.create_access_token(user_claims={"email": email, "role": role})
    return {"access token": new_access_token}


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    price = Column(Integer)    


Base.metadata.create_all(bind=engine_products)


class ProductCreate(BaseModel):
    name:str
    description:str
    price:int


class ProductResponse(BaseModel):
    name:str
    description:str
    price:int


def user_role(Authorize:AuthJWT = Depends()):
    claims = Authorize.get_raw_jwt()
    role = claims.get("role")
    return role


@fastapi.get('/displayproducts/')
def display_products(db: Session = Depends(get_db_products)):
    products = db.query(Product).all()
    return products


@fastapi.post('/addproduct/', tags=["products"])
def product_create(product: ProductCreate, db: Session = Depends(get_db_products)):
    if db.query(Product).filter(Product.name == product.name).first():
        raise HTTPException(status_code=404, detail="product already exists!")
    new_product = Product(name = product.name, description = product.description, price = product.price)
    db.add(new_product)
    db.commit()
    return {"product added!"}


@fastapi.get('/searchproducts/{Product.name}', response_model=ProductResponse, tags=["products"])
def search_products(product_name: str, db: Session = Depends(get_db_products)):
    product_found = db.query(Product).filter(Product.name == product_name).first()
    if not product_found:
        raise HTTPException(status_code=404, detail="product not found bitch")
    return product_found
#the post and get methods for the products are secured routes, i ll now make the post method only accessible by admin (dk how but will get it


class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    product_id = Column(Integer)


Base.metadata.create_all(bind=engine_carts)


class AddToCart(BaseModel):
    product_id:int


class GetCart(BaseModel):
    cart_id:int


class RemoveProductFromCart(BaseModel):
    product_id:int
    

def user_email(Authorize:AuthJWT = Depends()):
    claims = Authorize.get_raw_jwt()
    if claims == None:
        raise HTTPException(status_code=403, detail="login first bitch!")
    email = claims.get("email")
    return email


#endpoint for adding a product to cart
@fastapi.post('/addtocart/', tags=["cart"])
def add_to_cart(product: AddToCart, db_carts: Session = Depends(get_db_carts), db_products: Session = Depends(get_db_products), email: str = Depends(user_email), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required() 
    product_id1 = db_products.query(Product.id).filter(Product.id == product.product_id).scalar()
    if not product_id1:
        raise HTTPException(status_code=404, detail="product not found!")
    added_product = Cart(user_id = email, product_id = product_id1)
    db_carts.add(added_product)
    db_carts.commit()
    return {"product added to cart successfuly!"}
        
#endpoint for viewing stuff in cart
@fastapi.get('/viewcart/{Cart.id}', tags=["cart"])
def view_cart(email: str = Depends(user_email), db_carts: Session = Depends(get_db_carts), db_products: Session = Depends(get_db_products), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required() 
    product_ids = [p[0] for p in db_carts.query(Cart.product_id).filter(Cart.user_id == email).all()]
    if not product_ids:
        return {"message": "your cart is empty!"}
    products = db_products.query(Product.name).filter(Product.id.in_(product_ids)).all()
    product_names = [p[0] for p in products]
    return {"cart products": product_names}


@fastapi.put('/removeproductfromcart/', tags=["cart"])
def remove_product(product: RemoveProductFromCart, email: str = Depends(user_email), db_carts: Session = Depends(get_db_carts), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required() 
    desired_product = db_carts.query(Cart).filter(Cart.product_id == product.product_id, Cart.user_id == email).first()
    if not desired_product:
        raise HTTPException(status_code=404, detail="product unavailable!")
    db_carts.delete(desired_product) 
    db_carts.commit()
    return {"message": "product removed from cart!"}
