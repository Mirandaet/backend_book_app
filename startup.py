from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db_setup import get_db
from sqlalchemy.orm import sessionmaker
from app.database.models import User, Category, Book, SubCategory, BookShelf, Achievement, CompletedAchievement, YearlyPageCount, BookCover, Author, AuthorBook, Publisher
from datetime import datetime

# Replace 'your_database_url' with the actual URL of your database
db: Session = next(get_db())

try:
    # Create Categories
    categories_data = [
        {'name': 'Fiction', 'color_code': '#FF0000'},
        {'name': 'Non-Fiction', 'color_code': '#00FF00'},
        {'name': 'Mystery', 'color_code': '#0000FF'},
        {'name': 'Science Fiction', 'color_code': '#FFFF00'},
        {'name': 'Biography', 'color_code': '#FF00FF'},
        {'name': 'History', 'color_code': '#00FFFF'},
        {'name': 'Thriller', 'color_code': '#FFA500'},
        {'name': 'Romance', 'color_code': '#800080'},
        {'name': 'Self-Help', 'color_code': '#008000'},
        {'name': 'Fantasy', 'color_code': '#000080'}
    ]
    

    for category_data in categories_data:
        category = Category(**category_data)
        db.add(category)

    db.commit()

    # Create BookCover
    book_covers_data = [
        {'url': 'https://example.com/book1.jpg'},
        {'url': 'https://example.com/book2.jpg'},
        {'url': 'https://example.com/book3.jpg'},
        {'url': 'https://example.com/book4.jpg'},
    ]

    for book_cover_data in book_covers_data:
        book_cover = BookCover(**book_cover_data)
        db.add(book_cover)

    db.commit()

    
    publishers_data = [
    {'name': 'Publisher A'},
    {'name': 'Publisher B'},
    {'name': 'Publisher C'},
    {'name': 'Publisher D'},
    {'name': 'Publisher E'},
    {'name': 'Publisher F'},
    {'name': 'Publisher G'},
    {'name': 'Publisher H'},
    {'name': 'Publisher I'},
    {'name': 'Publisher J'},
]

    for publisher_data in publishers_data:
        publisher = Publisher(**publisher_data)
        db.add(publisher)


    db.commit()

    # Create Users
    users_data = [
        {'email': 'user1@example.com', 'password': '$2b$12$6krgi17eGmfHYHMFqEkWo.1xi5eUgva51GrQn1fs4YE7YPARfLqfi', 'user_name': 'User1', 'book_goal': 30},
        {'email': 'user2@example.com', 'password': 'password2', 'user_name': 'User2', 'book_goal': 20},
        {'email': 'user3@example.com', 'password': 'password3', 'user_name': 'User3', 'book_goal': 25},
        {'email': 'user4@example.com', 'password': 'password4', 'user_name': 'User4', 'book_goal': 15},
        {'email': 'user5@example.com', 'password': 'password5', 'user_name': 'User5', 'book_goal': 40},
        {'email': 'user6@example.com', 'password': 'password6', 'user_name': 'User6', 'book_goal': 10},
        {'email': 'user7@example.com', 'password': 'password7', 'user_name': 'User7', 'book_goal': 35},
        {'email': 'user8@example.com', 'password': 'password8', 'user_name': 'User8', 'book_goal': 28},
        {'email': 'user9@example.com', 'password': 'password9', 'user_name': 'User9', 'book_goal': 18},
        {'email': 'user10@example.com', 'password': 'password10', 'user_name': 'User10', 'book_goal': 22}
    ]

    for user_data in users_data:
        user = User(**user_data)
        db.add(user)

    db.commit()

    # Create Books
    books_data = [
    {'title': 'Book 1', 'page_count': 300, 'is_ebook': False, 'publisher_id': 1, 'publish_date': datetime(2023, 1, 1), 'description': 'Description of Book 1', 'language': 'English', 'main_category_id': 1, "book_cover_id": 1},
    {'title': 'Book 2', 'page_count': 400, 'is_ebook': True, 'publisher_id': 2, 'publish_date': datetime(2023, 2, 1), 'description': 'Description of Book 2', 'language': 'French', 'main_category_id': 2, "book_cover_id": 2},
    {'title': 'Book 3', 'page_count': 250, 'is_ebook': False, 'publisher_id': 3, 'publish_date': datetime(2023, 3, 1), 'description': 'Description of Book 3', 'language': 'German', 'main_category_id': 3, "book_cover_id": 3},
    {'title': 'Book 4', 'page_count': 350, 'is_ebook': True, 'publisher_id': 4, 'publish_date': datetime(2023, 4, 1), 'description': 'Description of Book 4', 'language': 'Spanish', 'main_category_id': 4, "book_cover_id": 4},
    {'title': 'Book 5', 'page_count': 200, 'is_ebook': False, 'publisher_id': 5, 'publish_date': datetime(2023, 5, 1), 'description': 'Description of Book 5', 'language': 'Italian', 'main_category_id': 5, "book_cover_id": 1},
    {'title': 'Book 6', 'page_count': 320, 'is_ebook': False, 'publisher_id': 6, 'publish_date': datetime(2023, 6, 1), 'description': 'Description of Book 6', 'language': 'English', 'main_category_id': 1, "book_cover_id": 2},
    {'title': 'Book 7', 'page_count': 420, 'is_ebook': True, 'publisher_id': 6, 'publish_date': datetime(2023, 7, 1), 'description': 'Description of Book 7', 'language': 'French', 'main_category_id': 2, "book_cover_id": 3},
    {'title': 'Book 8', 'page_count': 270, 'is_ebook': False, 'publisher_id': 6, 'publish_date': datetime(2023, 8, 1), 'description': 'Description of Book 8', 'language': 'German', 'main_category_id': 3, "book_cover_id": 4},
    {'title': 'Book 9', 'page_count': 380, 'is_ebook': True, 'publisher_id': 1, 'publish_date': datetime(2023, 9, 1), 'description': 'Description of Book 9', 'language': 'Spanish', 'main_category_id': 4, "book_cover_id": 1},
    {'title': 'Book 10', 'page_count': 220, 'is_ebook': False, 'publisher_id': 1, 'publish_date': datetime(2023, 10, 1), 'description': 'Description of Book 10', 'language': 'Italian', 'main_category_id': 5, "book_cover_id": 2},
]

    for book_data in books_data:
        book = Book(**book_data)
        db.add(book)

    db.commit()

    # Create SubCategories
    subcategories_data = [
        {'category_id': 1, 'book_id': 1},
        {'category_id': 2, 'book_id': 2},
        {'category_id': 3, 'book_id': 3},
        {'category_id': 4, 'book_id': 4},
        {'category_id': 5, 'book_id': 5},
        {'category_id': 6, 'book_id': 6},
        {'category_id': 7, 'book_id': 7},
        {'category_id': 8, 'book_id': 8},
        {'category_id': 9, 'book_id': 9},
        {'category_id': 10, 'book_id': 10}
    ]

    for subcategory_data in subcategories_data:
        subcategory = SubCategory(**subcategory_data)
        db.add(subcategory)

    db.commit()

    # Create BookShelves
    bookshelves_data = [
        {'pages_read': 100, 'start_date': datetime(2023, 1, 1), 'finished_date': None, 'user_id': 1, 'book_id': 1, 'isFinished': False},
        {'pages_read': 150, 'start_date': datetime(2023, 2, 1), 'finished_date': None, 'user_id': 1, 'book_id': 2, 'isFinished': False},
        {'pages_read': 50, 'start_date': datetime(2023, 3, 1), 'finished_date': datetime(2023, 3, 7), 'user_id': 1, 'book_id': 3, 'isFinished': True},
        {'pages_read': 120, 'start_date': datetime(2023, 4, 1), 'finished_date': datetime(2023, 4, 15), 'user_id': 1, 'book_id': 4, 'isFinished': True},
        {'pages_read': 80, 'start_date': datetime(2023, 5, 1), 'finished_date': datetime(2023, 5, 20), 'user_id': 1, 'book_id': 5, 'isFinished': True},
        {'pages_read': 200, 'start_date': datetime(2023, 6, 1), 'finished_date': None, 'user_id': 1, 'book_id': 6, 'isFinished': False},
        {'pages_read': 90, 'start_date': datetime(2023, 7, 1), 'finished_date': None, 'user_id': 1, 'book_id': 7, 'isFinished': False},
        {'pages_read': 180, 'start_date': datetime(2023, 8, 1), 'finished_date': datetime(2023, 8, 12), 'user_id': 1, 'book_id': 8, 'isFinished': True},
        {'pages_read': 60, 'start_date': datetime(2023, 9, 1), 'finished_date': datetime(2023, 9, 18), 'user_id': 1, 'book_id': 9, 'isFinished': True},
        {'pages_read': 130, 'start_date': datetime(2023, 10, 1), 'finished_date': datetime(2023, 10, 5), 'user_id': 1, 'book_id': 10, 'isFinished': True}
    ]


    for bookshelf_data in bookshelves_data:
        bookshelf = BookShelf(**bookshelf_data)
        db.add(bookshelf)

    db.commit()


    # Create Achievements 
    achievements_data = [
        {'name': 'Read 10 Books'},
        {'name': 'Read 50 Pages in a Day'},
        {'name': 'Complete a Mystery Book'},
        {'name': 'Achieve 100 Pages in a Sitting'},
        {'name': 'Read a Non-Fiction Bestseller'},
        {'name': 'Finish a Science Fiction Novel'},
        {'name': 'Explore a Biography'},
        {'name': 'Uncover a Thriller'},
        {'name': 'Experience a Romantic Tale'},
        {'name': 'Master the Art of Self-Help'}
    ]

    for achievement_data in achievements_data:
        achievement = Achievement(**achievement_data)
        db.add(achievement)

    db.commit()

    # Create CompletedAchievements
    completed_achievements_data = [
        {'achievements_id': 1, 'user_id': 1},
        {'achievements_id': 2, 'user_id': 2},
        {'achievements_id': 3, 'user_id': 3},
        {'achievements_id': 4, 'user_id': 4},
        {'achievements_id': 5, 'user_id': 5},
        {'achievements_id': 6, 'user_id': 6},
        {'achievements_id': 7, 'user_id': 7},
        {'achievements_id': 8, 'user_id': 8},
        {'achievements_id': 9, 'user_id': 9},
        {'achievements_id': 10, 'user_id': 10}
    ]

    for completed_achievement_data in completed_achievements_data:
        completed_achievement = CompletedAchievement(**completed_achievement_data)
        db.add(completed_achievement)


    yearly_page_counts_data = [
    {'january': 500, 'february': 600, 'march': 450, 'april': 700, 'may': 600, 'june': 700, 'july': 600, 'august': 700, 'september': 600, 'october': 700, 'november': 600, 'december': 700, 'user_id': 1},
    {'january': 550, 'february': 650, 'march': 500, 'april': 800, 'may': 600, 'june': 700, 'july': 600, 'august': 700, 'september': 600, 'october': 700, 'november': 600, 'december': 700, 'user_id': 2},
]

    for yearly_page_count_data in yearly_page_counts_data:
        yearly_page_count = YearlyPageCount(**yearly_page_count_data)
        db.add(yearly_page_count)

    db.commit()

    # Create Author
    authors_data = [
        {'name': 'Author 1'},
        {'name': 'Author 2'},
        {'name': 'Author 3'},
        {'name': 'Author 4'},
    ]

    for author_data in authors_data:
        author = Author(**author_data)
        db.add(author)

    db.commit()

    # Create AuthorBook
    author_books_data = [
        {'author_id': 1, 'book_id': 1},
        {'author_id': 2, 'book_id': 2},
        {'author_id': 3, 'book_id': 3},
        {'author_id': 4, 'book_id': 4},
    ]

    for author_book_data in author_books_data:
        author_book = AuthorBook(**author_book_data)
        db.add(author_book)

    db.commit()
    
    print("Dummy data created successfully!")

except Exception as e:
    db.rollback()
    print(f"An error occurred: {e}")

finally:
    db.close()


