from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, crete_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey
from pydantic import BaseModel 

app = FastAPI()

#Database connection and session setup
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
engine = crete_async_engine(DATABASE_URL,echo=True)
session_local = sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

#Base class
sqlalchmy_base = declarative_base()


class Book(sqlalchmy_base):
    __tablename__ = "books"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,index = True)
    author = Column(String,index=True)
    genre = Column(String,index=True)
    year_published = Column(Integer)
    summary = Column(String)

class Review(sqlalchmy_base):
    __tablename__ = 'reviews'
    id = Column(Integer,primary_key=True,index=True)
    book_id = Column(Integer,ForeignKey("books.id"),index=True)
    user_id = Column(Integer,index=True)
    review_text = Column(String)
    rating = Column(Integer)