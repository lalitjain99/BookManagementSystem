#all pydantic models

from typing import Optional
from pydantic import BaseModel 

class CreateBook(BaseModel):
    title:str
    author:str
    genre:Optional[str] = None
    year_published:Optional[int] = None
    summary:Optional[str] = None

class UpdateBook(BaseModel):
    title:Optional[str] = None
    author:Optional[str] = None
    genre:Optional[str] = None
    year_published:Optional[int] = None
    summary:Optional[str] = None

class CreateReview(BaseModel):
    book_id: int
    user_id: int
    review_text: str
    rating: int

class User(BaseModel):
    id: Optional[int] = None
    user_name: str
    email: Optional[str]
    password: str

class LoginRequest(BaseModel):
    user_name: str
    password: str
