"""
Advanced Polymarket Scanner with Parallel Processing
Scans markets in parallel with advanced multi-criteria scoring.
"""
import asyncio
import logging
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import random
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
    max_concurrent_scans: int = 50  # Increased for parallelism
    scan_interval_seconds: int = 30
    
    # Advanced filters
    max_spread_percent: float = 0.10  # 10% max spread
    taker_fee_percent: float = 0.02   # 2% estimated fee (conservative)


@dataclass
class OpportunityScore:
    """Detailed scoring breakdown"""
    market_id: str
    market_name: str
    market_slug: str # Added slug for URL
    
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
    
    # Advanced Metrics
    spread_percent: float = 0.0
    estimated_net_profit: float = 0.0


class AdvancedScanner:
    """
    Advanced parallel market scanner with multi-criteria scoring.
    """
    
    def __init__(self, config: Optional[ScanConfig] = None):
        self.config = config or ScanConfig()
        self.client: Optional[PolymarketClient] = None
        self._cache: Dict[str, Tuple[datetime, any]] = {}
        self._cache_ttl = 30  # shorter cache for freshness
        
        # Sniper Mode
        from backend.config import settings
        self.sniper_mode = settings.enable_sniper_mode
        self.ws_client: Optional[PolymarketWebSocketClient] = None
        
    async def initialize(self):
        """Initialize the scanner"""
        self.client = get_polymarket_client()
        
        if self.sniper_mode:
            logger.info("Sniper Mode ENABLED: Initializing WebSocket...")
            self.ws_client = PolymarketWebSocketClient(callback=self._handle_ws_update)
            await self.ws_client.connect()
            
        logger.info("Advanced scanner initialized (OPTIMIZED MODE)")
    
    async def close(self):
        """Cleanup resources"""
        if self.client:
            await self.client.close()
        if self.ws_client:
            await self.ws_client.close()

    async def _handle_ws_update(self, data: Dict):
        """Handle real-time updates from WebSocket"""
        pass
    
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
        for result in results:
            if isinstance(result, Exception):
                continue
            
            if result and result.total_score >= self.config.min_score:
                opportunities.append(result)
        
        # Sorting priority: Net Profit, then Score
        opportunities.sort(key=lambda x: (x.estimated_net_profit, x.total_score), reverse=True)
        
        # Notify logic...
        from backend.config import settings
        notification_service = get_notification_service()
        for opp in opportunities:
            # User Request: Notify based on Scanner Config Score (min_score_to_show)
            if opp.total_score >= self.config.min_score:
                await notification_service.notify_opportunity(opp)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Scan complete: {len(opportunities)} opportunities in {elapsed:.2f}s")
        
        return opportunities
    
    
    async def _analyze_market(self, market: Dict) -> Optional[OpportunityScore]:
        """
        Analyze a single market with multi-criteria scoring
        """
        try:
            market_id = market.get("id", "")
            
            # Check cache first
            cached = self._get_cached(f"analysis_{market_id}")
            if cached:
                return cached
            
            # --- 1. EARLY FILTERING (Metadata) ---
            # Don't waste API calls on dead markets
            # Check both 24h and total volume
            vol_24 = float(market.get("volume24hr", 0) or 0)
            vol_total = float(market.get("volume", 0) or 0)
            effective_vol = max(vol_24, vol_total)
            
            if effective_vol < (self.config.min_volume / 2):
                 logger.info(f"REJECT {market_id}: Low Volume {effective_vol}")
                 return None

            tokens = market.get("tokens", [])
            # Fallback for Gamma format
            if not tokens and "clobTokenIds" in market:
                clob_ids = json.loads(market["clobTokenIds"]) if isinstance(market["clobTokenIds"], str) else market["clobTokenIds"]
                if clob_ids and len(clob_ids) >= 2:
                    tokens = [{"token_id": clob_ids[0]}, {"token_id": clob_ids[1]}]
            
            # RAW ORDERBOOK DEBUG (Disabled for prod)
            # token_yes = tokens[0].get("token_id")
            # book_raw = await self.client.get_orderbook(token_yes)
            # print(f"DEBUG RAW BOOK ({market.get('question')[:20]}...): {str(book_raw)[:200]}") 
            
            if len(tokens) < 2:
                # logger.debug(f"REJECT {market_id}: Not enough tokens")
                return None
            
            # --- 2. GET PRICES & ORDERBOOK ---
            token_yes = tokens[0].get("token_id", "")
            token_no = tokens[1].get("token_id", "")
            
            # Parallel fetch of orderbooks (essential for spread/liquidity)
            book_yes_res, book_no_res = await asyncio.gather(
                self.client.get_orderbook(token_yes),
                self.client.get_orderbook(token_no),
                return_exceptions=True
            )
            
            if isinstance(book_yes_res, Exception) or isinstance(book_no_res, Exception):
                # logger.debug(f"REJECT {market_id}: Orderbook fetch failed")
                return None

            if not book_yes_res or not book_no_res or not book_yes_res.get("asks") or not book_no_res.get("asks"):
                 # logger.debug(f"REJECT {market_id}: Empty Orderbook (No Asks)")
                 return None

            # --- 3. SPREAD & FEE CALCULATION ---
            # We use Top of Book (Ask) for "Buying Cost"
            try:
                ask_yes = float(book_yes_res["asks"][0]["price"])
                ask_no = float(book_no_res["asks"][0]["price"])
                
                # We use Top of Book (Bid) to calc Spread
                bid_yes = float(book_yes_res["bids"][0]["price"]) if book_yes_res.get("bids") else 0.0
                bid_no = float(book_no_res["bids"][0]["price"]) if book_no_res.get("bids") else 0.0
            except (ValueError, IndexError, TypeError) as e:
                # logger.debug(f"REJECT {market_id}: Invalid orderbook data ({e})")
                return None
            
            if ask_yes == 0 or ask_no == 0: 
                # logger.debug(f"REJECT {market_id}: Zero price")
                return None

            # Calc Spread %
            spread_yes = (ask_yes - bid_yes) / ask_yes if ask_yes > 0 else 1.0
            spread_no = (ask_no - bid_no) / ask_no if ask_no > 0 else 1.0
            avg_spread = (spread_yes + spread_no) / 2
            
            # FILTER: Reject if spread is too wide (bad liquidity)
            # RELAXED: Don't hard reject, just penalize in score
            # if avg_spread > self.config.max_spread_percent:
            #    logger.info(f"REJECT {market.get('question', 'Unknown')}: Spread too high {avg_spread:.1%} > {self.config.max_spread_percent:.1%}")
            #    return None

            # --- 4. PROFITABILITY SIMULATION ---
            # Cost to buy 1 YES + 1 NO
            cost_basis = ask_yes + ask_no
            
            # Estimated Fee Impact (Taker fee x 2 sides)
            # Polymarket/CTF Exchange often acts as taker
            # fee = cost_basis * self.config.taker_fee_percent
            fee = self.config.taker_fee_percent # Simplified approximation of 2% total drain
            
            # Net Cost
            total_cost_with_fee = cost_basis + fee
            
            # Potential Payout is always 1.0 USDC
            # Net Profit = 1.0 - Total Cost
            estimated_net_profit = 1.0 - total_cost_with_fee
            
            # Divergence Score (Legacy, but useful)
            divergence_score = self._calc_divergence_score(ask_yes, ask_no)
            
            # --- 5. SCORING ---
            volume_score = self._calc_volume_score(market)
            liquidity_score = self._calc_liquidity_score(book_yes_res)
            timing_score = self._calc_timing_score(market)
            activity_score = self._calc_activity_score(market)
            
            # Base Weighted Score
            total = (
                divergence_score * 0.40 +
                volume_score * 0.20 +
                liquidity_score * 0.20 +
                timing_score * 0.10 +
                activity_score * 0.10
            )
            
            # BOOST: If Net Profit is Positive, Score is ALMOST AUTOMATICALLY 10
            # Unless volume/liquidity is absolute trash
            if estimated_net_profit > 0.005: # > 0.5% net profit
                if liquidity_score > 3:
                     total = 10 # JACKPOT
                else:
                     total = 8 # Risky but profitable
            elif estimated_net_profit > -0.02: # Break-even ish or small cost
                 # STRATEGY CHANGE: We might want these for "Equilibrage" if spread is tight
                 if avg_spread < 0.01: # < 1% spread
                     total = max(total, 9) # Great for hedging
                 elif avg_spread < 0.03:
                     total = max(total, 7)
            
            # PENALTY: If Cost > 1.02 (Guaranteed loss long-term), Score should be low
            # Unless we are market making (but we are Takers/Snipers generally)
            if total_cost_with_fee > 1.02:
                logger.info(f"Market {market_id} Overpriced: Cost {total_cost_with_fee:.3f}")
                total = 0 # Don't reject, just 0 score. 
                # Wait, if total is 0, logic below: max(1, int(total)) -> 1.
                # So it will be returned with score 1. Use min_score to filter.
            
            total_score = min(10, max(1, int(total)))
            
            result = OpportunityScore(
                market_id=market_id,
                market_name=market.get("question", "Unknown"),
                market_slug=market.get("slug", ""), # Extract slug
                price_yes=ask_yes,
                price_no=ask_no,
                divergence_score=divergence_score,
                volume_score=volume_score,
                liquidity_score=liquidity_score,
                timing_score=timing_score,
                activity_score=activity_score,
                total_score=total_score,
                volume_24h=vol_24,
                liquidity=float(market.get("liquidity", 0) or 0),
                hours_to_resolution=self._calc_hours_to_resolution(market),
                analyzed_at=datetime.now(),
                spread_percent=avg_spread,
                estimated_net_profit=estimated_net_profit
            )
            
            self._set_cached(f"analysis_{market_id}", result)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing market {market_id}: {e}", exc_info=True)
            return None
    
    # ==================== SCORING FUNCTIONS ====================
    
    def _calc_divergence_score(self, price_yes: float, price_no: float) -> float:
        total = price_yes + price_no
        divergence = abs(1.0 - total)
        return min(10, divergence * 200)
    
    def _calc_volume_score(self, market: Dict) -> float:
        vol_24 = float(market.get("volume24hr", 0) or 0)
        vol_total = float(market.get("volume", 0) or 0)
        volume = max(vol_24, vol_total)
        
        if volume < self.config.min_volume: return 0
        if volume >= 100000: return 10
        elif volume >= 50000: return 8
        elif volume >= 10000: return 5
        else: return 3
    
    def _calc_liquidity_score(self, orderbook: Optional[Dict]) -> float:
        if not orderbook: return 5
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])
        total_depth = sum(float(b.get("size", 0)) for b in bids[:5]) + sum(float(a.get("size", 0)) for a in asks[:5])
        if total_depth < self.config.min_liquidity: return 0
        if total_depth >= 10000: return 10
        elif total_depth >= 5000: return 8
        elif total_depth >= 2000: return 5
        else: return 3
    
    def _calc_timing_score(self, market: Dict) -> float:
        questions = market.get("question", "").lower()
        # Bonus for 'Will X happen by DATE' type questions approaching date
        return 5 # Simplified for now
    
    def _calc_activity_score(self, market: Dict) -> float:
        return 5 # Simplified
    
    def _calc_hours_to_resolution(self, market: Dict) -> Optional[float]:
        end_date = market.get("endDate") or market.get("end_date_iso")
        if not end_date: return None
        try:
            if isinstance(end_date, str):
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
