"""
Trading Engine Service
Handles position entry, monitoring, and liquidation.
"""
from typing import Optional, Dict, Tuple
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from backend.services.polymarket_client import get_polymarket_client
from backend.models.position import Position, PositionStatus, PositionSide
from backend.models.trade import Trade, TradeType, TradeSide
from backend.models.opportunity import Opportunity
from backend.config import settings

logger = logging.getLogger(__name__)


class TradingEngine:
    """Manages trading operations for equilibrage strategy"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = get_polymarket_client()
    
    def calculate_amounts(
        self,
        capital: float,
        ratio_yes: int = 50,
        ratio_no: int = 50
    ) -> Tuple[float, float]:
        """
        Calculate YES/NO amounts based on capital and ratios
        
        Args:
            capital: Total capital to allocate
            ratio_yes: Percentage for YES (0-100)
            ratio_no: Percentage for NO (0-100)
            
        Returns:
            Tuple of (amount_yes, amount_no)
        """
        total_ratio = ratio_yes + ratio_no
        if total_ratio == 0:
            return (0, 0)
        
        amount_yes = capital * (ratio_yes / total_ratio)
        amount_no = capital * (ratio_no / total_ratio)
        
        return (round(amount_yes, 2), round(amount_no, 2))
    
    async def enter_position(
        self,
        opportunity: Opportunity,
        capital: float,
        ratio_yes: int = 50,
        ratio_no: int = 50
    ) -> Optional[Position]:
        """
        Enter a new position based on opportunity
        
        Args:
            opportunity: The opportunity to trade
            capital: Capital to allocate
            ratio_yes: Percentage for YES
            ratio_no: Percentage for NO
            
        Returns:
            Created Position or None if failed
        """
        logger.info(f"Entering position for market: {opportunity.market_name}")
        
        # Calculate amounts
        amount_yes, amount_no = self.calculate_amounts(capital, ratio_yes, ratio_no)
        
        # Get current prices
        price_yes = opportunity.price_yes
        price_no = opportunity.price_no
        
        # Create position
        position = Position(
            market_id=opportunity.market_id,
            market_name=opportunity.market_name,
            entry_price_yes=price_yes,
            entry_price_no=price_no,
            amount_yes=amount_yes,
            amount_no=amount_no,
            current_price_yes=price_yes,
            current_price_no=price_no,
            current_value_yes=amount_yes,
            current_value_no=amount_no,
            pnl=0.0,
            pnl_percent=0.0,
            status=PositionStatus.ACTIVE,
            active_side=PositionSide.BOTH
        )
        
        try:
            self.db.add(position)
            self.db.commit()
            self.db.refresh(position)
            
            # Record entry trades
            if amount_yes > 0:
                self._record_trade(
                    position_id=position.id,
                    market_id=opportunity.market_id,
                    market_name=opportunity.market_name,
                    side=TradeSide.YES,
                    trade_type=TradeType.ENTRY,
                    amount=amount_yes,
                    price=price_yes
                )
            
            if amount_no > 0:
                self._record_trade(
                    position_id=position.id,
                    market_id=opportunity.market_id,
                    market_name=opportunity.market_name,
                    side=TradeSide.NO,
                    trade_type=TradeType.ENTRY,
                    amount=amount_no,
                    price=price_no
                )
            
            # Mark opportunity as traded
            opportunity.is_traded = True
            self.db.commit()
            
            logger.info(f"Position entered: {position.id} - YES: ${amount_yes} @ {price_yes}, NO: ${amount_no} @ {price_no}")
            return position
            
        except Exception as e:
            logger.error(f"Failed to enter position: {e}")
            self.db.rollback()
            return None
    
    def _record_trade(
        self,
        position_id: int,
        market_id: str,
        market_name: str,
        side: TradeSide,
        trade_type: TradeType,
        amount: float,
        price: float
    ) -> Trade:
        """Record a trade in the database"""
        trade = Trade(
            position_id=position_id,
            market_id=market_id,
            market_name=market_name,
            side=side,
            type=trade_type,
            amount=amount,
            price=price,
            total_value=amount * price
        )
        self.db.add(trade)
        self.db.commit()
        return trade
    
    async def update_position(self, position: Position) -> Position:
        """
        Update position with current prices and calculate P&L
        
        Args:
            position: Position to update
            
        Returns:
            Updated position
        """
        # Get market info to find token IDs
        market = await self.client.get_market(position.market_id)
        if not market:
            logger.warning(f"Could not fetch market {position.market_id}")
            return position
        
        tokens = market.get("tokens", [])
        if len(tokens) >= 2:
            # Fetch current prices
            price_yes = await self.client.get_midpoint_price(tokens[0].get("token_id", ""))
            price_no = await self.client.get_midpoint_price(tokens[1].get("token_id", ""))
            
            if price_yes and price_no:
                # Update current prices
                position.current_price_yes = price_yes
                position.current_price_no = price_no
                
                # Calculate current values based on active side
                if position.active_side in [PositionSide.BOTH, PositionSide.YES]:
                    position.current_value_yes = position.amount_yes * (price_yes / position.entry_price_yes) if position.entry_price_yes > 0 else 0
                
                if position.active_side in [PositionSide.BOTH, PositionSide.NO]:
                    position.current_value_no = position.amount_no * (price_no / position.entry_price_no) if position.entry_price_no > 0 else 0
                
                # Calculate P&L
                initial_value = position.amount_yes + position.amount_no
                current_value = (position.current_value_yes or 0) + (position.current_value_no or 0)
                
                position.pnl = current_value - initial_value
                position.pnl_percent = (position.pnl / initial_value * 100) if initial_value > 0 else 0
                
                position.updated_at = datetime.utcnow()
                self.db.commit()
        
        return position
    
    async def close_position(self, position: Position) -> Position:
        """
        Close a position completely
        
        Args:
            position: Position to close
            
        Returns:
            Closed position
        """
        logger.info(f"Closing position {position.id}")
        
        # Record exit trades
        if position.active_side in [PositionSide.BOTH, PositionSide.YES] and position.current_value_yes:
            self._record_trade(
                position_id=position.id,
                market_id=position.market_id,
                market_name=position.market_name,
                side=TradeSide.YES,
                trade_type=TradeType.EXIT,
                amount=position.amount_yes,
                price=position.current_price_yes or 0
            )
        
        if position.active_side in [PositionSide.BOTH, PositionSide.NO] and position.current_value_no:
            self._record_trade(
                position_id=position.id,
                market_id=position.market_id,
                market_name=position.market_name,
                side=TradeSide.NO,
                trade_type=TradeType.EXIT,
                amount=position.amount_no,
                price=position.current_price_no or 0
            )
        
        # Update position status
        position.status = PositionStatus.CLOSED
        position.closed_at = datetime.utcnow()
        self.db.commit()
        
        logger.info(f"Position {position.id} closed with P&L: ${position.pnl:.2f} ({position.pnl_percent:.2f}%)")
        return position
    
    def get_active_positions(self) -> list:
        """Get all active positions"""
        return (
            self.db.query(Position)
            .filter(Position.status == PositionStatus.ACTIVE)
            .order_by(Position.created_at.desc())
            .all()
        )
    
    def get_position(self, position_id: int) -> Optional[Position]:
        """Get position by ID"""
        return self.db.query(Position).filter(Position.id == position_id).first()


def get_trading_engine(db: Session) -> TradingEngine:
    """Get trading engine instance with database session"""
    return TradingEngine(db)
