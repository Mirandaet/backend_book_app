from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, Column, Table, DateTime, func
from datetime import datetime

class base(DeclarativeBase):
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
class User(base):
    email: Mapped[str]
    password: Mapped[str]
    user_name: Mapped[str]
    book_goal: Mapped[int]

class Books(base):
    title: Mapped[str]
    page_count: Mapped[int]

class Types(base):
    type_name: Mapped[str]

