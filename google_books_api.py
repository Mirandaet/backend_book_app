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

def fetch_google_books(search_term, spare_goodreads):
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
                book_version_info["is_ebook"] = False
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
                book_version_info["publisher"] = None
            try:
                book_version_info["description"] = book["volumeInfo"]["description"]
            except KeyError:
                logging.debug("description fail")
                continue
            if spare_goodreads:
                search_book_title(book=book_info, book_version = book_version_info, spare_goodreads=spare_goodreads, db=db)
            else:
                search_book_title(book=book_info, book_version = book_version_info, db=db)
            logging.debug("End of google_books loop")





def search_book_title(book: BookSchema, book_version: BookVersionSchema, db, spare_goodreads = None):
    logging.debug(f"start of search_book_title, searching for {book["title"]}")
    result = None
    book_key = None
    found_book = False  
    book["title"] = string.capwords(book["title"])
  

    result = db.execute(
        select(Book)
        .where(Book.title == book["title"])
    ).scalars().first()
    logging.debug(f"Result: {result}")

    if not result:
        author_keys = author_search(book=book, db=db)
        del book["authors"]
        genre_keys, publihed_date = search_goodreads(book=book, spare_goodreads=spare_goodreads, db=db)

            

        book["first_published"] = publihed_date

        if not genre_keys:
            return

        book["main_category_id"] = genre_keys[0]
        try:
            logging.debug(f"adding book {book["title"]} to database")
            add = db.execute(insert(Book).values(**book))
            add = add.inserted_primary_key
            book_key = add.id
            db.commit()
            logging.debug(f"{book["title"]} added to database")
        except IntegrityError as e:
            logging.info(f"Error occured when adding book {book["title"]} to database, error: {e}")
            db.commit()
        del genre_keys[0]


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
    else:
        book_key = result.id
        


    if not book_key:
        return                        
    
    url_key = None
    result = db.execute(
        select(BookCover)
        .where(BookCover.url == book_version["book_cover"])
    ).scalars().first()
    if not result:
        try:
            logging.debug(f"Book cover { book_version["book_cover"]} does not exsist, adding cover to database")
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

    if book_version["publisher"]:
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


    if not book_key:
        logging.debug("Could not add book to database, ending search_book_title")
        return

    try:
        book_version["book_id"] = book_key
        logging.debug(f"adding book book version to database")
        db.execute(insert(BookVersion).values(**book_version))
        db.commit()
        logging.debug(f"Book version added to database")
    except IntegrityError as e:
        logging.info(f"Error occured when adding book book version to database, error: {e}")
        db.commit()

    logging.debug("End of search_book_title")


def author_search(book, db):
    author_keys = []


    for author in book["authors"]:
        author = author.replace(".", "")
        author = string.capwords(author)
        try:
            result = db.scalars(select(Author).where(Author.name == author)).first()
            db.commit()
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
    

def search_goodreads(book, db, spare_goodreads = None):
    genres = None
    genre_keys = []
    title= book["title"]
    title= title.replace(" ", "+")
    intitle = True

    book_url = "https://openlibrary.org/search.json"
    book_params = {"q": title}

    try:
        res = requests.get(book_url, params=book_params)
    except Exception as e:
        logging.warning(f"Error occured when fetching goodreads_id error: {e}")

    first_for_genre = True

    try:
        open_library_docs = res.json()["docs"][0]
        goodreads_id = open_library_docs["id_goodreads"]
    except (IndexError, KeyError, requests.JSONDecodeError):
        logging.debug("could not find goodreads id, using spare goodreads id")
        goodreads_id = spare_goodreads
        first_for_genre = False

    if first_for_genre:
        if open_library_docs["title"].lower() not in book["title"].lower():
            if book["title"].lower() not in open_library_docs["title"].lower():
             intitle = False
        if intitle:  
            for id in goodreads_id:
                try:
                    goodreads_results = scrape(id)
                    genres = goodreads_results[0]
                    if genres is None:
                        continue
                    published_date = goodreads_results[1]
                    break
                except IndexError:
                    logging.info("scraping failed, trying next index")
                except HTTPError as e:
                    logging.info(f"scraping failed, error: {e}")

    if not genres:
        if spare_goodreads:
            if spare_goodreads["title"].lower() == book["title"].lower():
                try:
                    spare_goodreads_id = spare_goodreads["id_goodreads"]
                except KeyError:
                    logging.debug("No goodreads_id in spare_goodreads")
                    spare_goodreads_id = []
                for id in spare_goodreads_id:
                    try:
                        goodreads_results = scrape(id)
                        if goodreads_results is None:
                            continue
                        genres = goodreads_results[0]
                        published_date = goodreads_results[1]
                        break
                    except IndexError:
                        logging.info("scraping failed, trying next index")
                    except HTTPError as e:
                        logging.info(f"scraping failed, error: {e}")

    if not genres:
        logging.info("No genres from goodreads")
        return None, None

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

    return (genre_keys, published_date)


if __name__ == "__main__":
    logging.debug("start of program")
    fetch_google_books(12)
    logging.debug("end of program")
    