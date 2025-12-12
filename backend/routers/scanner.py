"""
Advanced Scanner API Router
Endpoints for advanced market scanning and opportunities.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.database import get_db
from backend.services.advanced_scanner import get_advanced_scanner, ScanConfig
from backend.models.scanner_config import ScannerConfig
from backend.models.opportunity import Opportunity

router = APIRouter(prefix="/api/scanner", tags=["scanner"])


# ==================== SCHEMAS ====================

class OpportunityScoreResponse(BaseModel):
    market_id: str
    market_name: str
    price_yes: float
    price_no: float
    divergence_score: float
    volume_score: float
    liquidity_score: float
    timing_score: float
    activity_score: float
    total_score: int
    volume_24h: float
    liquidity: float
    hours_to_resolution: Optional[float]
    analyzed_at: datetime


class ScanResultResponse(BaseModel):
    scanned_count: int
    opportunities_found: int
    scan_duration_seconds: float
    opportunities: List[OpportunityScoreResponse]


class ScannerConfigResponse(BaseModel):
    auto_trading_enabled: bool
    scan_interval_seconds: int
    max_markets_per_scan: int
    min_score_to_trade: int
    min_score_to_show: int
    min_volume_24h: float
    min_liquidity: float
    max_active_positions: int
    max_capital_per_trade: float
    max_total_capital: float
    default_ratio_yes: int
    default_ratio_no: int
    stop_loss_percent: float
    take_profit_percent: float


class UpdateConfigRequest(BaseModel):
    auto_trading_enabled: Optional[bool] = None
    scan_interval_seconds: Optional[int] = None
    min_score_to_trade: Optional[int] = None
    min_score_to_show: Optional[int] = None
    min_volume_24h: Optional[float] = None
    min_liquidity: Optional[float] = None
    max_active_positions: Optional[int] = None
    max_capital_per_trade: Optional[float] = None
    stop_loss_percent: Optional[float] = None
    take_profit_percent: Optional[float] = None
    default_ratio_yes: Optional[int] = None
    default_ratio_no: Optional[int] = None


# ==================== HELPERS ====================

def get_or_create_config(db: Session) -> ScannerConfig:
    """Get or create scanner configuration"""
    config = db.query(ScannerConfig).first()
    if not config:
        config = ScannerConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


# ==================== ENDPOINTS ====================

@router.get("/opportunities", response_model=List[OpportunityScoreResponse])
async def get_opportunities(
    min_score: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get current opportunities from database"""
    opportunities = (
        db.query(Opportunity)
        .filter(Opportunity.is_active == True)
        .filter(Opportunity.score >= min_score)
        .order_by(Opportunity.score.desc())
        .limit(limit)
        .all()
    )
    
    return [
        OpportunityScoreResponse(
            market_id=o.market_id,
            market_name=o.market_name,
            price_yes=o.price_yes,
            price_no=o.price_no,
            divergence_score=0,  # Not stored in basic model
            volume_score=0,
            liquidity_score=0,
            timing_score=0,
            activity_score=0,
            total_score=o.score,
            volume_24h=o.volume_24h or 0,
            liquidity=o.liquidity or 0,
            hours_to_resolution=None,
            analyzed_at=o.detected_at
        )
        for o in opportunities
    ]


@router.post("/scan", response_model=ScanResultResponse)
async def trigger_advanced_scan(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Trigger an advanced parallel market scan.
    Returns scored opportunities.
    """
    start_time = datetime.now()
    
    # Get scanner config
    config = get_or_create_config(db)
    
    # Create scanner with config
    scan_config = ScanConfig(
        min_score=config.min_score_to_show,
        min_volume=config.min_volume_24h,
        min_liquidity=config.min_liquidity
    )
    
    scanner = get_advanced_scanner(scan_config)
    
    # Run scan
    opportunities = await scanner.scan_all_markets(limit=limit)
    
    # Save to database
    for opp in opportunities:
        existing = db.query(Opportunity).filter(
            Opportunity.market_id == opp.market_id,
            Opportunity.is_active == True
        ).first()
        
        if existing:
            existing.price_yes = opp.price_yes
            existing.price_no = opp.price_no
            existing.score = opp.total_score
            existing.volume_24h = opp.volume_24h
            existing.liquidity = opp.liquidity
        else:
            new_opp = Opportunity(
                market_id=opp.market_id,
                market_name=opp.market_name,
                price_yes=opp.price_yes,
                price_no=opp.price_no,
                divergence=abs(1.0 - opp.price_yes - opp.price_no),
                score=opp.total_score,
                volume_24h=opp.volume_24h,
                liquidity=opp.liquidity,
                is_active=True,
                is_traded=False
            )
            db.add(new_opp)
    
    db.commit()
    
    duration = (datetime.now() - start_time).total_seconds()
    
    return ScanResultResponse(
        scanned_count=limit,
        opportunities_found=len(opportunities),
        scan_duration_seconds=duration,
        opportunities=[
            OpportunityScoreResponse(
                market_id=o.market_id,
                market_name=o.market_name,
                price_yes=o.price_yes,
                price_no=o.price_no,
                divergence_score=o.divergence_score,
                volume_score=o.volume_score,
                liquidity_score=o.liquidity_score,
                timing_score=o.timing_score,
                activity_score=o.activity_score,
                total_score=o.total_score,
                volume_24h=o.volume_24h,
                liquidity=o.liquidity,
                hours_to_resolution=o.hours_to_resolution,
                analyzed_at=o.analyzed_at
            )
            for o in opportunities
        ]
    )


@router.get("/config", response_model=ScannerConfigResponse)
async def get_scanner_config(db: Session = Depends(get_db)):
    """Get current scanner configuration"""
    config = get_or_create_config(db)
    return config.to_dict()


@router.put("/config", response_model=ScannerConfigResponse)
async def update_scanner_config(
    updates: UpdateConfigRequest,
    db: Session = Depends(get_db)
):
    """Update scanner configuration"""
    config = get_or_create_config(db)
    
    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    
    return config.to_dict()


@router.post("/toggle-auto-trading")
async def toggle_auto_trading(
    enabled: bool,
    db: Session = Depends(get_db)
):
    """Toggle automatic trading on/off"""
    config = get_or_create_config(db)
    config.auto_trading_enabled = enabled
    db.commit()
    
    return {
        "auto_trading_enabled": enabled,
        "message": "Trading automatique " + ("activé" if enabled else "désactivé")
    }
