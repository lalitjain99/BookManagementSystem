from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel 

app = FastAPI()

#Database connection and session setup
DATABASE_URL = "postgresql+asyncpg://postgres:admin@123@localhost/bookstore"
engine = create_async_engine(DATABASE_URL,echo=True)
session_local = sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

#Base class
sqlalchemy_base = declarative_base()


class BookSQL(sqlalchemy_base):
    __tablename__ = "books"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,index = True)
    author = Column(String,index=True)
    genre = Column(String,index=True)
    year_published = Column(Integer)
    summary = Column(String)

class Book(BaseModel):
    id:int
    title:str
    author:str
    genre:str
    year_published:int
    summary:str

class ReviewSQL(sqlalchemy_base):
    __tablename__ = 'reviews'
    id = Column(Integer,primary_key=True,index=True)
    book_id = Column(Integer,ForeignKey("books.id"),index=True)
    user_id = Column(Integer,index=True)
    review_text = Column(String)
    rating = Column(Integer)

class Review(BaseModel):
    book_id: int
    user_id: int
    review_text: str
    rating: int