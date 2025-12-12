"""
Scanner Configuration Model
Stores scanner settings in database for persistence.
"""
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime
from sqlalchemy.sql import func
from backend.database import Base


class ScannerConfig(Base):
    """Scanner configuration stored in database"""
    __tablename__ = "scanner_config"
    
    id = Column(Integer, primary_key=True, default=1)
    
    # Auto trading toggle
    auto_trading_enabled = Column(Boolean, default=False)
    
    # Scanning settings
    scan_interval_seconds = Column(Integer, default=30)
    max_markets_per_scan = Column(Integer, default=100)
    
    # Scoring thresholds
    min_score_to_trade = Column(Integer, default=0)
    min_score_to_show = Column(Integer, default=0)
    
    # Volume & Liquidity filters
    min_volume_24h = Column(Float, default=0.0)
    min_liquidity = Column(Float, default=0.0)
    
    # Position limits
    max_active_positions = Column(Integer, default=0)
    max_capital_per_trade = Column(Float, default=0.0)
    max_total_capital = Column(Float, default=0.0)
    
    # Entry ratios (default 0)
    default_ratio_yes = Column(Integer, default=0)
    default_ratio_no = Column(Integer, default=0)
    
    # Stop Loss / Take Profit
    stop_loss_percent = Column(Float, default=0.0)
    take_profit_percent = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            "auto_trading_enabled": self.auto_trading_enabled,
            "scan_interval_seconds": self.scan_interval_seconds,
            "max_markets_per_scan": self.max_markets_per_scan,
            "min_score_to_trade": self.min_score_to_trade,
            "min_score_to_show": self.min_score_to_show,
            "min_volume_24h": self.min_volume_24h,
            "min_liquidity": self.min_liquidity,
            "max_active_positions": self.max_active_positions,
            "max_capital_per_trade": self.max_capital_per_trade,
            "max_total_capital": self.max_total_capital,
            "default_ratio_yes": self.default_ratio_yes,
            "default_ratio_no": self.default_ratio_no,
            "stop_loss_percent": self.stop_loss_percent,
            "take_profit_percent": self.take_profit_percent,
        }
