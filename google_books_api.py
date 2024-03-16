import requests
import json
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from sqlalchemy import select, update, delete, insert, func
from sqlalchemy.exc import IntegrityError
from app.db_setup import init_db, get_db
from app.database.models import User, Category, Book, SubCategory, BookShelf, Achievement, CompletedAchievement, Author, BookCover, Publisher
from app.database.schemas import UserSchema, CategorySchema, SubCategorySchema, BookShelfSchema, AchievementSchema, CompletedAchievementSchema, PasswordSchema, TokenSchema, TokenDataSchema, UserWithIDSchema, BookSchema
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from webscrape import scrape

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = init_db()
    yield

load_dotenv(override=True)
db = get_db()
app = FastAPI(lifespan=lifespan)

from main import get_db

def fetch_google_books():
    db = next(get_db())  # Call the generator to get the database session
    index = 0
    search_term = "intitle:The+intitle:Moonstone"
    url = f"https://www.googleapis.com/books/v1/volumes"

    while True:
        book_info = {}
        params = {"q": search_term, "maxResults": 40, "startIndex": index}

        index += 40
        res = requests.get(url, params=params)
        
        response = res.json()
        print (index)
        
        try:
            items = response["items"]
        except:    
            print(res)
            print("closing")
            break

        for book in items:
            book_info["title"] = book["volumeInfo"]["title"]
            book_info["language"] = book["volumeInfo"]["language"]
            book_info["is_ebook"] = book["saleInfo"]["isEbook"]
            try:
                book_info["book_cover"] = book["volumeInfo"]["imageLinks"]["thumbnail"]
            except:
                print("cover_fail")
                book_info["book_cover"] = False
                continue
            try:
                book_info["page_count"] = book["volumeInfo"]["pageCount"]
            except:
                book_info["page_count"] = False
                print("page_count fail")
                continue
            try:
                book_info["publish_date"] = book["volumeInfo"]["publishedDate"]
            except KeyError:
                book_info["publish_date"] = False
                print("publish_date fail")
                continue
            try:
                book_info["authors"] = book["volumeInfo"]["authors"]
            except KeyError:
                book_info["authors"] = False
                print("authors fail")
                continue
            try:
                book_info["publisher"] = book["volumeInfo"]["publisher"]
            except KeyError:
                book_info["publisher"] = False
                print("publisher fails")
                continue
            try:
                book_info["description"] = book["volumeInfo"]["description"]
            except KeyError:
                book_info["description"] =False
                print("description fail")
                continue
            search_book_title(book=book_info, db=db)






def search_book_title(book: BookSchema, db):
    print("in search book title")
    author_keys = []

    for author in book["authors"]:
        print(author)
        result = db.execute(
            select(Author)
            .where(Author.name == author)
        ).scalars().all()
        if not result:
            try:
                author_dict = {"name": author}
                db_author = Author(**author_dict)
                add = db.execute(insert(Author).values(name=author))
                commit = db.commit()
                add = add.inserted_primary_key
                author_keys.append(add[0])
            except IntegrityError as e:
                raise HTTPException(status_code=400, detail="Database error")
        else:
            for authors in result:
                author_keys.append(authors.id)
                
    
    del book["authors"]
    url_key = None
    result = db.execute(
        select(BookCover)
        .where(BookCover.url == book["book_cover"])
    ).scalars().first()
    if not result:
        try:
            cover_dict = {"url": book["book_cover"]}
            db_cover = BookCover(**cover_dict)
            add = db.execute(insert(BookCover).values(url=book["book_cover"]))
            url_key = add.inserted_primary_key[0]
            commit = db.commit()
            print(add, commit)
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail="Database error")
    else:
        url_key = result.id

    del book["book_cover"]
    
    # print("keys: ", author_keys, url_key)

    publisher_key = None

    result = db.execute(
        select(Publisher)
        .where(Publisher.name == book["publisher"])
    ).scalars().first()
    if not result:
        try:
            publisher_dict = {"name": book["publisher"]}
            db_publisher = Publisher(**publisher_dict)
            add = db.execute(insert(Publisher).values(name=book["publisher"]))
            publisher_key = add.inserted_primary_key[0]
            commit = db.commit()
            print(add, commit)
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail="Database error")
    else:
        publisher_key = result.id

    
    del book["publisher"]

    book["book_cover_id"] = url_key
    book["publisher_id"] = publisher_key

    title= book["title"]
    title= title.replace(" ", "+")

    book_url = "https://openlibrary.org/search.json"
    book_params = {"q": title}


    res = requests.get(book_url, params=book_params)


    goodreads_id = res.json()["docs"][0]["id_goodreads"][0]

    genres = scrape(goodreads_id)
    
    for genre in genres:
        print(genre)

    result = db.execute(
        select(Book)
        .where(Book.title == book["title"])
    ).scalars().all()

    
    # print("book:", book)
    if not result:
        # try:
            db_book = Book(**book)
            db.add(db_book)
            db.commit()
        # except IntegrityError as e:
        #     raise HTTPException(status_code=400, detail="Database error")
    
    # print(result)



fetch_google_books()