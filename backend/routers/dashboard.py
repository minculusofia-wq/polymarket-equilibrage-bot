"""
Dashboard API Router
Endpoints for bot status and dashboard data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.config import settings
from backend.models.position import Position, PositionStatus
from backend.models.opportunity import Opportunity
from backend.models.trade import Trade

router = APIRouter(prefix="/api", tags=["dashboard"])


# ==================== SCHEMAS ====================

class BotStatusResponse(BaseModel):
    status: str  # running, paused, error
    wallet_configured: bool
    total_capital: float
    capital_engaged: float
    capital_available: float
    active_positions: int
    total_pnl: float
    total_pnl_percent: float
    opportunities_count: int
    best_opportunity_score: int
    timestamp: datetime


class DashboardStatsResponse(BaseModel):
    # Capital
    total_capital: float
    capital_engaged: float
    capital_available: float
    
    # Positions
    active_positions: int
    closed_positions: int
    
    # Performance
    total_pnl: float
    total_pnl_percent: float
    winning_trades: int
    losing_trades: int
    win_rate: float
    
    # Opportunities
    active_opportunities: int
    best_score: int


class RecentTradeResponse(BaseModel):
    id: int
    position_id: int
    market_name: str
    side: str
    type: str
    amount: float
    price: float
    total_value: float
    executed_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status(db: Session = Depends(get_db)):
    """
    Get current bot status
    """
    # Check wallet configuration
    wallet_configured = bool(settings.wallet_private_key and settings.wallet_address)
    
    # Get positions
    active_positions = db.query(Position).filter(Position.status == PositionStatus.ACTIVE).all()
    all_positions = db.query(Position).all()
    
    # Calculate capital
    capital_engaged = sum((p.amount_yes + p.amount_no) for p in active_positions)
    total_capital = 0  # TODO: Get from wallet balance
    capital_available = total_capital - capital_engaged
    
    # Calculate P&L
    total_pnl = sum(p.pnl or 0 for p in all_positions)
    initial_capital = sum((p.amount_yes + p.amount_no) for p in all_positions) or 1
    total_pnl_percent = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0
    
    # Get opportunities
    opportunities = db.query(Opportunity).filter(Opportunity.is_active == True).all()
    best_score = max((o.score for o in opportunities), default=0)
    
    return BotStatusResponse(
        status="running",
        wallet_configured=wallet_configured,
        total_capital=total_capital,
        capital_engaged=capital_engaged,
        capital_available=capital_available,
        active_positions=len(active_positions),
        total_pnl=total_pnl,
        total_pnl_percent=total_pnl_percent,
        opportunities_count=len(opportunities),
        best_opportunity_score=best_score,
        timestamp=datetime.utcnow()
    )


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get detailed dashboard statistics
    """
    # Positions
    all_positions = db.query(Position).all()
    active_positions = [p for p in all_positions if p.status == PositionStatus.ACTIVE]
    closed_positions = [p for p in all_positions if p.status == PositionStatus.CLOSED]
    
    # Capital
    capital_engaged = sum((p.amount_yes + p.amount_no) for p in active_positions)
    total_capital = 0  # TODO: Get from wallet
    
    # Performance
    total_pnl = sum(p.pnl or 0 for p in all_positions)
    initial = sum((p.amount_yes + p.amount_no) for p in all_positions) or 1
    
    winning = len([p for p in closed_positions if (p.pnl or 0) > 0])
    losing = len([p for p in closed_positions if (p.pnl or 0) < 0])
    win_rate = (winning / (winning + losing) * 100) if (winning + losing) > 0 else 0
    
    # Opportunities
    opportunities = db.query(Opportunity).filter(Opportunity.is_active == True).all()
    
    return DashboardStatsResponse(
        total_capital=total_capital,
        capital_engaged=capital_engaged,
        capital_available=total_capital - capital_engaged,
        active_positions=len(active_positions),
        closed_positions=len(closed_positions),
        total_pnl=total_pnl,
        total_pnl_percent=(total_pnl / initial * 100) if initial > 0 else 0,
        winning_trades=winning,
        losing_trades=losing,
        win_rate=win_rate,
        active_opportunities=len(opportunities),
        best_score=max((o.score for o in opportunities), default=0)
    )


@router.get("/trades/recent", response_model=List[RecentTradeResponse])
async def get_recent_trades(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get most recent trades"""
    trades = (
        db.query(Trade)
        .order_by(Trade.executed_at.desc())
        .limit(limit)
        .all()
    )
    return trades
