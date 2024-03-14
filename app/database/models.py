from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, Column, Table, DateTime, func, UniqueConstraint 
from datetime import datetime

class Base(DeclarativeBase):
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class User(Base):
    __tablename__= "users"
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    user_name: Mapped[str] = mapped_column(nullable=True, unique=True)
    book_goal: Mapped[int] = mapped_column(nullable=True)

    # relationships
    books: Mapped[list["BookShelf"]] = relationship(back_populates="user")
    achievements: Mapped[list["CompletedAchievement"]] = relationship(back_populates="user")


class Category(Base):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(unique=True)
    color_code: Mapped[str]

    # relationships
    books: Mapped[list["Book"]] = relationship("Book", back_populates="main_category")
    books_sub_categories: Mapped[list["SubCategory"]] = relationship("SubCategory", back_populates="category")


class Book(Base):
    __tablename__= "books"
    title: Mapped[str]
    page_count: Mapped[int]
    is_ebook: Mapped[bool]

    #relationships
    main_category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    main_category: Mapped[Category] = relationship(back_populates="books")
    sub_categories: Mapped[list["SubCategory"]] = relationship(back_populates="book")
    users: Mapped[list["BookShelf"]] = relationship(back_populates="book")


class SubCategory(Base):
    __tablename__ = "sub_categories"
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))

    # relationships
    category: Mapped[Category] = relationship(back_populates="books_sub_categories")
    book: Mapped[Book] = relationship("Book", back_populates="sub_categories")

    __table_args__ = (
        UniqueConstraint("category_id", "book_id"),
    )


class BookShelf(Base):
    __tablename__= "book_shelves"
    pages_read: Mapped[int]
    start_date: Mapped[datetime] = mapped_column(nullable=True)
    finished_date: Mapped[datetime] = mapped_column(nullable=True)
    isFinished: Mapped[bool] = mapped_column(default=False)

    # realtionships
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    user: Mapped["User"] = relationship(back_populates="books")
    book: Mapped["Book"] = relationship(back_populates="users")


class Achievement(Base):
    __tablename__= "achievements"
    name: Mapped[str]

    #realtiosnhips
    users: Mapped[list["CompletedAchievement"]] = relationship(back_populates="achievement")


class CompletedAchievement(Base):
    __tablename__= "completed_achievements"
    # relationships
    achievements_id: Mapped[int] = mapped_column(ForeignKey("achievements.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(back_populates="users")

    __table_args__ = (
        UniqueConstraint("user_id", "achievements_id"),
    )