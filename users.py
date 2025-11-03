from fastapi import FastAPI, HTTPException, Depends, Body, Request 
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship 
from pydantic import BaseModel
from auth_handler import sign_jwt
import bcrypt
from auth_bearer import JWTBearer, IsAdmin
fastapi = FastAPI()

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
    cart = relationship('Cart', back_populates='user')


Base.metadata.create_all(bind=engine_users)


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
def user_create(user: UserCreate, db: Session = Depends(get_db_users)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="user already exists")
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(email = user.email, username = user.username, password = hashed_pw.decode('utf-8'))
#we firstly encode the password given by the user in the create user, and store that encoded thing in a variable (hashed_pw), then when we come to add it to our db we decode it    
    db.add(new_user)
    db.commit()
    role1 = db.query(User.role).filter(User.email == user.email).first() 
    return sign_jwt(user_id=user.email, role=role1[0])


@fastapi.post('/signin/')
def user_login(user: UserLogin, db: Session = Depends(get_db_users)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="user not found!")
    passkey = db.query(User.password).filter(User.email == user.email).first()
    if bcrypt.checkpw(user.password.encode('utf-8'), db_user.password.encode('utf-8')):
#we now take the password entered by the user in the sign in process, then we use the checkpw function by bcrypt to see if the encoded version of the user password matches the encoded version of the password in our db        
        role1 = db.query(User.role).filter(User.email == user.email).scalar() 
        role1 = str(role1).strip() 
        return sign_jwt(user_id=user.email, role=role1)
#we return the encoded token to the user once he signs up or in, this token will be later used to access secured routes
    else:
        raise HTTPException(status_code=401, detail="incorrect password!")
    

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    price = Column(Integer)    
    cart = relationship('Cart', back_populates='product')


Base.metadata.create_all(bind=engine_products)


class ProductCreate(BaseModel):
    name:str
    description:str
    price:int


class ProductResponse(BaseModel):
    name:str
    description:str
    price:int


@fastapi.post('/addproduct/', dependencies=[Depends(IsAdmin())], tags=["products"])
def product_create(product: ProductCreate, db: Session = Depends(get_db_products)):
    if db.query(Product).filter(Product.name == product.name).first():
        raise HTTPException(status_code=404, detail="product already exists!")
    new_product = Product(name = product.name, description = product.description, price = product.price)
    db.add(new_product)
    db.commit()
    return {"product added!"}


@fastapi.get('/displayproducts/{Product.id}', dependencies=[Depends(JWTBearer())], response_model=ProductResponse, tags=["products"])
def display_products(product_id:int, db: Session = Depends(get_db_products)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="product already exists!")
    return product
#the post and get methods for the products are secured routes, i ll now make the post method only accessible by admin (dk how but will get it


class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey(User.email, ondelete='cascade'))
    product_id = Column(Integer, ForeignKey(Product.id, ondelete='cascade'))
    user = relationship('User', back_populates='cart')
    product = relationship('Product', back_populates='cart')


Base.metadata.create_all(bind=engine_carts)


class AddToCart(BaseModel):
    product_id:int


class GetCart(BaseModel):
    cart_id:int


@fastapi.post('/addtocart/', dependencies=[Depends(JWTBearer())], tags=["cart"])
def add_to_cart(product: AddToCart, db_carts: Session = Depends(get_db_carts), db_products: Session = Depends(get_db_products)):
    product_id1 = db_products.query(Product.id).filter(Product.id == product.product_id).scalar()
    if not product_id1:
        raise HTTPException(status_code=404, detail="product not found!")
    async def __call__(self, request: Request, product: AddToCart, db_carts: Session = Depends(get_db_carts), db_products: Session = Depends(get_db_products)):
        token = await super().__call__(request)
        payload = decode_jwt(token)
        email = payload.get('id')
        added_product = Cart(user_id = email, product_id = product_id1)
        db.add(added_product)
        db.commit()
        return {"product added to cart successfuly!"}


