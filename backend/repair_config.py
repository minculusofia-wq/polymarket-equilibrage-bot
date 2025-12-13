from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, engine 
# Import ALL models to ensure they are registered with Base.metadata
from backend.models.scanner_config import ScannerConfig
from backend.models.position import Position
from backend.models.opportunity import Opportunity
from backend.models.trade import Trade
from backend.config import settings

# Initialize DB connection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print("♻️ Resetting database schema (Fresh Start)...")
    # Drop all tables first to handle Enum conflicts or partial states
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")
    
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    print("Checking for existing config...")
    config = db.query(ScannerConfig).first()
    
    if not config:
        print("No config found. Creating new one...")
        config = ScannerConfig()
        db.add(config)
    else:
        print(f"Found config ID {config.id}")

    # FORCE RESET of critical fields to defaults
    print("Repairing configuration values...")
    config.scan_interval_seconds = settings.scanner_interval or 30
    config.max_markets_per_scan = 100
    config.min_score_to_trade = 8
    config.min_score_to_show = 1
    config.min_volume_24h = 5000.0
    config.min_liquidity = 2000.0
    config.max_active_positions = settings.default_max_positions or 5
    config.max_capital_per_trade = settings.default_capital_allocation or 20
    config.max_total_capital = (settings.default_capital_allocation or 20) * (settings.default_max_positions or 5)
    config.default_ratio_yes = settings.default_ratio_yes or 50
    config.default_ratio_no = settings.default_ratio_no or 50
    config.stop_loss_percent = settings.default_stop_loss or 10.0
    config.take_profit_percent = settings.default_take_profit or 20.0
    
    # New fields that might be causing issues
    config.exit_model = "GLOBAL"
    config.leg_stop_loss_percent = 5.0
    config.leg_take_profit_price = 0.98
    config.auto_trading_enabled = False

    db.commit()
    print("✅ Configuration successfully repaired and saved!")

except Exception as e:
    print(f"❌ Error repairing config: {e}")
    db.rollback()
finally:
    db.close()
