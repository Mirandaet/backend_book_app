from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from sqlalchemy import select, update, delete, insert, func, desc
from app.db_setup import init_db, get_db
from app.database.models import User, Category, Book, SubCategory, BookShelf, Achievement, CompletedAchievement, Author, AuthorBook, BookVersion, YearlyPageCount
from app.database.schemas import NewPasswordSchema, UserSchema, CategorySchema, SubCategorySchema, BookSchema, BookShelfSchema, AchievementSchema, CompletedAchievementSchema, PasswordSchema, TokenSchema, TokenDataSchema, UserWithIDSchema
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from typing import Annotated, Optional
from dotenv import load_dotenv
import os
from difflib import SequenceMatcher
from app.email import generate_password_reset_token, send_password_reset_email, verify_password_reset_token


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


def order_search(search_term, search_list):
    sorted_dict = sorted(search_list, key=lambda x: SequenceMatcher(
        None, x.title, search_term).ratio(), reverse=True)
    return sorted_dict


def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.execute(statement).scalars().first()
    return session_user

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
        BookShelf.isFinished == False).options(selectinload(BookShelf.book_version).options(selectinload(BookVersion.book_cover)).options(selectinload(BookVersion.book).options(selectinload(Book.main_category)))).order_by(BookShelf.book_version_id)).all()
    return result


@app.post("/users/reading/{book_version_id}")
def add_to_read(
        current_user: Annotated[User, Depends(get_current_user)], book_version_id: int, db: Session = Depends(get_db)):
    today = datetime.today()
    check = db.scalars(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.book_version_id == book_version_id).where(BookShelf.isFinished == False)).first()
    if check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Server error, book version is already being read", headers={"WWW-Authenticate": "Bearer"})
    bookshelf = BookShelf(book_version_id=book_version_id, user_id=current_user.id,
                          pages_read=0, start_date=today, isFinished=False, paused=False)
    db.add(bookshelf)
    db.commit()
    db.refresh(bookshelf)
    return True


@app.delete("/users/reading/{book_version_id}")
def remove_from_read(
        current_user: Annotated[User, Depends(get_current_user)], book_version_id: int, db: Session = Depends(get_db)):
    check = db.scalars(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.book_version_id == book_version_id).where(BookShelf.isFinished == False)).first()
    if not check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Server error, book version is not being read", headers={"WWW-Authenticate": "Bearer"})
    db.execute(delete(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.book_version == book_version_id))
    db.commit()
    return True


@app.put("/users/reading/{book_version_id}/{new_book_version_id}")
def change_edition(
        current_user: Annotated[User, Depends(get_current_user)], book_version_id: int, new_book_version_id: int, db: Session = Depends(get_db)):
    book_shelf = db.execute(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.book_version_id == book_version_id)).scalar_one()
    if int(book_shelf.pages_read) >= int(book_shelf.book_version.page_count):
        book_shelf.pages_read = book_shelf.book_version.page_count
        book_shelf.isFinished = True
        book_shelf.finished_date = datetime.now()
    book_shelf.book_version_id = new_book_version_id
    db.commit()


@app.put("/book/pause/{book_version_id}")
def set_paused(
        current_user: Annotated[User, Depends(get_current_user)], book_version_id, db: Session = Depends(get_db)):
    book_shelf = db.scalars(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.book_version_id == book_version_id).where(BookShelf.isFinished == False)).first()
    if not book_shelf:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Server error, book version is not being read", headers={"WWW-Authenticate": "Bearer"})
    book_shelf.paused = True
    db.commit()


@app.put("/book/unpause/{book_version_id}")
def set_unpaused(
        current_user: Annotated[User, Depends(get_current_user)], book_version_id, db: Session = Depends(get_db)):
    book_shelf = db.scalars(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.book_version_id == book_version_id).where(BookShelf.isFinished == False)).first()
    if not book_shelf:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Server error, book version is not being read", headers={"WWW-Authenticate": "Bearer"})
    book_shelf.paused = False
    db.commit()


@app.get("/users/readbooks")
def list_read_books(
        current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    result = db.scalars(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.isFinished == True).options(selectinload(BookShelf.book_version).options(selectinload(BookVersion.book_cover)).options(selectinload(BookVersion.book).options(selectinload(Book.main_category), selectinload(Book.authors).options(selectinload(AuthorBook.author))))).order_by(BookShelf.finished_date)).all()
    return result


