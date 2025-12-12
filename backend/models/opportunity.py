from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from backend.database import Base

class Opportunity(Base):
    """Opportunity model for detected trading opportunities"""
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Market information
    market_id = Column(String, nullable=False, index=True)
    market_name = Column(String, nullable=False)
    
    # Current prices
    price_yes = Column(Float, nullable=False)
    price_no = Column(Float, nullable=False)
    
    # Opportunity metrics
    divergence = Column(Float, nullable=False)  # Price divergence from 1.0
    score = Column(Integer, nullable=False, index=True)  # Score 1-10
    
    # Market metrics
    volume_24h = Column(Float, nullable=True)
    liquidity = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_traded = Column(Boolean, default=False)
    
    # Timestamps
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Opportunity(id={self.id}, market={self.market_name}, score={self.score})>"
