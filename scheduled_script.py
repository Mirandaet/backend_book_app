import schedule
import time
from main import delete_current_month_pages_read
from app.db_setup import get_db
from sqlalchemy.orm import Session

db: Session = next(get_db())

def job():
    delete_current_month_pages_read(db)

def start_scheduler():
    schedule.every(20).seconds.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)