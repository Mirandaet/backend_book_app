import requests
import json
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload, selectinload, load_only
from sqlalchemy import select, update, delete, insert, func
from sqlalchemy.exc import IntegrityError
from app.db_setup import init_db, get_db
from app.database.models import User, Category, Book, SubCategory, BookShelf, Achievement, CompletedAchievement, Author, BookCover, Publisher, AuthorBook, BookVersion
from app.database.schemas import UserSchema, CategorySchema, SubCategorySchema, BookShelfSchema, AchievementSchema, CompletedAchievementSchema, PasswordSchema, TokenSchema, TokenDataSchema, UserWithIDSchema, BookSchema, BookVersionSchema
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from webscrape import scrape
import logging
from urllib.error import HTTPError
import string



@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

load_dotenv(override=True)
db = get_db()
app = FastAPI(lifespan=lifespan)

from main import get_db

def fetch_google_books(search_term, spare_goodreads = None):
    logging.debug("start of fetch_google_books")
    db = next(get_db())  # Call the generator to get the database session
    index = 0
    logging.debug(f"Search term = {search_term}")

    url = f"https://www.googleapis.com/books/v1/volumes"

    while True:
        logging.debug(f"Inside google_books_api loop, index: {index}")
        book_info = {}
        book_version_info = {}
        params = {"q": search_term, "maxResults": 40, "startIndex": index}

        index += 40
        res = requests.get(url, params=params)
        
        response = res.json()
        try:
            items = response["items"]
        except KeyError:
            logging.debug(f"End of google_books_api loop, response: {res}") 
            break

        for book in items:
            try:
                book_info["title"] = book["volumeInfo"]["title"]
            except KeyError:
                logging.debug("title fail")
                continue            
            logging.debug(f"Book title {book_info["title"]}")
            try:
                book_info["authors"] = book["volumeInfo"]["authors"]
            except KeyError:
                book_info["authors"] = False
                logging.debug("authors fail")
                continue
            try:
                book_version_info["language"] = book["volumeInfo"]["language"]
            except KeyError:
                logging.debug("Language fail")
                continue            
            try:
                book_version_info["is_ebook"] = book["saleInfo"]["isEbook"]
            except KeyError:
                logging.debug("ebook fail")
                continue
            try:
                book_version_info["book_cover"] = book["volumeInfo"]["imageLinks"]["thumbnail"]
            except KeyError:
                logging.debug("book_cover fail")
                continue
            try:
                book_version_info["page_count"] = book["volumeInfo"]["pageCount"]
                if book_version_info["page_count"] <= 0:
                    logging.debug("page_count fail, pages 0 or fewer")
                    continue
            except KeyError:
                logging.debug("page_count fail, no page_count value")
                continue
            try:
                book_version_info["publisher"] = book["volumeInfo"]["publisher"]
            except KeyError:
                logging.debug("publisher fails")
                continue
            try:
                book_version_info["description"] = book["volumeInfo"]["description"]
            except KeyError:
                logging.debug("description fail")
                continue
            search_book_title(book=book_info, book_version = book_version_info, spare_goodreads=spare_goodreads, db=db)

            logging.debug("End of google_books loop")





