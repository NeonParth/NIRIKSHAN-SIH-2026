from app.database.connection import SessionLocal
from app.seed import seed_if_empty

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print(seed_if_empty(db))
    finally:
        db.close()
