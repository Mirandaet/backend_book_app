from fastapi import FastAPI, HTTPException, Depends, status
from app.db_setup import init_db, get_db
from contextlib import asynccontextmanager
from fastapi import Request
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, update, delete, insert
from app.database.models import User, Category, Book, SubCategory, BookShelf, Achievement, CompletedAchievement
from app.database.schemas import UserSchema, CategorySchema, SubCategorySchema, BookShelfSchema, AchievementSchema, CompletedAchievementSchema


# Funktion som körs när vi startar FastAPI - 
# perfekt ställe att skapa en uppkoppling till en databas
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db() # Vi ska skapa denna funktion
    yield

app = FastAPI(lifespan=lifespan)