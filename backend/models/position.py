from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from backend.database import Base
import enum

class PositionStatus(str, enum.Enum):
    """Position status enumeration"""
    ACTIVE = "active"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"

class PositionSide(str, enum.Enum):
    """Position side enumeration"""
    YES = "yes"
    NO = "no"
    BOTH = "both"

class Position(Base):
    """Position model for tracking active and historical positions"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Market information
    market_id = Column(String, nullable=False, index=True)
    market_name = Column(String, nullable=False)
    
    # Entry prices
    entry_price_yes = Column(Float, nullable=False)
    entry_price_no = Column(Float, nullable=False)
    
    # Entry amounts
    amount_yes = Column(Float, nullable=False)
    amount_no = Column(Float, nullable=False)
    
    # Current prices (updated by monitor)
    current_price_yes = Column(Float, nullable=True)
    current_price_no = Column(Float, nullable=True)
    
    # Current values
    current_value_yes = Column(Float, nullable=True)
    current_value_no = Column(Float, nullable=True)
    
    # P&L
    pnl = Column(Float, default=0.0)
    pnl_percent = Column(Float, default=0.0)
    
    # Status
    status = Column(Enum(PositionStatus), default=PositionStatus.ACTIVE, index=True)
    
    # Which side is still active (for partial liquidation)
    active_side = Column(Enum(PositionSide), default=PositionSide.BOTH)
    
    # Independent Leg Status
    is_yes_closed = Column(Boolean, default=False)
    is_no_closed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Position(id={self.id}, market={self.market_name}, status={self.status})>"
