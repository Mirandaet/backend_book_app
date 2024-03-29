import requests
import json
import logging
from google_books_api import fetch_google_books

logging.basicConfig(filename="logs/open_library_api_logs.txt", level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s")



def fetch_genre():
    index = 3000
    loop_index = 330
    while True:
        logging.debug(f"Looping fetch genre, offset: {index}")
        genre = "romance.json"

        book_url = f"https://openlibrary.org/subjects/{genre}"
        book_params = {"limit": 1000, "offset": index}
        index += 1000

        res = requests.get(book_url, params=book_params)
        response = res.json()

        if response["works"] is False:
            logging.debug("Empty response, ending loop")
            break

        for ind, book in enumerate(response["works"][loop_index:]):
            logging.debug(f"Book number {ind}")
            book_url = "https://openlibrary.org/search.json"
            
            open_search_term =  book["title"].replace(" ", "+")
            book_params = {"q": open_search_term}
            res = requests.get(book_url, params=book_params)

            try:
                goodreads_id = res.json()["docs"][0]
            except (KeyError, requests.JSONDecodeError):
                goodreads_id = False
            
            search_term = book["title"].replace(" ", "+intitle:")
            search_term = "intitle:" + search_term

            
            fetch_google_books(search_term=search_term, spare_goodreads=goodreads_id)

        loop_index = 0
    

        print("End of loop")
        logging.debug("End of loop")


if __name__ == "__main__":
    logging.debug("Start of program")
    fetch_genre()
    logging.debug("End of program")