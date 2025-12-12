from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base
import enum

class TradeType(str, enum.Enum):
    """Trade type enumeration"""
    ENTRY = "entry"
    EXIT = "exit"
    PARTIAL_EXIT = "partial_exit"

class TradeSide(str, enum.Enum):
    """Trade side enumeration"""
    YES = "yes"
    NO = "no"

class Trade(Base):
    """Trade model for tracking all trade executions"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Position reference
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False, index=True)
    
    # Market information
    market_id = Column(String, nullable=False)
    market_name = Column(String, nullable=False)
    
    # Trade details
    side = Column(Enum(TradeSide), nullable=False)
    type = Column(Enum(TradeType), nullable=False)
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Total value
    total_value = Column(Float, nullable=False)
    
    # Polymarket order ID (if available)
    order_id = Column(String, nullable=True)
    
    # Timestamp
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Trade(id={self.id}, type={self.type}, side={self.side}, amount={self.amount})>"
