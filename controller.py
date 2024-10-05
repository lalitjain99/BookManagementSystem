import asyncio
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
# from sqlalchemy import Column, Integer, String, ForeignKey
# from pydantic import BaseModel
from models import Book, Review,BookSQL,ReviewSQL
import uvicorn

app = FastAPI()

#Database connection and session setup
# DATABASE_URL = "postgresql+asyncpg://postgres:admin@123@localhost/bookstore"
DATABASE_URL = "postgresql+asyncpg://postgres:admin%40123@localhost/bookstore"
import asyncpg

async def test_connection():
    async with asyncpg.connect(DATABASE_URL) as conn:
        print("Connected to database successfully!")

# asyncio.run(test_connection())

engine = create_async_engine(DATABASE_URL,echo=True)
session_local = sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)


#Sqlalchemy class for storing Books
# class Book(Base):
#     __tablename__ = "books"
#     id = Column(Integer,primary_key=True,index=True)
#     title = Column(String,index = True)
#     author = Column(String,index=True)
#     genre = Column(String,index=True)
#     year_published = Column(Integer)
#     summary = Column(String)

#Pydantic class for Books table
# class BookCreate(BaseModel):
#     title:str
#     author:str
#     genre:str
#     year_published:int
#     summary:str

# class BookUpdate(BaseModel):
#     title:str
#     author:str
#     genre:str
#     year_published:int
#     summary:str

# class Review(Base):
#     __tablename__ = 'reviews'
#     id = Column(Integer,primary_key=True,index=True)
#     book_id = Column(Integer,ForeignKey("books.id"),index=True)
#     user_id = Column(Integer,index=True)
#     review_text = Column(String)
#     rating = Column(Integer)

#Pydantic Class for Review table
# class CreateReview(BaseModel):
#     book_id: int
#     user_id: int
#     review_text: str
#     rating: int

############################################  API's ############################################

#1. Add a new book
@app.post("/books")
async def create_book(book: Book):
    async with session_local() as session:
        print(**book.model_dump())
        new_book = Book.Book(**book.model_dump())
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book
    
#2. Retrieve all books
@app.get("/books")
async def get_all_books():
    async with session_local() as session:
        result = await session.execute(select (BookSQL))
        books = result.scalar()
        print(books)
        return books 
        # books = []
        # for row in result:
        #     book = BookSQL(**row)  # Use unpacking to create Book objects
        #     books.append(book)
        # return books
    
#3. Retrieve a specific book by its ID
@app.get("/books/{id}")
async def get_book_by_id(book_id:int):
    async with session_local() as session:
        result = await session.execute(select (Book).where(Book.id == book_id))
        #need to add validation for multiple result
        book = result.scalar().first()
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        return book
        
#4. Update a book's information by its ID
@app.put("/books/{id}")
async def update_book(book_id:int, book:Book):
    async with session_local() as session:
        result = await session.execute(select (Book).where(Book.id == book_id))
        existing_book = result.scalar().first()
        if existing_book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        
        for key,value in book.model_dump().items():
            setattr(existing_book,key,value)
        
        await session.commit()
        await session.refresh(existing_book)

        return existing_book
    
#5. Delete a book by its ID
@app.delete("/books/{id}")
async def delete_book(book_id:int):
    async with session_local() as session:
        result = await session.execute(select (Book).where(Book.id == book_id))
        book = result.scalar().first()
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        await session.delete(book)
        await session.commit()
        return {"message": "Book deleted successfully"}

#6a. Add a review for a book
@app.post("/books/{id}/review")
async def create_review(book_id:int, review:Review):
    async with session_local() as session:
        result = await session.execute(select (Book).where(Book.id == book_id))
        book = result.scalar().first()
        if book is None:
            raise HTTPException(status_code=404,detail="Book not found")
        new_review = review.model_dump()
        await session.add(new_review)
        await session.commit()
        await session.refresh(new_review)

        return new_review
    
#6b Add a review for a book via book title??
    
#7. Retrieve all reviews for a book
@app.get("books/{id}/reviews")
async def get_all_reviews(book_id:int):
    async with session_local() as session:
        result = await session.execute(select(Review).where(Review.book_id == book_id))
        reviews = result.scalar().all()
        if reviews is None:
            raise HTTPException(status_code=404, detail="Reviews for this book not found")
        return reviews
    
#8. Get a summary and aggregated rating for a book
@app.get("books/{id}/summary")
async def get_summary_by_book_id(book_id: int):
    async with session_local() as session:
        result = await session.execute(select(Book).where(Book.id ==  book_id))
        book = result.scalar().first()
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        
        review_result = await session.execute(select(function.avg(Review.rating)).where(Review.book_id == book_id))
        avg_rating = review_result.scalar()
        return {"summary": book.summary,"Average_rating": avg_rating}
    
if __name__ == "__main__":
    # asyncio.run(test_connection())
    uvicorn.run(app,host="127.0.0.1",port=8000)