@app.post("/user", status_code=201)
def add_user(user: PasswordSchema, db: Session = Depends(get_db)) -> PasswordSchema:
    hashed_password = get_password_hash(user.password)
    new_user = User(user_name=user.user_name,
                    email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return PasswordSchema(user_name=new_user.user_name, email=new_user.email, password=hashed_password)


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


@app.get("/books/{searchterm}")
async def find_books(searchterm, db: Session = Depends(get_db)):
    result = db.scalars(select(Book).where(Book.title.icontains(searchterm)).options(selectinload(Book.authors).selectinload(
        AuthorBook.author)).options(selectinload(Book.versions).selectinload(BookVersion.book_cover))).all()
    sorted_result = order_search(search_list=result, search_term=searchterm)
    return sorted_result


@app.get("/books/id/{book_id}")
async def get_book(book_id: int,  db: Session = Depends(get_db)):
    book = db.scalars(select(Book).where(Book.id == book_id).options(selectinload(Book.versions).selectinload(BookVersion.book_cover)).options(selectinload(
        Book.authors).selectinload(AuthorBook.author)).options(selectinload(Book.main_category)).options(selectinload(Book.sub_categories).selectinload(SubCategory.category))).first()
    return book


@app.put("/users/reading/pages/{book_version_id}/{pages}")
async def update_pages(current_user: Annotated[User, Depends(get_current_user)], book_version_id, pages, db: Session = Depends(get_db)):
    reading_books = db.execute(select(BookShelf).where(BookShelf.user_id == current_user.id).where(
        BookShelf.book_version_id == book_version_id).options(selectinload(BookShelf.book_version))).scalar_one()
    if int(pages) > int(reading_books.book_version.page_count):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Server error, pages cannot be larger than page count", headers={"WWW-Authenticate": "Bearer"})
    if int(pages) == int(reading_books.book_version.page_count):
        reading_books.isFinished = True
        reading_books.finished_date = datetime.now()
    reading_books.pages_read = pages
    db.commit()


@app.put("/user/{user_name}/{book_goal}/{email}")
async def update_user(user_name: str, book_goal: int, email: str, current_user: UserWithIDSchema = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.execute(select(User).where(
        User.id == current_user.id)).scalar_one()

    if len(user_name) < 5 or len(user_name) > 320:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username must be between 5 and 320 characters", headers={"WWW-Authenticate": "Bearer"})
    user.user_name = user_name

    if not int(book_goal):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Book goal must be an integer", headers={"WWW-Authenticate": "Bearer"})
    elif book_goal < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Book goal cannot be smaller than 0", headers={"WWW-Authenticate": "Bearer"})
    elif book_goal > 5000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Book goal cannot be larger than 5000", headers={"WWW-Authenticate": "Bearer"})
    user.book_goal = book_goal

    # if email != user.email:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Changing email is not supported", headers={"WWW-Authenticate": "Bearer"})
    user.email = email

    db.commit()
    return user


@app.put("/user/password/{password}")
async def update_password(current_user: Annotated[User, Depends(get_current_user)], password, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(
        User.id == current_user.id)).scalar_one()
    if password == user.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This password has already been used", headers={"WWW-Authenticate": "Bearer"})
    elif len(password) < 5 or len(password) > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password has to be between 5 and 100 characters", headers={"WWW-Authenticate": "Bearer"})
    hashed_password = get_password_hash(password)
    user.password = hashed_password
    db.commit()
    return user


@app.get("/editions/popular/{book_id}")
async def popular_editions(book_id, db: Session = Depends(get_db)):
    editions = db.scalars(select(BookVersion, func.count(BookShelf.book_version_id).label("popular")).join(BookShelf, isouter=True).group_by(
        BookVersion).options(selectinload(BookVersion.book_cover)).where(BookVersion.book_id == book_id).order_by(desc("popular"))).all()
    return editions


@app.get("/user/{email}")
async def get_user_with_email(email: str, db: Session = Depends(get_db)):
    user = db.scalars(select(User).where(User.email == email)).first()
    return user


@app.get("/users/{user_name}")
async def get_user_with_user_name(user_name: str, db: Session = Depends(get_db)):
    user = db.scalars(select(User).where(User.user_name == user_name)).first()
    return user


@app.get("/book_goal")
async def get_users_book_goal(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    user = db.scalars(select(User).where(User.id == current_user.id)).first()
    return user.book_goal


@app.get("/pages-read", status_code=200)
def get_pages_read(current_user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    result = db.scalars(select(YearlyPageCount).where(YearlyPageCount.user_id == current_user.id)).all()
    return result


@app.post("/password-recovery/{email}")
def recover_password(email: str, db: Session = Depends(get_db)):
    """
    Password Recovery
    """
    user = get_user_by_email(session=db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    send_password_reset_email(email, password_reset_token)
    return {"message": "Email has been sent"}


@app.put("/reset-password/")
def reset_password(body: NewPasswordSchema, db: Session = Depends(get_db)):
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = get_user_by_email(session=db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    hashed_password = get_password_hash(password=body.new_password)
    user.password = hashed_password
    db.add(user)
    db.commit()
    return {"message": "password updated"}