from fastapi import APIRouter, HTTPException, Depends
from requests import Session
from sqlalchemy.ext.asyncio import AsyncSession
from request_response import LoginRequest,User
from auth import generate_access_token, get_db
from models import UserSQL
from sqlalchemy.future import select

login_router = APIRouter()


@login_router.post("/login")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # user = db.query(User).filter(User.username == login_data.username).first()
    stmt = select(UserSQL).where(UserSQL.user_name == login_data.user_name and UserSQL.password == login_data.password)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    # if not user or not UserSQL.verify_password(login_data.password, user.password):
    #     raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token  = generate_access_token(user={"username": user.user_name,"id":user.id})
    return {"access_token": access_token}