"""
Advanced Polymarket Scanner with Parallel Processing
Scans markets in parallel with advanced multi-criteria scoring.
"""
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from backend.services.polymarket_client import get_polymarket_client, PolymarketClient
from backend.services.polymarket_websocket import PolymarketWebSocketClient
from backend.services.notification import get_notification_service

logger = logging.getLogger(__name__)


@dataclass
class ScanConfig:
    """Scanner configuration"""
    min_score: int = 0
    min_volume: float = 0.0
    min_liquidity: float = 0.0
    max_hours_to_resolution: int = 8760  # 365 days
    max_concurrent_scans: int = 20
    scan_interval_seconds: int = 30


@dataclass
class OpportunityScore:
    """Detailed scoring breakdown"""
    market_id: str
    market_name: str
    
    # Prices
    price_yes: float
    price_no: float
    
    # Score components (0-10 each)
    divergence_score: float  # 40% weight
    volume_score: float      # 20% weight
    liquidity_score: float   # 20% weight
    timing_score: float      # 10% weight
    activity_score: float    # 10% weight
    
    # Final score (1-10)
    total_score: int
    
    # Metadata
    volume_24h: float
    liquidity: float
    hours_to_resolution: Optional[float]
    analyzed_at: datetime


class AdvancedScanner:
    """
    Advanced parallel market scanner with multi-criteria scoring.
    
    Scoring weights:
    - Divergence from equilibrium: 40%
    - 24h Volume: 20%
    - Orderbook liquidity: 20%
    - Time to resolution: 10%
    - Recent activity: 10%
    """
    
    def __init__(self, config: Optional[ScanConfig] = None):
        self.config = config or ScanConfig()
        self.client: Optional[PolymarketClient] = None
        self._cache: Dict[str, Tuple[datetime, any]] = {}
        self._cache_ttl = 60  # seconds
        
        # Sniper Mode
        from backend.config import settings
        self.sniper_mode = settings.enable_sniper_mode
        self.ws_client: Optional[PolymarketWebSocketClient] = None
        self.subscribed_markets: Set[str] = set()
        
    async def initialize(self):
        """Initialize the scanner"""
        self.client = get_polymarket_client()
        
        if self.sniper_mode:
            logger.info("Sniper Mode ENABLED: Initializing WebSocket...")
            self.ws_client = PolymarketWebSocketClient(callback=self._handle_ws_update)
            await self.ws_client.connect()
            
        logger.info("Advanced scanner initialized")
    
    async def close(self):
        """Cleanup resources"""
        if self.client:
            await self.client.close()
        if self.ws_client:
            await self.ws_client.close()

    async def _handle_ws_update(self, data: Dict):
        """Handle real-time updates from WebSocket"""
        try:
            # Polymarket WS format is typically: [{"event_type": "book", "market": "...", "data": ...}]
            # Implementation needs to parse this and update local state/trigger alerts
            # For this MVP, we will log "Sniper Hit" if score is high
            # In production, this would update a local orderbook and re-run scoring instantly
            
            # Simplified parsing to detect activity
            event_type = data.get("event_type")
            if event_type == "book":
                # Market ID is often in "market" field or implied by subscription
                market_id = data.get("market")
                if market_id:
                    # logger.debug(f"Sniper update: {market_id}")
                    # Trigger analysis? 
                    # Ideally we don't do full analysis on every tick, but check spreads
                    pass

        except Exception as e:
            logger.error(f"Error handling WS update: {e}")
    
    # ==================== CACHE ====================
    
    # ==================== CACHE ====================
    
    def _get_cached(self, key: str) -> Optional[any]:
        """Get cached value if not expired"""
        if key in self._cache:
            cached_time, value = self._cache[key]
            if datetime.now() - cached_time < timedelta(seconds=self._cache_ttl):
                return value
        return None
    
    def _set_cached(self, key: str, value: any):
        """Set cached value"""
        self._cache[key] = (datetime.now(), value)
    
    # ==================== PARALLEL SCANNING ====================
    
    async def scan_all_markets(self, limit: int = 100) -> List[OpportunityScore]:
        """
        Scan all markets in parallel
        
        Args:
            limit: Maximum markets to scan
            
        Returns:
            List of scored opportunities, sorted by score
        """
        if not self.client:
            await self.initialize()
        
        start_time = datetime.now()
        logger.info(f"Starting parallel scan of {limit} markets...")
        
        # Fetch markets
        markets = await self.client.get_markets(limit=limit, active_only=True)
        
        if not markets:
            logger.warning("No markets returned")
            return []
        
        # Scan markets in parallel with semaphore
        semaphore = asyncio.Semaphore(self.config.max_concurrent_scans)
        
        async def scan_with_semaphore(market):
            async with semaphore:
                return await self._analyze_market(market)
        
        # Execute all scans in parallel
        tasks = [scan_with_semaphore(m) for m in markets]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid results
        opportunities = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Scan error: {result}")
                continue
            
            # Log the result for debugging
            if result:
                logger.info(f"Market analysis result: {result.market_id} - Score: {result.total_score}")
            else:
                logger.info(f"Market analysis returned None for task {i}")

            if result and result.total_score >= self.config.min_score:
                opportunities.append(result)
        
        # Sort by score descending
        opportunities.sort(key=lambda x: x.total_score, reverse=True)
        
        # Notify for top opportunities
        from backend.config import settings
        notification_service = get_notification_service()
        for opp in opportunities:
            if opp.total_score >= settings.discord_notify_min_score:
                # Fire and forget (or await if simple)
                # To avoid blocking scan too much, we launch task or just await (it's fast HTTP)
                # For safety in this loop, we await
                await notification_service.notify_opportunity(opp)

        # Sniper Mode: Subscribe to top opportunities
        if self.sniper_mode and self.ws_client:
            await self._subscribe_to_hot_markets(opportunities)

        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Scan complete: {len(opportunities)} opportunities in {elapsed:.2f}s")
        
        return opportunities
    
    async def _subscribe_to_hot_markets(self, opportunities: List[OpportunityScore]):
        """Subscribe to top markets for real-time updates"""
        from backend.config import settings
        max_subs = settings.sniper_max_subscriptions
        
        # Get top N markets
        targets = opportunities[:max_subs]
        new_ids = []
        
        for opp in targets:
            # We need token IDs for subscription, not just market ID
            # In a full impl, we'd cache these during analysis
            # For now, we'll optimistically subscribe if we have the ID,
            # assuming the WS takes market IDs or we fetched tokens
            
            # The WS `book` channel often takes Token IDs, not Condition IDs.
            # We need to ensure we have the token IDs.
            # In `_analyze_market`, we have access to tokens. 
            # We should probably store token IDs in OpportunityScore.
            pass
            
        # Placeholder for subscription logic once Token IDs are propagated
        # logger.info(f"Sniper: Would subscribe to {len(targets)} markets")
    
    
    async def _analyze_market(self, market: Dict) -> Optional[OpportunityScore]:
        """
        Analyze a single market with multi-criteria scoring
        
        Args:
            market: Market data from API
            
        Returns:
            OpportunityScore or None if analysis fails
        """
        try:
            market_id = market.get("id", "")
            logger.info(f"Analyzing market: {market_id}")
            # DEBUG: Dump keys to understand why tokens is empty
            logger.info(f"Market keys: {market.keys()}")
            
            # Check cache
            cached = self._get_cached(f"analysis_{market_id}")
            if cached:
                return cached
            
            tokens = market.get("tokens", [])
            
            # Fallback for Gamma API format which uses clobTokenIds
            if not tokens and "clobTokenIds" in market:
                clob_ids = json.loads(market["clobTokenIds"]) if isinstance(market["clobTokenIds"], str) else market["clobTokenIds"]
                if clob_ids and len(clob_ids) >= 2:
                    # Construct pseudo token objects
                    tokens = [
                        {"token_id": clob_ids[0], "outcome": "YES"}, # Assumption: Order usually matches outcomes
                        {"token_id": clob_ids[1], "outcome": "NO"}
                    ]
            
            if len(tokens) < 2:
                # logger.warning(f"Market {market_id} skipped: Not enough tokens ({len(tokens)})")
                return None
            
            # Get prices in parallel
            token_yes = tokens[0].get("token_id", "")
            token_no = tokens[1].get("token_id", "")
            
            if not token_yes or not token_no:
                logger.warning(f"Market {market_id} skipped: Missing token IDs")
                return None
            
            # logger.info(f"Market {market_id}: Fetching prices for {token_yes}, {token_no}")

            # Initialize defaults
            price_yes = 0.5
            price_no = 0.5
            ask_yes = 1.0
            ask_no = 1.0
            
            # Fetch orderbooks
            book_yes_res, book_no_res = await asyncio.gather(
                self.client.get_orderbook(token_yes),
                self.client.get_orderbook(token_no),
                return_exceptions=True
            )
            
            if isinstance(book_yes_res, dict) and book_yes_res.get("asks"):
                 ask_yes = float(book_yes_res["asks"][0]["price"])
                 price_yes = ask_yes # Use ask as price proxy if available
            elif isinstance(book_yes_res, Exception) or not book_yes_res:
                 # If orderbook fails, try midpoint or just default
                 pass 
                 
            if isinstance(book_no_res, dict) and book_no_res.get("asks"):
                 ask_no = float(book_no_res["asks"][0]["price"])
                 price_no = ask_no
            
            # If we have NO valid pricing data at all (both 1.0), skip or score 0
            if ask_yes == 1.0 and ask_no == 1.0:
                 # Check if we can get last trade price from market metadata?
                 pass


            # Calculate STRICT scores based on Ask (Execution Price)
            # Opportunity = 1.0 - (AskYes + AskNo)
            # If positive, we have profit (before fees)
            
            # Divergence Score (40%)
            real_cost = ask_yes + ask_no
            divergence_score = self._calc_divergence_score(ask_yes, ask_no)
            
            # If real_cost > 1.0, divergence score should practically be 0 for 'Profitability'
            # But we might show it as 1 to indicate 'analyzed'
            if real_cost >= 1.0:
                divergence_score = 0
            
            # Use Ask for display prices to be honest
            display_price_yes = ask_yes
            display_price_no = ask_no

            volume_score = self._calc_volume_score(market)
            liquidity_score = self._calc_liquidity_score(book_yes_res if isinstance(book_yes_res, dict) else None)
            timing_score = self._calc_timing_score(market)
            activity_score = self._calc_activity_score(market)
            
            # weighted total
            total = (
                divergence_score * 0.50 + # Increased weight for profit
                volume_score * 0.15 +
                liquidity_score * 0.15 +
                timing_score * 0.10 +
                activity_score * 0.10
            )
            
            # Bonus: If profitable after fee (est 2%), boost to 10
            if real_cost < 0.98:
                total = 10
            
            total_score = min(10, max(1, int(total)))
            
            result = OpportunityScore(
                market_id=market_id,
                market_name=market.get("question", "Unknown"),
                price_yes=display_price_yes,
                price_no=display_price_no,
                divergence_score=divergence_score,
                volume_score=volume_score,
                liquidity_score=liquidity_score,
                timing_score=timing_score,
                activity_score=activity_score,
                total_score=total_score,
                volume_24h=float(market.get("volume24hr", 0) or 0),
                liquidity=float(market.get("liquidity", 0) or 0),
                hours_to_resolution=self._calc_hours_to_resolution(market),
                analyzed_at=datetime.now()
            )
            
            # Cache result
            self._set_cached(f"analysis_{market_id}", result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing market {market_id}: {e}", exc_info=True)
            return None
    
    # ==================== SCORING FUNCTIONS ====================
    
    def _calc_divergence_score(self, price_yes: float, price_no: float) -> float:
        """
        Calculate divergence score (0-10)
        Higher divergence from equilibrium = higher score
        Equilibrium: YES + NO = 1.0
        """
        total = price_yes + price_no
        divergence = abs(1.0 - total)
        
        # Map divergence to score
        # 0% divergence = 0, 5%+ divergence = 10
        score = min(10, divergence * 200)
        return score
    
    def _calc_volume_score(self, market: Dict) -> float:
        """
        Calculate volume score (0-10)
        Higher 24h volume = higher score
        """
        volume = float(market.get("volume24hr", 0) or 0)
        
        # Check minimum
        if volume < self.config.min_volume:
            return 0
        
        # Map volume to score
        # $1k = 2, $10k = 5, $100k+ = 10
        if volume >= 100000:
            return 10
        elif volume >= 50000:
            return 8
        elif volume >= 20000:
            return 6
        elif volume >= 10000:
            return 5
        elif volume >= 5000:
            return 4
        elif volume >= 2000:
            return 3
        else:
            return 2
    
    def _calc_liquidity_score(self, orderbook: Optional[Dict]) -> float:
        """
        Calculate liquidity score (0-10)
        Better orderbook depth = higher score
        """
        if not orderbook:
            return 5  # Neutral if no data
        
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])
        
        # Calculate total depth
        bid_depth = sum(float(b.get("size", 0)) for b in bids[:5])
        ask_depth = sum(float(a.get("size", 0)) for a in asks[:5])
        total_depth = bid_depth + ask_depth
        
        if total_depth < self.config.min_liquidity:
            return 0
        
        # Map depth to score
        if total_depth >= 10000:
            return 10
        elif total_depth >= 5000:
            return 8
        elif total_depth >= 2000:
            return 6
        elif total_depth >= 1000:
            return 5
        else:
            return 3
    
    def _calc_timing_score(self, market: Dict) -> float:
        """
        Calculate timing score (0-10)
        Sweet spot: 1-7 days to resolution
        Too soon or too far = lower score
        """
        hours = self._calc_hours_to_resolution(market)
        
        if hours is None:
            return 5  # Neutral if no data
        
        # Sweet spot is 24-168 hours (1-7 days)
        if 24 <= hours <= 168:
            return 10
        elif 12 <= hours < 24:
            return 7
        elif 168 < hours <= 336:
            return 6
        elif hours < 12:
            return 3  # Too soon, risky
        else:
            return 4  # Too far
    
    def _calc_activity_score(self, market: Dict) -> float:
        """
        Calculate activity score (0-10)
        Recent trades/activity = higher score
        """
        # Use volume as proxy for activity
        volume = float(market.get("volume24hr", 0) or 0)
        
        if volume > 50000:
            return 10
        elif volume > 20000:
            return 8
        elif volume > 10000:
            return 6
        elif volume > 5000:
            return 5
        elif volume > 1000:
            return 3
        else:
            return 1
    
    def _calc_hours_to_resolution(self, market: Dict) -> Optional[float]:
        """Calculate hours until market resolution"""
        end_date = market.get("endDate") or market.get("end_date_iso")
        
        if not end_date:
            return None
        
        try:
            if isinstance(end_date, str):
                # Parse ISO date
                end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            else:
                end_dt = datetime.fromtimestamp(end_date)
            
            delta = end_dt - datetime.now(end_dt.tzinfo)
            return delta.total_seconds() / 3600
        except:
            return None


# Singleton instance
_scanner: Optional[AdvancedScanner] = None


def get_advanced_scanner(config: Optional[ScanConfig] = None) -> AdvancedScanner:
    """Get or create advanced scanner instance"""
    global _scanner
    if _scanner is None:
        _scanner = AdvancedScanner(config)
    return _scanner
