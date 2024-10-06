import asyncio
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
# from pydantic import BaseModel
import asyncpg
from models import BookSQL,ReviewSQL
import uvicorn
from request_response import CreateBook, CreateReview, UpdateBook

app = FastAPI()

#Database connection and session setup
# DATABASE_URL = "postgresql+asyncpg://postgres:admin@123@localhost/bookstore"
DATABASE_URL = "postgresql+asyncpg://postgres:admin%40123@localhost/bookstore"


async def test_connection():
    async with asyncpg.connect(DATABASE_URL) as conn:
        print("Connected to database successfully!")

# asyncio.run(test_connection())

engine = create_async_engine(DATABASE_URL,echo=True)
session_local = sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)


############################################  API's ############################################

#1. Add a new book --> done
@app.post("/books")
async def create_book(book: CreateBook):
    async with session_local() as session:
        new_book = BookSQL(
        title=book.title,
        author=book.author,
        genre=book.genre,
        year_published=book.year_published,
        summary=book.summary,
    )
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book
    
#2. Retrieve all books --done
@app.get("/books")
async def get_all_books():
    async with session_local() as session:
        result = await session.execute(select (BookSQL))
        books = result.scalar()
        return books 

    
#3. Retrieve a specific book by its ID --> done
@app.get("/books/{book_id}")
async def get_book_by_id(book_id:int):
    print(f"Received book_id: {book_id}")
    async with session_local() as session:
        result = await session.execute(select(BookSQL).where(BookSQL.id == book_id))
        book = result.scalars().all()  # Use scalars() for multiple results
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        elif len(book) > 1:
            # Handle case of multiple books with same ID (if applicable)
            # You can raise an error, return a list, or log a warning
            raise HTTPException(status_code=400, detail="Multiple books found with the same ID")
        return book[0]
     
#4. Update a book's information by its ID --> done
@app.put("/books/{book_id}") 
async def update_book(book_id:int, book_data:UpdateBook):
    async with session_local() as session:
        result = await session.execute(select(BookSQL).where(BookSQL.id == book_id))
        existing_book = result.scalar()
        print(existing_book)
        if existing_book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        
        for key,value in book_data.model_dump().items():
            if hasattr(existing_book,key):
                setattr(existing_book,key,value)
            else:
                # Handle potential error if an invalid key is provided
                raise HTTPException(status_code=400, detail=f"Invalid update field: {key}")
        
        await session.commit()
        await session.refresh(existing_book)
        return existing_book
    
#5. Delete a book by its ID --> done
@app.delete("/books/{id}")
async def delete_book(book_id:int):
    async with session_local() as session:
        result = await session.execute(select (BookSQL).where(BookSQL.id == book_id))
        book = result.scalar()
        print(book)
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        await session.delete(book)
        await session.commit()
        return {"message": "Book deleted successfully"}

#6a. Add a review for a book
@app.post("/books/{book_id:int}/review")
async def create_review(book_id: int, review: CreateReview):
    async with session_local() as session:
        result = await session.execute(select(BookSQL).where(BookSQL.id == book_id))
        book = result.scalar()
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        new_review = ReviewSQL(
            book_id=review.book_id,  # Use data from the Pydantic model
            user_id=review.user_id,
            review_text=review.review_text,
            rating=review.rating
        )
        session.add(new_review)
        await session.commit()
        await session.refresh(new_review)

        return new_review
    
#6b Add a review for a book via book title??
    
#7. Retrieve all reviews for a book
@app.get("/books/{book_id:int}/reviews")
async def get_all_reviews(book_id:int):
    async with session_local() as session:
        query = select(ReviewSQL).where(ReviewSQL.book_id == book_id)
        # query = select(ReviewSQL) \
        #     .join(BookSQL, ReviewSQL.book_id == BookSQL.id) \
        #     .where(BookSQL.id == book_id)
        print("Executing query:", query)
        result = await session.execute(query)
        print(result)
        reviews = result.scalar()
        if reviews is None:
            raise HTTPException(status_code=404, detail="Reviews for this book not found")
        return reviews
    
#8. Get a summary and aggregated rating for a book
@app.get("/books/{book_id}/summary")
async def get_summary_by_book_id(book_id: int):
    async with session_local() as session:
        result = await session.execute(select(BookSQL).where(BookSQL.id ==  book_id))
        book = result.scalar()
        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        
        review_result = await session.execute(select(func.avg(ReviewSQL.rating)).where(ReviewSQL.book_id == book_id))
        avg_rating = review_result.scalar()
        return {"summary": book.summary,"Average_rating": avg_rating}
    
if __name__ == "__main__":
    # asyncio.run(test_connection())
    uvicorn.run(app,host="127.0.0.1",port=8000)
