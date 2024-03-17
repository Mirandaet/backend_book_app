from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from sqlalchemy import select, update, delete, insert, func
from app.db_setup import init_db, get_db
from app.database.models import User, Category, Book, SubCategory, BookShelf, Achievement, CompletedAchievement, Author, AuthorBook
from app.database.schemas import UserSchema, CategorySchema, SubCategorySchema, BookShelfSchema, AchievementSchema, CompletedAchievementSchema, PasswordSchema, TokenSchema, TokenDataSchema, UserWithIDSchema
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from jose import JWTError, jwt, ExpiredSignatureError
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
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
algorithm = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
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
        raise HTTPException(status_code=404, detail="User not found")
    user = result
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encode_jwt


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        print("user", username)
        if username is None:
            raise credential_exception
        token_data = TokenDataSchema(username=username)
    except ExpiredSignatureError:  # <---- this one
        raise HTTPException(status_code=403, detail="token has been expired")
    except JWTError:
        raise credential_exception
    user = search_email(db=db, email=token_data.username)
    if user is None:
        raise credential_exception
    return user


def search_email(email: str, db: Session = Depends(get_db)):
    result = db.scalars(
        select(User)
        .where(User.email == email)
    ).first()
    if not result:
        return HTTPException(status_code=404, detail="User not found")
    return UserWithIDSchema(user_name=result.user_name, email=result.email, book_goal=result.book_goal, id=result.id)

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


@app.get("/users/reading")
def list_reading_books(
        current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    result = db.scalars(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.isFinished == False).options(selectinload(BookShelf.book).options(selectinload(Book.main_category))).order_by(BookShelf.book_id)).all()
    return result


@app.get("/users/readbooks")
def list_read_books(
        current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    result = db.scalars(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.isFinished == True).options(selectinload(BookShelf.book).selectinload(Book.main_category)).options(selectinload(BookShelf.book).selectinload(Book.authors).selectinload(AuthorBook.author))).all()
    return result


@app.post("/user", status_code=201)
def add_user(user: PasswordSchema, db: Session = Depends(get_db)) -> PasswordSchema:
    hashed_password = get_password_hash(user.password)
    new_user = User(user_name=user.user_name, email=user.email, book_goal=user.book_goal, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return PasswordSchema(users_name=new_user.user_name, email=new_user.email, book_goal=new_user.book_goal, password=hashed_password)


@app.get("/categories", status_code=200)
def list_categories(db: Session = Depends(get_db)):
    query = select(Category)
    categories = db.scalars(query).all()
    return categories


@app.get("/users/completed_achievements", status_code=200)
def list_users_completed_achievements(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    result = db.scalars(select(CompletedAchievement).where(
        CompletedAchievement.user_id == current_user.id)).all()
    return result


@app.post("/token", response_model=TokenSchema)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = validate_user(form_data.username, form_data.password, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user/me", response_model=None)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@app.put("/users/reading/pages/{book_id}/{pages}")
async def update_pages(current_user: Annotated[User, Depends(get_current_user)], book_id, pages, db: Session = Depends(get_db)):
    reading_books = db.execute(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.book_id == book_id).options(selectinload(BookShelf.book))).scalar_one()
    if int(pages) > int(reading_books.book.page_count):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Server error, pages cannot be larger than page count", headers={"WWW-Authenticate": "Bearer"})
    reading_books.pages_read = pages
    db.commit()
