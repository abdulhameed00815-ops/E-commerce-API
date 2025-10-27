from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

fastapi = FastAPI()

engine = create_engine("postgresql://postgres:1234@localhost/products")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
session = SessionLocal()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    price = Column(Integer)    


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProductCreate(BaseModel):
    name:str
    description:str
    price:int


class ProductResponse(BaseModel):
    name:str
    description:str
    price:int

@fastapi.post('/addproduct/')
def product_create(product: ProductCreate, db: Session = Depends(get_db)):
    if db.query(Product).filter(Product.name == product.name).first():
        raise HTTPException(status_code=404, detail="product already exists!")
    new_product = Product(name = product.name, description = product.description, price = product.price)
    db.add(new_product)
    db.commit()
    return {"product added!"}


@fastapi.get('/displayproducts/{Product.id}', response_model=ProductResponse)
def display_products(product_id:int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="product already exists!")
    return product
