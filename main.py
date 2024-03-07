from fastapi import FastAPI, HTTPException, Depends, status
from app.db_setup import init_db, get_db
from contextlib import asynccontextmanager
from fastapi import Request
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from sqlalchemy import select, update, delete, insert, func
from app.database.models import User, Category, Book, SubCategory, BookShelf, Achievement, CompletedAchievement
from app.database.schemas import UserSchema, CategorySchema, SubCategorySchema, BookShelfSchema, AchievementSchema, CompletedAchievementSchema
from fastapi.middleware.cors import CORSMiddleware



# Funktion som körs när vi startar FastAPI - 
# perfekt ställe att skapa en uppkoppling till en databas
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db() # Vi ska skapa denna funktion
    yield

app = FastAPI(lifespan=lifespan)

origin = [
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/users/count")
def list_users(db: Session = Depends(get_db)):
    count = db.scalars(
    select(func.count()).select_from(User))
    return count


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
def list_reading_books(id, db: Session = Depends(get_db)):
    result = db.scalars(select(BookShelf).where(BookShelf.user_id == id).where(BookShelf.finished_date != None)).all()
    return result


@app.get("/categories", status_code=200)
def list_categories(db: Session = Depends(get_db)):
    query = select(Category)
    categories = db.scalars(query).all()
    return categories   


@app.get("/users/{id}/completed_achievements", status_code=200)
def list_users_completed_achievements(id, db: Session = Depends(get_db)):
    result = db.scalars(select(CompletedAchievement).where(CompletedAchievement.user_id == id)).all()
    return result