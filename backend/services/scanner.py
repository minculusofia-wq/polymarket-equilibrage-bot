"""
Market Scanner Service
Scans Polymarket for equilibrage opportunities in real-time.
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from backend.services.polymarket_client import get_polymarket_client
from backend.models.opportunity import Opportunity
from backend.config import settings

logger = logging.getLogger(__name__)


class MarketScanner:
    """Scans Polymarket markets for equilibrage opportunities"""
    
    def __init__(self, db: Session):
        self.db = db
        self.client = get_polymarket_client()
        self.min_score = 1  # Minimum score to save opportunity
        
    async def scan_all_markets(self, limit: int = 50) -> List[Dict]:
        """
        Scan all active markets for opportunities
        
        Args:
            limit: Max markets to scan
            
        Returns:
            List of opportunities found
        """
        logger.info(f"Starting market scan (limit={limit})")
        
        # Fetch active markets
        markets = await self.client.get_markets(limit=limit, active_only=True)
        
        if not markets:
            logger.warning("No markets returned from Polymarket")
            return []
        
        opportunities = []
        
        # Analyze each market
        for market in markets:
            try:
                analysis = await self.client.analyze_market_opportunity(market)
                
                if analysis.get("score", 0) >= self.min_score:
                    # Save to database
                    opportunity = self._save_opportunity(analysis)
                    if opportunity:
                        opportunities.append(analysis)
                        
            except Exception as e:
                logger.error(f"Error analyzing market {market.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Scan complete: found {len(opportunities)} opportunities")
        return opportunities
    
    def _save_opportunity(self, analysis: Dict) -> Optional[Opportunity]:
        """
        Save opportunity to database
        
        Args:
            analysis: Analysis result from market analysis
            
        Returns:
            Saved Opportunity model
        """
        try:
            # Check if opportunity already exists
            existing = self.db.query(Opportunity).filter(
                Opportunity.market_id == analysis["market_id"],
                Opportunity.is_active == True
            ).first()
            
            if existing:
                # Update existing opportunity
                existing.price_yes = analysis["price_yes"]
                existing.price_no = analysis["price_no"]
                existing.divergence = analysis["divergence"]
                existing.score = analysis["score"]
                existing.updated_at = datetime.utcnow()
                self.db.commit()
                return existing
            else:
                # Create new opportunity
                opportunity = Opportunity(
                    market_id=analysis["market_id"],
                    market_name=analysis["market_name"],
                    price_yes=analysis["price_yes"],
                    price_no=analysis["price_no"],
                    divergence=analysis["divergence"],
                    score=analysis["score"],
                    is_active=True,
                    is_traded=False
                )
                self.db.add(opportunity)
                self.db.commit()
                self.db.refresh(opportunity)
                return opportunity
                
        except Exception as e:
            logger.error(f"Failed to save opportunity: {e}")
            self.db.rollback()
            return None
    
    def get_top_opportunities(self, limit: int = 10, min_score: int = 5) -> List[Opportunity]:
        """
        Get top opportunities from database
        
        Args:
            limit: Max opportunities to return
            min_score: Minimum score filter
            
        Returns:
            List of Opportunity models
        """
        return (
            self.db.query(Opportunity)
            .filter(Opportunity.is_active == True)
            .filter(Opportunity.is_traded == False)
            .filter(Opportunity.score >= min_score)
            .order_by(Opportunity.score.desc())
            .limit(limit)
            .all()
        )
    
    def deactivate_old_opportunities(self, max_age_hours: int = 1):
        """
        Deactivate opportunities older than max_age_hours
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        self.db.query(Opportunity).filter(
            Opportunity.is_active == True,
            Opportunity.detected_at < cutoff
        ).update({"is_active": False})
        
        self.db.commit()


def get_scanner(db: Session) -> MarketScanner:
    """Get scanner instance with database session"""
    return MarketScanner(db)
