"""
Positions API Router
Endpoints for managing trading positions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.database import get_db
from backend.services.trading_engine import get_trading_engine
from backend.models.position import Position, PositionStatus, PositionSide

router = APIRouter(prefix="/api/positions", tags=["positions"])


# ==================== SCHEMAS ====================

class PositionResponse(BaseModel):
    id: int
    market_id: str
    market_name: str
    entry_price_yes: float
    entry_price_no: float
    amount_yes: float
    amount_no: float
    current_price_yes: Optional[float]
    current_price_no: Optional[float]
    current_value_yes: Optional[float]
    current_value_no: Optional[float]
    pnl: float
    pnl_percent: float
    status: str
    active_side: str
    created_at: datetime
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CreatePositionRequest(BaseModel):
    opportunity_id: int
    capital: float
    ratio_yes: int = 50
    ratio_no: int = 50


class PositionStatsResponse(BaseModel):
    total_positions: int
    active_positions: int
    closed_positions: int
    total_pnl: float
    total_capital_engaged: float


# ==================== ENDPOINTS ====================

@router.get("", response_model=List[PositionResponse])
async def get_positions(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all positions, optionally filtered by status
    
    Args:
        status: Filter by status (active, closed, liquidated)
    """
    query = db.query(Position)
    
    if status:
        status_enum = PositionStatus(status.lower())
        query = query.filter(Position.status == status_enum)
    
    positions = query.order_by(Position.created_at.desc()).all()
    return positions


@router.get("/active", response_model=List[PositionResponse])
async def get_active_positions(db: Session = Depends(get_db)):
    """Get all active positions"""
    engine = get_trading_engine(db)
    return engine.get_active_positions()


@router.get("/stats", response_model=PositionStatsResponse)
async def get_position_stats(db: Session = Depends(get_db)):
    """Get position statistics"""
    all_positions = db.query(Position).all()
    active = [p for p in all_positions if p.status == PositionStatus.ACTIVE]
    closed = [p for p in all_positions if p.status == PositionStatus.CLOSED]
    
    total_pnl = sum(p.pnl or 0 for p in all_positions)
    capital_engaged = sum((p.amount_yes + p.amount_no) for p in active)
    
    return PositionStatsResponse(
        total_positions=len(all_positions),
        active_positions=len(active),
        closed_positions=len(closed),
        total_pnl=total_pnl,
        total_capital_engaged=capital_engaged
    )


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: int,
    db: Session = Depends(get_db)
):
    """Get specific position by ID"""
    engine = get_trading_engine(db)
    position = engine.get_position(position_id)
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    return position


@router.post("", response_model=PositionResponse)
async def create_position(
    request: CreatePositionRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new position from an opportunity
    
    Args:
        opportunity_id: ID of the opportunity to trade
        capital: Amount of capital to allocate
        ratio_yes: Percentage for YES side (0-100)
        ratio_no: Percentage for NO side (0-100)
    """
    from backend.models.opportunity import Opportunity
    
    # Get the opportunity
    opportunity = db.query(Opportunity).filter(Opportunity.id == request.opportunity_id).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    if opportunity.is_traded:
        raise HTTPException(status_code=400, detail="Opportunity already traded")
    
    # Create position
    engine = get_trading_engine(db)
    position = await engine.enter_position(
        opportunity=opportunity,
        capital=request.capital,
        ratio_yes=request.ratio_yes,
        ratio_no=request.ratio_no
    )
    
    if not position:
        raise HTTPException(status_code=500, detail="Failed to create position")
    
    return position


@router.post("/{position_id}/close", response_model=PositionResponse)
async def close_position(
    position_id: int,
    db: Session = Depends(get_db)
):
    """Close a position completely"""
    engine = get_trading_engine(db)
    position = engine.get_position(position_id)
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    if position.status != PositionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Position is not active")
    
    closed_position = await engine.close_position(position)
    return closed_position


@router.post("/{position_id}/update", response_model=PositionResponse)
async def update_position_prices(
    position_id: int,
    db: Session = Depends(get_db)
):
    """Update position with current market prices"""
    engine = get_trading_engine(db)
    position = engine.get_position(position_id)
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    if position.status != PositionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Position is not active")
    
    updated_position = await engine.update_position(position)
    return updated_position
