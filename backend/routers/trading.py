"""
Trading Control API Router
Endpoints for controlling autonomous trading (start, stop, panic).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from backend.database import get_db
from backend.services.auto_trading import get_auto_trading_engine
from backend.models.scanner_config import ScannerConfig
from backend.models.position import Position, PositionStatus

router = APIRouter(prefix="/api/trading", tags=["trading"])


# ==================== SCHEMAS ====================

class TradingStatusResponse(BaseModel):
    is_running: bool
    is_paused: bool
    auto_trading_enabled: bool
    active_positions: int
    total_pnl: float


class ControlResponse(BaseModel):
    success: bool
    message: str
    status: TradingStatusResponse


class PanicResponse(BaseModel):
    success: bool
    positions_closed: int
    message: str


# ==================== HELPERS ====================

def get_trading_status(db: Session) -> TradingStatusResponse:
    """Get current trading status"""
    engine = get_auto_trading_engine()
    
    config = db.query(ScannerConfig).first()
    auto_enabled = config.auto_trading_enabled if config else False
    
    active_positions = db.query(Position).filter(
        Position.status == PositionStatus.ACTIVE
    ).all()
    
    total_pnl = sum(p.pnl or 0 for p in active_positions)
    
    return TradingStatusResponse(
        is_running=engine.is_running,
        is_paused=engine.is_paused,
        auto_trading_enabled=auto_enabled,
        active_positions=len(active_positions),
        total_pnl=total_pnl
    )


# ==================== ENDPOINTS ====================

@router.get("/status", response_model=TradingStatusResponse)
async def get_status(db: Session = Depends(get_db)):
    """Get current trading engine status"""
    return get_trading_status(db)


@router.post("/start", response_model=ControlResponse)
async def start_trading(db: Session = Depends(get_db)):
    """Start the autonomous trading engine"""
    engine = get_auto_trading_engine()
    engine.start()
    
    # Enable auto-trading in config
    config = db.query(ScannerConfig).first()
    if config:
        config.auto_trading_enabled = True
        db.commit()
    
    return ControlResponse(
        success=True,
        message="🤖 Trading automatique démarré",
        status=get_trading_status(db)
    )


@router.post("/stop", response_model=ControlResponse)
async def stop_trading(db: Session = Depends(get_db)):
    """Stop the autonomous trading engine"""
    engine = get_auto_trading_engine()
    engine.stop()
    
    # Disable auto-trading in config
    config = db.query(ScannerConfig).first()
    if config:
        config.auto_trading_enabled = False
        db.commit()
    
    return ControlResponse(
        success=True,
        message="🛑 Trading automatique arrêté",
        status=get_trading_status(db)
    )


@router.post("/pause", response_model=ControlResponse)
async def pause_trading(db: Session = Depends(get_db)):
    """Pause trading (no new positions, still monitors)"""
    engine = get_auto_trading_engine()
    engine.pause()
    
    return ControlResponse(
        success=True,
        message="⏸️ Trading en pause (monitoring actif)",
        status=get_trading_status(db)
    )


@router.post("/resume", response_model=ControlResponse)
async def resume_trading(db: Session = Depends(get_db)):
    """Resume trading after pause"""
    engine = get_auto_trading_engine()
    engine.resume()
    
    return ControlResponse(
        success=True,
        message="▶️ Trading repris",
        status=get_trading_status(db)
    )


@router.post("/panic", response_model=PanicResponse)
async def panic_close_all(db: Session = Depends(get_db)):
    """
    🚨 PANIC BUTTON: Close ALL active positions immediately
    Use only in emergency!
    """
    engine = get_auto_trading_engine()
    
    # Stop trading first
    engine.stop()
    
    # Disable auto-trading
    config = db.query(ScannerConfig).first()
    if config:
        config.auto_trading_enabled = False
    
    # Close all positions
    closed_count = await engine.panic_close_all(db)
    
    db.commit()
    
    return PanicResponse(
        success=True,
        positions_closed=closed_count,
        message=f"🚨 PANIC: {closed_count} positions fermées, trading désactivé"
    )


@router.post("/close/{position_id}")
async def close_single_position(
    position_id: int,
    db: Session = Depends(get_db)
):
    """Manually close a single position"""
    position = db.query(Position).filter(Position.id == position_id).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    
    if position.status != PositionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Position is not active")
    
    engine = get_auto_trading_engine()
    await engine._close_position(db, position, reason="MANUAL CLOSE")
    db.commit()
    
    return {
        "success": True,
        "message": f"Position {position_id} fermée manuellement",
        "pnl": position.pnl,
        "pnl_percent": position.pnl_percent
    }
