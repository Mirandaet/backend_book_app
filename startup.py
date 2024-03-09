from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db_setup import get_db
from sqlalchemy.orm import sessionmaker
from app.database.models import User, Category, Book, SubCategory, BookShelf, Achievement, CompletedAchievement, Base
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
        {'title': 'Book1', 'page_count': 200, 'is_ebook': False, 'main_category_id': 1},
        {'title': 'Book2', 'page_count': 300, 'is_ebook': True, 'main_category_id': 2},
        {'title': 'Book3', 'page_count': 150, 'is_ebook': True, 'main_category_id': 3},
        {'title': 'Book4', 'page_count': 250, 'is_ebook': False, 'main_category_id': 1},
        {'title': 'Book5', 'page_count': 180, 'is_ebook': True, 'main_category_id': 4},
        {'title': 'Book6', 'page_count': 320, 'is_ebook': False, 'main_category_id': 5},
        {'title': 'Book7', 'page_count': 190, 'is_ebook': True, 'main_category_id': 6},
        {'title': 'Book8', 'page_count': 270, 'is_ebook': False, 'main_category_id': 7},
        {'title': 'Book9', 'page_count': 220, 'is_ebook': True, 'main_category_id': 8},
        {'title': 'Book10', 'page_count': 280, 'is_ebook': False, 'main_category_id': 9}
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
        {'pages_read': 100, 'start_date': datetime(2023, 1, 1), 'finished_date': datetime(2023, 1, 5), 'user_id': 1, 'book_id': 1},
        {'pages_read': 150, 'start_date': datetime(2023, 2, 1), 'finished_date': datetime(2023, 2, 10), 'user_id': 1, 'book_id': 2},
        {'pages_read': 50, 'start_date': datetime(2023, 3, 1), 'finished_date': datetime(2023, 3, 7), 'user_id': 1, 'book_id': 3},
        {'pages_read': 120, 'start_date': datetime(2023, 4, 1), 'finished_date': datetime(2023, 4, 15), 'user_id': 1, 'book_id': 4},
        {'pages_read': 80, 'start_date': datetime(2023, 5, 1), 'finished_date': datetime(2023, 5, 20), 'user_id': 1, 'book_id': 5},
        {'pages_read': 200, 'start_date': datetime(2023, 6, 1), 'finished_date': datetime(2023, 6, 8), 'user_id': 1, 'book_id': 6},
        {'pages_read': 90, 'start_date': datetime(2023, 7, 1), 'finished_date': datetime(2023, 7, 25), 'user_id': 1, 'book_id': 7},
        {'pages_read': 180, 'start_date': datetime(2023, 8, 1), 'finished_date': datetime(2023, 8, 12), 'user_id': 1, 'book_id': 8},
        {'pages_read': 60, 'start_date': datetime(2023, 9, 1), 'finished_date': datetime(2023, 9, 18), 'user_id': 1, 'book_id': 9},
        {'pages_read': 130, 'start_date': datetime(2023, 10, 1), 'finished_date': datetime(2023, 10, 5), 'user_id': 1, 'book_id': 10}
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

    db.commit()
    print("Dummy data created successfully!")

except Exception as e:
    db.rollback()
    print(f"An error occurred: {e}")

finally:
    db.close()


