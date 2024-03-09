from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from sqlalchemy import select, update, delete, insert, func
from app.db_setup import init_db, get_db
from app.database.models import User, Category, Book, SubCategory, BookShelf, Achievement, CompletedAchievement
from app.database.schemas import UserSchema, CategorySchema, SubCategorySchema, BookShelfSchema, AchievementSchema, CompletedAchievementSchema, PasswordSchema, TokenSchema, TokenDataSchema
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Annotated, Optional
from dotenv import load_dotenv
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db() 
    yield

load_dotenv(override=True)
app = FastAPI(lifespan=lifespan)


# Token Authentication
secret_key = os.getenv("SECRET_KEY")
access_token_expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
algorithm = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def validate_user(email: str, password: str, db: Session = Depends(get_db)):
    result = db.scalars(
        select(User)
        .where(User.email == email)
    ).first()
    if not result:
        return HTTPException(status_code=404, detail="User not found")
    user = UserSchema(**result)
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.endoce(to_encode, secret_key, algorithm=algorithm)
    return encode_jwt

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenDataSchema(username=username)
    except JWTError:
        raise credential_exception
    user = search_email(db, username=token_data.username)
    if user is None:
        raise credential_exception
    return user

# async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# Middleware
origin = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Endpoints
@app.get("/users/count")
def list_users(db: Session = Depends(get_db)):
    count = db.scalars(
    select(func.count()).select_from(User))
    return count


@app.get("/users/email/{email}")
def search_email(email: str, db: Session = Depends(get_db)):
    result = db.scalars(
        select(User)
        .where(User.email == email).options(selectinload(User.email, User.user_name, User.book_goal))
    ).first()
    if not result:
        return HTTPException(status_code=404, detail="User not found")
    return UserSchema(**result)


@app.get("/users/{id}")
def user_detail(id: int, db: Session = Depends(get_db)):
    result = db.scalars(
        select(User)
        .where(User.id == id)
        .options(load_only(User.user_name, User.email, User.book_goal))
    ).first()
    if not result:
        return HTTPException(status_code=404, detail="User not found")
    return result


@app.get("/users/{id}/reading")
def list_reading_books(id: int, db: Session = Depends(get_db)):
    result = db.scalars(select(BookShelf).where(BookShelf.user_id == id).where(BookShelf.finished_date != None)).all()
    return result


@app.get("/categories", status_code=200)
def list_categories(db: Session = Depends(get_db)):
    query = select(Category)
    categories = db.scalars(query).all()
    return categories   


@app.get("/users/{id}/completed_achievements", status_code=200)
def list_users_completed_achievements(id: int, db: Session = Depends(get_db)):
    result = db.scalars(select(CompletedAchievement).where(CompletedAchievement.user_id == id)).all()
    return result


@app.post("/token", response_model=TokenSchema)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = validate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}