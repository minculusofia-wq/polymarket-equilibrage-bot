"""
Autonomous Trading Engine
Handles automatic trading: detection → entry → monitoring → exit
"""
import asyncio
import logging
from typing import Optional, List, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from backend.services.polymarket_client import get_polymarket_client
from backend.services.advanced_scanner import get_advanced_scanner, OpportunityScore
from backend.models.position import Position, PositionStatus, PositionSide
from backend.models.trade import Trade, TradeType, TradeSide
from backend.models.opportunity import Opportunity
from backend.models.scanner_config import ScannerConfig
from backend.services.websocket_manager import get_ws_manager

logger = logging.getLogger(__name__)


class AutoTradingEngine:
    """
    Autonomous trading engine that:
    1. Scans markets continuously
    2. Auto-enters positions when opportunities meet thresholds
    3. Monitors positions for SL/TP
    4. Auto-exits when conditions are met
    """
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.is_running = False
        self.is_paused = False
        self._task: Optional[asyncio.Task] = None
        self.client = get_polymarket_client()
        self.scanner = get_advanced_scanner()
        self.ws_manager = get_ws_manager()
        
    # ==================== CONTROL ====================
    
    def start(self):
        """Start the autonomous trading loop"""
        if self.is_running:
            logger.warning("Trading engine already running")
            return
        
        self.is_running = True
        self.is_paused = False
        self._task = asyncio.create_task(self._trading_loop())
        logger.info("🤖 Autonomous trading engine STARTED")
        asyncio.create_task(self.ws_manager.broadcast({
            "type": "TRADING_STATUS",
            "data": {"is_running": True, "is_paused": False}
        }))
    
    def stop(self):
        """Stop the autonomous trading loop"""
        self.is_running = False
        if self._task:
            self._task.cancel()
        logger.info("🛑 Autonomous trading engine STOPPED")
        asyncio.create_task(self.ws_manager.broadcast({
            "type": "TRADING_STATUS",
            "data": {"is_running": False, "is_paused": False}
        }))
    
    def pause(self):
        """Pause trading (still monitors, but no new trades)"""
        self.is_paused = True
        logger.info("⏸️ Trading PAUSED")
        asyncio.create_task(self.ws_manager.broadcast({
            "type": "TRADING_STATUS",
            "data": {"is_running": True, "is_paused": True}
        }))
    
    def resume(self):
        """Resume trading"""
        self.is_paused = False
        logger.info("▶️ Trading RESUMED")
        asyncio.create_task(self.ws_manager.broadcast({
            "type": "TRADING_STATUS",
            "data": {"is_running": True, "is_paused": False}
        }))
    
    async def panic_close_all(self, db: Session) -> int:
        """
        PANIC BUTTON: Close all active positions immediately
        
        Returns:
            Number of positions closed
        """
        logger.warning("🚨 PANIC CLOSE ALL triggered!")
        
        active_positions = db.query(Position).filter(
            Position.status == PositionStatus.ACTIVE
        ).all()
        
        closed_count = 0
        for position in active_positions:
            await self._close_position(db, position, reason="PANIC CLOSE")
            closed_count += 1
        
        logger.warning(f"🚨 Closed {closed_count} positions")
        return closed_count
    
    # ==================== MAIN LOOP ====================
    
    async def _trading_loop(self):
        """Main autonomous trading loop"""
        logger.info("Trading loop started")
        
        while self.is_running:
            try:
                db = self.db_session_factory()
                
                try:
                    config = self._get_config(db)
                    
                    # Only trade if auto-trading is enabled
                    if config.auto_trading_enabled and not self.is_paused:
                        # 1. Scan for opportunities
                        await self._scan_and_trade(db, config)
                    
                    # 2. Always monitor existing positions (even if paused)
                    await self._monitor_positions(db, config)
                    
                    # Store interval for sleep outside session
                    scan_interval = config.scan_interval_seconds
                    
                finally:
                    db.close()
                
                # Wait before next iteration
                await asyncio.sleep(scan_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(10)  # Wait before retry
        
        logger.info("Trading loop ended")
    
    # ==================== SCANNING & ENTRY ====================
    
    async def _scan_and_trade(self, db: Session, config: ScannerConfig):
        """Scan markets and auto-enter if conditions met"""
        
        # Check if we can take more positions
        active_count = db.query(Position).filter(
            Position.status == PositionStatus.ACTIVE
        ).count()
        
        if active_count >= config.max_active_positions:
            logger.debug(f"Max positions reached ({active_count}/{config.max_active_positions})")
            return
        
        # Scan markets
        opportunities = await self.scanner.scan_all_markets(
            limit=config.max_markets_per_scan
        )
        
        # Filter by trading threshold
        tradeable = [
            o for o in opportunities 
            if o.total_score >= config.min_score_to_trade
            and not self._is_already_trading(db, o.market_id)
        ]
        
        # Broadcast opportunities
        if opportunities:
            top_opps = [
                {
                    "market_id": o.market_id,
                    "market_name": o.market_name,
                    "total_score": o.total_score,
                    "price_yes": o.price_yes,
                    "price_no": o.price_no
                }
                for o in opportunities[:5]
            ]
            await self.ws_manager.broadcast({
                "type": "SCAN_COMPLETE",
                "data": {
                    "count": len(opportunities),
                    "top_opportunities": top_opps
                }
            })
        
        if not tradeable:
            return
        
        # Take the best opportunity
        best = tradeable[0]
        logger.info(f"🎯 Auto-trading opportunity: {best.market_name} (score: {best.total_score})")
        
        await self._enter_position(db, best, config)
    
    def _is_already_trading(self, db: Session, market_id: str) -> bool:
        """Check if we already have a position in this market"""
        return db.query(Position).filter(
            Position.market_id == market_id,
            Position.status == PositionStatus.ACTIVE
        ).count() > 0
    
    async def _enter_position(
        self, 
        db: Session, 
        opportunity: OpportunityScore, 
        config: ScannerConfig
    ):
        """Enter a new position automatically"""
        
        # Calculate amounts
        capital = min(config.max_capital_per_trade, config.max_total_capital)
        ratio_yes = config.default_ratio_yes / 100
        ratio_no = config.default_ratio_no / 100
        
        amount_yes = capital * ratio_yes
        amount_no = capital * ratio_no
        
        # Fetch market details to get token IDs
        market = await self.client.get_market(opportunity.market_id)
        if not market:
            logger.error(f"Could not fetch market details for {opportunity.market_id}")
            return

        tokens = market.get("tokens", [])
        if len(tokens) < 2:
            logger.error(f"Market {opportunity.market_id} has insufficient tokens")
            return

        token_yes_id = tokens[0].get("token_id")
        token_no_id = tokens[1].get("token_id")

        if not token_yes_id or not token_no_id:
            logger.error("Could not find token IDs")
            return

        # 1. EXECUTE REAL TRADES (YES + NO)
        logger.info(f"🚀 Executing REAL trade for {opportunity.market_name}...")
        
        # Buy YES
        order_yes = await self.client.place_order(
            token_id=token_yes_id,
            side="BUY",
            size=amount_yes,
            price=opportunity.price_yes
        )
        
        # Buy NO
        order_no = await self.client.place_order(
            token_id=token_no_id,
            side="BUY",
            size=amount_no,
            price=opportunity.price_no
        )

        # STRICT CHECK: If orders failed (e.g. no private key), DO NOT CREATE POSITION
        if not order_yes and not order_no:
            logger.error("❌ Trade failed: Could not place orders (Missing Private Key? Check .env)")
            return

        # If partial success, we still track what we got (logic could be refined)
        real_amount_yes = amount_yes if order_yes else 0
        real_amount_no = amount_no if order_no else 0

        # Create position in DB only for successful trades
        position = Position(
            market_id=opportunity.market_id,
            market_name=opportunity.market_name,
            entry_price_yes=opportunity.price_yes,
            entry_price_no=opportunity.price_no,
            amount_yes=real_amount_yes,
            amount_no=real_amount_no,
            current_price_yes=opportunity.price_yes,
            current_price_no=opportunity.price_no,
            current_value_yes=real_amount_yes,
            current_value_no=real_amount_no,
            pnl=0.0,
            pnl_percent=0.0,
            status=PositionStatus.ACTIVE,
            active_side=PositionSide.BOTH
        )
        
        db.add(position)
        db.commit()
        db.refresh(position)
        
        # Record entry trades
        if real_amount_yes > 0:
            self._record_trade(db, position, TradeSide.YES, TradeType.ENTRY, 
                            real_amount_yes, opportunity.price_yes)
        if real_amount_no > 0:
            self._record_trade(db, position, TradeSide.NO, TradeType.ENTRY,
                            real_amount_no, opportunity.price_no)
        
        # Mark opportunity as traded
        opp_record = db.query(Opportunity).filter(
            Opportunity.market_id == opportunity.market_id
        ).first()
        if opp_record:
            opp_record.is_traded = True
        
        db.commit()
        
        logger.info(f"✅ Position opened: {position.id} on {opportunity.market_name}")
        
        # Broadcast new position
        await self.ws_manager.broadcast({
            "type": "POSITION_OPENED",
            "data": {
                "id": position.id,
                "market_name": position.market_name,
                "amount": real_amount_yes + real_amount_no
            }
        })
    
    # ==================== MONITORING & EXIT ====================
    
    async def _monitor_positions(self, db: Session, config: ScannerConfig):
        """Monitor all active positions and apply SL/TP"""
        
        active_positions = db.query(Position).filter(
            Position.status == PositionStatus.ACTIVE
        ).all()
        
        for position in active_positions:
            await self._update_position_prices(db, position)
            
            # ==========================================
            # STRATEGY 1: GLOBAL P&L (Legacy)
            # ==========================================
            if config.exit_model == "GLOBAL":
                # Check Stop Loss
                if position.pnl_percent <= -config.stop_loss_percent:
                    logger.warning(f"📉 Stop Loss triggered for {position.id}: {position.pnl_percent:.2f}%")
                    await self._close_position(db, position, reason="STOP LOSS")
                    continue
                
                # Check Take Profit
                if position.pnl_percent >= config.take_profit_percent:
                    logger.info(f"📈 Take Profit triggered for {position.id}: {position.pnl_percent:.2f}%")
                    await self._close_position(db, position, reason="TAKE PROFIT")
                    continue

            # ==========================================
            # STRATEGY 2: INDEPENDENT LEGS (Smart Exit)
            # ==========================================
            elif config.exit_model == "INDEPENDENT":
                # Check YES Leg
                if not position.is_yes_closed:
                    # Stop Loss (Drawdown)
                    if position.current_price_yes < (position.entry_price_yes * (1 - (config.leg_stop_loss_percent / 100))):
                        logger.warning(f"📉 Cutting YES loser on {position.market_name}")
                        await self._close_leg(db, position, TradeSide.YES, reason="UGLY LEG CUT")
                    
                    # Take Profit (Target Price)
                    elif position.current_price_yes >= config.leg_take_profit_price:
                        logger.info(f"🚀 Taking YES profit on {position.market_name}")
                        await self._close_leg(db, position, TradeSide.YES, reason="MOON LEG TAKEN")

                # Check NO Leg
                if not position.is_no_closed:
                    # Stop Loss (Drawdown)
                    if position.current_price_no < (position.entry_price_no * (1 - (config.leg_stop_loss_percent / 100))):
                        logger.warning(f"📉 Cutting NO loser on {position.market_name}")
                        await self._close_leg(db, position, TradeSide.NO, reason="UGLY LEG CUT")
                    
                    # Take Profit (Target Price)
                    elif position.current_price_no >= config.leg_take_profit_price:
                        logger.info(f"🚀 Taking NO profit on {position.market_name}")
                        await self._close_leg(db, position, TradeSide.NO, reason="MOON LEG TAKEN")
                
                # Close position if both legs are gone
                if position.is_yes_closed and position.is_no_closed:
                     position.status = PositionStatus.CLOSED
                     position.closed_at = datetime.utcnow()
                     logger.info(f"✅ Position {position.id} fully CLOSED (both legs exited)")
                     await self.ws_manager.broadcast({
                        "type": "POSITION_CLOSED",
                        "data": {"id": position.id, "market_name": position.market_name, "reason": "BOTH LEGS EXITED"}
                     })
            
            # TODO: Implement smart liquidation (sell loser, keep winner)
        
        db.commit()
    
    async def _update_position_prices(self, db: Session, position: Position):
        """Update position with current market prices"""
        try:
            market = await self.client.get_market(position.market_id)
            if not market:
                return
            
            tokens = market.get("tokens", [])
            if len(tokens) < 2:
                return
            
            price_yes = await self.client.get_midpoint_price(tokens[0].get("token_id", ""))
            price_no = await self.client.get_midpoint_price(tokens[1].get("token_id", ""))
            
            if price_yes and price_no:
                position.current_price_yes = price_yes
                position.current_price_no = price_no
                
                # Calculate current values
                if position.entry_price_yes > 0:
                    position.current_value_yes = position.amount_yes * (price_yes / position.entry_price_yes)
                if position.entry_price_no > 0:
                    position.current_value_no = position.amount_no * (price_no / position.entry_price_no)
                
                # Calculate P&L
                initial = position.amount_yes + position.amount_no
                current = (position.current_value_yes or 0) + (position.current_value_no or 0)
                
                position.pnl = current - initial
                position.pnl_percent = (position.pnl / initial * 100) if initial > 0 else 0
                position.updated_at = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Error updating position {position.id}: {e}")
    
    async def _close_position(self, db: Session, position: Position, reason: str = "MANUAL"):
        """Close a position completely"""
        logger.info(f"Closing position {position.id}: {reason}")
        
        # Record exit trades
        if position.current_value_yes and position.current_value_yes > 0:
            self._record_trade(db, position, TradeSide.YES, TradeType.EXIT,
                              position.amount_yes, position.current_price_yes or 0)
        
        if position.current_value_no and position.current_value_no > 0:
            self._record_trade(db, position, TradeSide.NO, TradeType.EXIT,
                              position.amount_no, position.current_price_no or 0)
        
        position.status = PositionStatus.CLOSED
        position.closed_at = datetime.utcnow()
        
        logger.info(f"Position {position.id} closed. P&L: ${position.pnl:.2f} ({position.pnl_percent:.2f}%)")
        
        # Broadcast closed
        await self.ws_manager.broadcast({
            "type": "POSITION_CLOSED",
            "data": {
                "id": position.id,
                "market_name": position.market_name,
                "pnl": position.pnl,
                "reason": reason
            }
        })
    
    # ==================== HELPERS ====================
    
    async def _close_leg(self, db: Session, position: Position, side: TradeSide, reason: str = "PARTIAL"):
        """Close a single leg of the position"""
        logger.info(f"Closing Leg {side} for position {position.id}: {reason}")
        
        token_id = ""
        amount = 0.0
        current_price = 0.0
        
        # Get data based on side
        try:
            market = await self.client.get_market(position.market_id)
            tokens = market.get("tokens", [])
            
            if side == TradeSide.YES:
                token_id = tokens[0].get("token_id")
                amount = position.amount_yes
                current_price = await self.client.get_midpoint_price(token_id) or position.current_price_yes
            else:
                token_id = tokens[1].get("token_id")
                amount = position.amount_no
                current_price = await self.client.get_midpoint_price(token_id) or position.current_price_no
                
            # Execute Sell
            # TODO: Integrate real order execution here when wallet is ready
            # For now, we simulate the 'Sell' logic on DB level if real order succeeds (or implies logic)
            # In Phase 5, we assume we might not have keys yet so we just mark it.
            
            # Record exit trade
            self._record_trade(db, position, side, TradeType.EXIT, amount, current_price)
            
            # Update Position State
            if side == TradeSide.YES:
                position.is_yes_closed = True
                position.active_side = PositionSide.NO if not position.is_no_closed else PositionSide.BOTH # Should ideally be NONE if closed
                position.amount_yes = 0 # Holdings are gone
                position.current_value_yes = 0
            else:
                position.is_no_closed = True
                position.active_side = PositionSide.YES if not position.is_yes_closed else PositionSide.BOTH
                position.amount_no = 0
                position.current_value_no = 0
                
            db.commit()
            
            await self.ws_manager.broadcast({
                "type": "LEG_CLOSED",
                "data": {
                    "id": position.id,
                    "side": side.value,
                    "reason": reason,
                    "price": current_price
                }
            })
            
        except Exception as e:
            logger.error(f"Error closing leg {side}: {e}")

    def _get_config(self, db: Session) -> ScannerConfig:
        """Get scanner configuration"""
        config = db.query(ScannerConfig).first()
        if not config:
            config = ScannerConfig()
            db.add(config)
            db.commit()
            db.refresh(config)
        return config
    
    def _record_trade(
        self,
        db: Session,
        position: Position,
        side: TradeSide,
        trade_type: TradeType,
        amount: float,
        price: float
    ):
        """Record a trade in the database"""
        trade = Trade(
            position_id=position.id,
            market_id=position.market_id,
            market_name=position.market_name,
            side=side,
            type=trade_type,
            amount=amount,
            price=price,
            total_value=amount * price
        )
        db.add(trade)


# Global engine instance
_engine: Optional[AutoTradingEngine] = None


def get_auto_trading_engine(db_session_factory=None) -> AutoTradingEngine:
    """Get or create auto trading engine"""
    global _engine
    if _engine is None:
        from backend.database import SessionLocal
        _engine = AutoTradingEngine(db_session_factory or SessionLocal)
    return _engine
