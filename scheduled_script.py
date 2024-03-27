from app.db_setup import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Depends
from datetime import datetime
from app.database.models import YearlyPageCount


db: Session = next(get_db())

def delete_current_month_pages_read(db: Session = Depends(get_db)):
    current_month = datetime.now().strftime('%B').lower()
    query = select(YearlyPageCount)
    yearly_page_counts = db.execute(query).scalars().all()
    for yearly_page_count in yearly_page_counts:
        if getattr(yearly_page_count, current_month) > 0:
            setattr(yearly_page_count, current_month, 0)
    db.commit()

    return {"message": "Pages read for the current month have been deleted."}