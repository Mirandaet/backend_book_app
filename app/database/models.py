from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, Column, Table, DateTime, func
from datetime import datetime

class base(DeclarativeBase):
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
class User(base):
    __tablename__= "users"
    email: Mapped[str]
    password: Mapped[str]
    user_name: Mapped[str]
    book_goal: Mapped[int]

class Category(base):
    __tablename__= "categories"
    name: Mapped[str]
    color_code: Mapped[str]

class Book(base):
    __tablename__= "books"
    title: Mapped[str]
    page_count: Mapped[int]
    is_ebook: Mapped[bool]
    main_category: [int]

    #relationships
    

class SubCategory:
    __tablename__= "sub_categories"
    category_id: Mapped[int]
    book_id: Mapped[int]

class BooksShelf:
    __tablename__= "book_shelves"
    user_id: Mapped[int]
    book_id: Mapped[int]
    pages_read: Mapped[int]
    is_read: Mapped[bool]

class Achievement:
    __tablename__= "achievements"
    name: Mapped[str]

class CompletedAchievement:
    __tablename__= "completed_achievements"
    achievements_id: Mapped[int]
    user_id: Mapped[int]


