"""Compatibility wrapper. Canonical seed is `python -m app.seed`."""

from app.database.connection import SessionLocal
from app.seed import seed_if_empty


def seed_demo_scenario():
    db = SessionLocal()
    try:
        result = seed_if_empty(db)
        print(result)
        return result
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_scenario()
