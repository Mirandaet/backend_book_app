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

    # relationships
    books: Mapped[list["BookShelf"]] = relationship(back_populates="user")
    achievements: Mapped[list["CompletedAchievement"]] = relationship(back_populates="users")


class Category(base):
    __tablename__= "categories"
    name: Mapped[str]
    color_code: Mapped[str]
    
    # relationships
    books: Mapped[list["Book"]] = relationship("Book", back_populates="categories")
    books_sub_categories: Mapped[list["SubCategory"]] = relationship(back_populates="category")



class Book(base):
    __tablename__= "books"
    title: Mapped[str]
    page_count: Mapped[int]
    is_ebook: Mapped[bool]

    #relationships
    main_category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    main_category: Mapped[Category] = relationship("Book", back_populates="books")
    sub_categories: Mapped[list["SubCategory"]] = relationship(back_populates="book")
    users: Mapped[list["BookShelf"]] = relationship(back_populates="book")


class SubCategory:
    __tablename__= "sub_categories"
    category_id: Mapped[int]
    book_id: Mapped[int]

    # realtionship
    category: Mapped["Category"] = relationship(back_pipulates="books")
    book: Mapped["Book"] = relationship(back_populates="categories")


class BookShelf:
    __tablename__= "book_shelves"
    pages_read: Mapped[int]
    is_read: Mapped[bool]

    # realtionships
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    user: Mapped["User"] = relationship(back_populates="books")
    book: Mapped["Book"] = relationship(back_populates="users")


class Achievement:
    __tablename__= "achievements"
    name: Mapped[str]

    #realtiosnhips
    users: Mapped[list["CompletedAchievement"]] = relationship(back_populates="achievement")


class CompletedAchievement:
    __tablename__= "completed_achievements"
    # relationships
    achievements_id: Mapped[int] = mapped_column(ForeignKey("achievements.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

