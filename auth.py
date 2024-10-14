from fastapi import HTTPException,Depends
import secrets
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from request_response import User
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:admin%40123@localhost/bookstore"
# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create the session factory
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
# def get_db():
#     engine = create_async_engine(DATABASE_URL,echo=True)
#     db = sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
#     try:
#         yield db
#     finally:
#         db.close()
secret_key = secrets.token_urlsafe(32)
#JWT Token Generation
def generate_access_token(user: User):
    print(user)
    expire_time = datetime.now() + timedelta(minutes=30)
    to_encode = {
        "exp": expire_time,
        "sub": str(user['id']),
    }
    
    print("Secret_key in login",secret_key)
    print(f"Payload to encode: {to_encode}")
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    print(f"Encoded JWT: {encoded_jwt}")
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = secret_key
ALGORITHM = "HS256"
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        print(f"encoded token received {token}")
        print(f"Secret key in verification {SECRET_KEY}")
        print(ALGORITHM)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        user_name: str = payload.get("sub")
        if user_name is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials due to User",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_name
    except Exception as e:
        print(e)
    
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_by_id(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secrets.token_urlsafe(32),
                                algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = await get_user_by_id(user_id)  # Replace with your user retrieval function
        return user
    except JWTError:
        raise credentials_exception