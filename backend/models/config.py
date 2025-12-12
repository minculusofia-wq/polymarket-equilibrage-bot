from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class Config(Base):
    """Configuration model for storing bot settings"""
    __tablename__ = "config"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Configuration key-value
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(String, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Config(key={self.key}, value={self.value})>"