def search_book_title(book: BookSchema, book_version: BookVersionSchema, spare_goodreads, db):
    logging.debug(f"start of search_book_title, searching for {book["title"]}")
    result = None
    book_key = None
    found_book = False  

    book["main_category_id"] = genre_keys[0]
    book["title"] = string.capwords(book["title"])
  

    result = db.execute(
        select(Book)
        .where(Book.title == book["title"])
    ).scalars().first()

    if not result:
        found_book = True
        book_key = result.id

        author_keys = author_search(book=book, db=db)
        genre_keys = search_genres(book=book, spare_goodreads=spare_goodreads, db=db)
        
        try:
            logging.debug(f"adding book {book["title"]} to database")
            db_book = Book(**book)  
            add = db.execute(insert(Book).values(**book))
            add = add.inserted_primary_key
            book_key = add.id
            db.commit()
            logging.debug(f"{book["title"]} added to database")
        except IntegrityError as e:
            logging.info(f"Error occured when adding book {book["title"]} to database, error: {e}")
            db.commit()

        del genre_keys[0]
                                
    
    del book["authors"]
    url_key = None
    result = db.execute(
        select(BookCover)
        .where(BookCover.url == book_version["book_cover"])
    ).scalars().first()
    if not result:
        try:
            logging.debug(f"Book cover { book_version["book_cover"]} does not exsist, adding cover to database")
            cover_dict = {"url": book_version["book_cover"]}
            db_cover = BookCover(**cover_dict)
            add = db.execute(insert(BookCover).values(url=book_version["book_cover"]))
            url_key = add.inserted_primary_key[0]
            commit = db.commit()
            print(add, commit)
        except IntegrityError as e:
            logging.info(f"Database Error occured when adding book cover { book_version["book_cover"]}, error: {e}, raising database error")
            raise HTTPException(status_code=400, detail="Database error") from e
    else:
        logging.debug(f"Book cover { book_version["book_cover"]} already exsists")
        url_key = result.id

    del book_version["book_cover"]
    
    publisher_key = None

    result = db.execute(
        select(Publisher)
        .where(Publisher.name == book_version["publisher"])
    ).scalars().first()
    if not result:
        try:
            logging.debug(f"Publisher {book_version["publisher"]} does not exsist, adding publisher to database")
            publisher_dict = {"name": book_version["publisher"]}
            db_publisher = Publisher(**publisher_dict)
            add = db.execute(insert(Publisher).values(name=book_version["publisher"]))
            publisher_key = add.inserted_primary_key[0]
            commit = db.commit()
            print(add, commit)
        except IntegrityError as e:
            logging.info(f"Database Error occured when adding publisher {book_version["publisher"]}, error: {e}, raising database error")
            raise HTTPException(status_code=400, detail="Database error") from e
    else:
        logging.debug(f"Publisher {book_version["publisher"]} already exsists") 
        publisher_key = result.id

    
    del book_version["publisher"]

    book_version["book_cover_id"] = url_key
    book_version["publisher_id"] = publisher_key


    if not found_book:
        try:
            logging.debug(f"adding book {book["title"]} to database")
            db_book = Book(**book)  
            add = db.execute(insert(Book).values(**book))
            add = add.inserted_primary_key
            book_key = add.id
            db.commit()
            logging.debug(f"{book["title"]} added to database")
        except IntegrityError as e:
            logging.info(f"Error occured when adding book {book["title"]} to database, error: {e}")
            db.commit()

    if book_key:
        if found_book == False:
            for author_key in author_keys:
                try:
                    logging.debug(f"adding AuthorBook-relationship to database")
                    add = db.execute(insert(AuthorBook).values(book_id=book_key, author_id=author_key))
                    db.commit()
                    logging.debug(f"AuthorBook-relationship added to database")
                except IntegrityError as e:
                    logging.info(f"Error occured when adding book AuthorBook-relationship to database, error: {e}")
                    db.commit()
            
            for genre_key in genre_keys:
                try:
                    logging.debug(f"adding subcategory to database")
                    add = db.execute(insert(SubCategory).values(book_id=book_key, category_id=genre_key))
                    db.commit()
                    logging.debug(f"subcategory added to database")
                except IntegrityError as e:
                    logging.info(f"Error occured when adding book subcategory to database, error: {e}")
                    db.commit()
        try:
            book_version["book_id"] = book_key
            logging.debug(f"adding book book version to database")
            db.execute(insert(BookVersion).values(**book_version))
            db.commit()
            logging.debug(f"Book version added to database")
        except IntegrityError as e:
            logging.info(f"Error occured when adding book book version to database, error: {e}")
            db.commit()

    logging.debug("End of search_title")


def author_search(book, db):
    author_keys = []


    for author in book["authors"]:
        author = author.replace(".", "")
        author = string.capwords(author)
        try:
            result = db.scalars(select(Author).where(Author.name == author)).first()
            commit = db.commit()
        except Exception as e:
            logging.warning(f"Could not fetch authors, error: {e}")
            db.commit()
        if not result:
            try:
                logging.debug(f"Author {author} does not exsist, adding author to database")
                author_dict = {"name": author}
                db_author = Author(**author_dict)
                add = db.execute(insert(Author).values(name=author))
                commit = db.commit()
                add = add.inserted_primary_key
                author_keys.append(add[0])
            except IntegrityError as e:
                logging.info(f"Database Error occured when adding author {author}, error: {e}, raising database error")
                raise HTTPException(status_code=400, detail="Database error") from e
        else:
            logging.debug(f"Author {author} already exsists")
            author_keys.append(result.id)

        return author_keys
    

def search_genres(book, spare_goodreads, db):
    genres = None
    genre_keys = []
    title= book["title"]
    title= title.replace(" ", "+")

    book_url = "https://openlibrary.org/search.json"
    book_params = {"q": title}

    res = requests.get(book_url, params=book_params)

    first_for_genre = True

    try:
        goodreads_id = res.json()["docs"][0]["id_goodreads"]
    except (IndexError, KeyError):
        goodreads_id = spare_goodreads
        first_for_genre = False

    if first_for_genre:
        for id in goodreads_id:
            try:
                genres = scrape(id)
                break
            except IndexError:
                logging.info("scraping failed, trying next index")
            except HTTPError as e:
                logging.info(f"scraping failed, error: {e}")

    if not genres:
        if spare_goodreads:
            for id in spare_goodreads:
                try:
                    genres = scrape(id)
                    break
                except IndexError:
                    logging.info("scraping failed, trying next index")
                except HTTPError as e:
                    logging.info(f"scraping failed, error: {e}")


        for genre in genres:
            result = db.execute(
                select(Category)
                .where(Category.name == genre)
            ).scalars().first()
            if not result:
                try:
                    logging.debug(f"Genre {genre} does not exsist, adding genre to database")
                    genre_dict = {"name": genre}
                    db_author = Category(**genre_dict)
                    add = db.execute(insert(Category).values(name=genre))
                    commit = db.commit()
                    add = add.inserted_primary_key
                    genre_keys.append(add[0])
                except IntegrityError as e:
                    logging.info(f"Database Error occured when adding genre {genre}, error: {e}, raising database error")
                    raise HTTPException(status_code=400, detail="Database error") from e
            else:
                logging.debug(f"Genre {genre} already exsists") 
                genre_keys.append(result.id)

    return genre_keys


if __name__ == "__main__":
    logging.debug("start of program")
    fetch_google_books(12)
    logging.debug("end of program")
    