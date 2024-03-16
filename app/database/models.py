from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, Column, Table, DateTime, func, UniqueConstraint
from datetime import datetime


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)


class User(Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    user_name: Mapped[str] = mapped_column(nullable=True, unique=True)
    book_goal: Mapped[int] = mapped_column(nullable=True)

    # relationships
    books: Mapped[list["BookShelf"]] = relationship(back_populates="user")
    achievements: Mapped[list["CompletedAchievement"]
                         ] = relationship(back_populates="user")
    yearly_page_counts: Mapped[list["YearlyPageCount"]] = relationship(
        "YearlyPageCount", back_populates="user")


class Category(Base):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(unique=True)
    color_code: Mapped[str]

    # relationships
    books: Mapped[list["Book"]] = relationship(
        "Book", back_populates="main_category")
    books_sub_categories: Mapped[list["SubCategory"]] = relationship(
        "SubCategory", back_populates="category")


class Book(Base):
    __tablename__ = "books"
    title: Mapped[str]
    page_count: Mapped[int]
    is_ebook: Mapped[bool]
    publish_date = Mapped[datetime]
    description = Mapped[str]
    language = Mapped[str]

    # relationships
    main_category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    main_category: Mapped["Category"] = relationship(back_populates="books")
    sub_categories: Mapped[list["SubCategory"]
                           ] = relationship(back_populates="book")
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id"))
    publisher: Mapped["Publisher"] = relationship(back_populates="books")
    users: Mapped[list["BookShelf"]] = relationship(back_populates="book")
    authors: Mapped[list["AuthorBook"]] = relationship(back_populates="book")
    book_cover_id: Mapped[int] = mapped_column(ForeignKey("book_covers.id"))
    book_covers: Mapped[list["BookCover"]
                        ] = relationship(back_populates="book")


class YearlyPageCount(Base):
    __tablename__ = "yearly_page_counts"
    january: Mapped[int] = mapped_column(default=0)
    february: Mapped[int] = mapped_column(default=0)
    march: Mapped[int] = mapped_column(default=0)
    april: Mapped[int] = mapped_column(default=0)
    may: Mapped[int] = mapped_column(default=0)
    june: Mapped[int] = mapped_column(default=0)
    july: Mapped[int] = mapped_column(default=0)
    august: Mapped[int] = mapped_column(default=0)
    september: Mapped[int] = mapped_column(default=0)
    october: Mapped[int] = mapped_column(default=0)
    november: Mapped[int] = mapped_column(default=0)
    december: Mapped[int] = mapped_column(default=0)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="yearly_page_counts")


class BookCover(Base):
    __tablename__ = "book_covers"
    url: Mapped[str]
    book: Mapped["Book"] = relationship(back_populates="book_covers")


class AuthorBook(Base):
    __tablename__ = "author_books"
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))

    # Realtionship
    author: Mapped["Author"] = relationship(back_populates="books")
    book: Mapped["Book"] = relationship(back_populates="authors")

    __table_args__ = (
        UniqueConstraint("book_id", "author_id"),
    )


class Author(Base):
    __tablename__ = "authors"
    name: Mapped[str]
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=True)

    # Realtionship
    books: Mapped[list["AuthorBook"]] = relationship(back_populates="author")


class SubCategory(Base):
    __tablename__ = "sub_categories"
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))

    # relationships
    category: Mapped[Category] = relationship(
        back_populates="books_sub_categories")
    book: Mapped[Book] = relationship("Book", back_populates="sub_categories")

    __table_args__ = (
        UniqueConstraint("category_id", "book_id"),
    )


class BookShelf(Base):
    __tablename__ = "book_shelves"
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
    __tablename__ = "achievements"
    name: Mapped[str]

    # realtiosnhips
    users: Mapped[list["CompletedAchievement"]] = relationship(
        back_populates="achievement")


class CompletedAchievement(Base):
    __tablename__ = "completed_achievements"
    # relationships
    achievements_id: Mapped[int] = mapped_column(ForeignKey("achievements.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(back_populates="users")

    __table_args__ = (
        UniqueConstraint("user_id", "achievements_id"),
    )

class Publisher(Base):
    __tablename__ = "publishers"
    name: Mapped[str]

    #relationship
    books: Mapped[list["Book"]] = relationship(
        "Book", back_populates="publisher")
