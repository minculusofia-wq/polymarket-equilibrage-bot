
import os
import sys
from sqlalchemy import create_engine, text

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings

def migrate():
    print("Checking database schema...")
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        try:
            # Check if columns exist
            result = conn.execute(text("SELECT spread_percent, estimated_net_profit FROM opportunities LIMIT 1"))
            print("Columns already exist.")
        except Exception:
            conn.rollback()  # Reset transaction state
            print("Columns missing. Adding them...")
            try:
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN spread_percent FLOAT DEFAULT 0.0"))
                conn.execute(text("ALTER TABLE opportunities ADD COLUMN estimated_net_profit FLOAT DEFAULT 0.0"))
                conn.commit()
                print("Migration successful: Added spread_percent and estimated_net_profit.")
            except Exception as e:
                print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
