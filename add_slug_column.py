import sys
import os
from sqlalchemy import create_engine, text
from backend.config import settings

def migrate_slug():
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        try:
            print("Adding market_slug column...")
            conn.execute(text("ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS market_slug VARCHAR"))
            conn.commit()
            print("Column added successfully (or existed).")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    migrate_slug()
