import sys
import os
from sqlalchemy import text

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine

def migrate():
    print("🔄 Migrating database schema...")
    with engine.connect() as conn:
        # ScannerConfig updates
        try:
            conn.execute(text("ALTER TABLE scanner_config ADD COLUMN exit_model VARCHAR DEFAULT 'GLOBAL'"))
            print("✅ Added exit_model to scanner_config")
        except Exception as e:
            print(f"⚠️  Already exists: exit_model")

        try:
            conn.execute(text("ALTER TABLE scanner_config ADD COLUMN leg_stop_loss_percent FLOAT DEFAULT 0.0"))
            print("✅ Added leg_stop_loss_percent to scanner_config")
        except Exception as e:
            print(f"⚠️  Already exists: leg_stop_loss_percent")

        try:
            conn.execute(text("ALTER TABLE scanner_config ADD COLUMN leg_take_profit_price FLOAT DEFAULT 0.0"))
            print("✅ Added leg_take_profit_price to scanner_config")
        except Exception as e:
            print(f"⚠️  Already exists: leg_take_profit_price")

        # Position updates
        try:
            conn.execute(text("ALTER TABLE positions ADD COLUMN is_yes_closed BOOLEAN DEFAULT FALSE"))
            print("✅ Added is_yes_closed to positions")
        except Exception as e:
            print(f"⚠️  Already exists: is_yes_closed")

        try:
            conn.execute(text("ALTER TABLE positions ADD COLUMN is_no_closed BOOLEAN DEFAULT FALSE"))
            print("✅ Added is_no_closed to positions")
        except Exception as e:
            print(f"⚠️  Already exists: is_no_closed")
            
        conn.commit()
    print("🎉 Migration complete!")

if __name__ == "__main__":
    migrate()
