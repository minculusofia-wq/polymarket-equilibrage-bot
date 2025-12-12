from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://polymarket_user:polymarket_pass@localhost:5432/polymarket"
    )
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Polymarket API
    polymarket_api_key: Optional[str] = os.getenv("POLYMARKET_API_KEY")
    polymarket_api_url: str = os.getenv(
        "POLYMARKET_API_URL",
        "https://clob.polymarket.com"
    )
    polymarket_api_secret: Optional[str] = os.getenv("POLYMARKET_API_SECRET")
    polymarket_api_passphrase: Optional[str] = os.getenv("POLYMARKET_API_PASSPHRASE")
    web3_provider_url: str = os.getenv("WEB3_PROVIDER_URI", "")
    
    
    # Wallet
    wallet_address: Optional[str] = os.getenv("WALLET_ADDRESS")
    wallet_private_key: Optional[str] = os.getenv("WALLET_PRIVATE_KEY")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Application
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Trading Configuration
    default_ratio_yes: int = int(os.getenv("DEFAULT_RATIO_YES", "50"))
    default_ratio_no: int = int(os.getenv("DEFAULT_RATIO_NO", "50"))
    default_stop_loss: float = float(os.getenv("DEFAULT_STOP_LOSS", "0"))
    default_take_profit: float = float(os.getenv("DEFAULT_TAKE_PROFIT", "0"))
    default_max_positions: int = int(os.getenv("DEFAULT_MAX_POSITIONS", "5"))
    default_capital_allocation: int = int(os.getenv("DEFAULT_CAPITAL_ALLOCATION", "20"))
    
    # Scanner Configuration
    scanner_interval: int = int(os.getenv("SCANNER_INTERVAL", "60"))
    position_monitor_interval: int = int(os.getenv("POSITION_MONITOR_INTERVAL", "30"))
    whale_tracker_interval: int = int(os.getenv("WHALE_TRACKER_INTERVAL", "120"))
    
    # Sniper Mode Configuration
    enable_sniper_mode: bool = os.getenv("ENABLE_SNIPER_MODE", "False").lower() == "true"
    sniper_max_subscriptions: int = int(os.getenv("SNIPER_MAX_SUBSCRIPTIONS", "50"))
    
    
    # Discord Notifications
    discord_webhook_url: Optional[str] = os.getenv("DISCORD_WEBHOOK_URL")
    discord_notify_min_score: int = int(os.getenv("DISCORD_NOTIFY_MIN_SCORE", "7"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
