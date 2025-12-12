"""
Polymarket Client - Real API Integration
Connects directly to Polymarket CLOB API for market data and trading.
"""
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Polymarket API endpoints
POLYMARKET_API_URL = "https://clob.polymarket.com"
GAMMA_API_URL = "https://gamma-api.polymarket.com"


class PolymarketClient:
    """Client for Polymarket CLOB API"""
    
    def __init__(self, api_key: Optional[str] = None, private_key: Optional[str] = None):
        self.api_key = api_key
        self.private_key = private_key
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
    
    # ==================== MARKET DATA ====================
    
    async def get_markets(self, limit: int = 100, active_only: bool = True) -> List[Dict]:
        """
        Fetch list of markets from Polymarket
        
        Args:
            limit: Maximum number of markets to return
            active_only: Only return active markets
            
        Returns:
            List of market dictionaries
        """
        try:
            url = f"{GAMMA_API_URL}/markets"
            params = {"limit": limit}
            if active_only:
                params["active"] = "true"
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            
            markets = response.json()
            logger.info(f"Fetched {len(markets)} markets from Polymarket")
            return markets
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch markets: {e}")
            return []
    
    async def get_market(self, market_id: str) -> Optional[Dict]:
        """
        Fetch single market details
        
        Args:
            market_id: The market/condition ID
            
        Returns:
            Market dictionary or None if not found
        """
        try:
            url = f"{GAMMA_API_URL}/markets/{market_id}"
            response = await self.http_client.get(url)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch market {market_id}: {e}")
            return None
    
    async def get_market_prices(self, token_id: str) -> Optional[Dict]:
        """
        Fetch current prices for a market token
        
        Args:
            token_id: The token ID (YES or NO token)
            
        Returns:
            Price data dictionary
        """
        try:
            url = f"{POLYMARKET_API_URL}/price"
            params = {"token_id": token_id}
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch price for token {token_id}: {e}")
            return None
    
    async def get_orderbook(self, token_id: str) -> Optional[Dict]:
        """
        Fetch orderbook for a token
        
        Args:
            token_id: The token ID
            
        Returns:
            Orderbook with bids and asks
        """
        try:
            url = f"{POLYMARKET_API_URL}/book"
            params = {"token_id": token_id}
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch orderbook for {token_id}: {e}")
            return None
    
    async def get_midpoint_price(self, token_id: str) -> Optional[float]:
        """
        Get the midpoint price between best bid and ask
        
        Args:
            token_id: The token ID
            
        Returns:
            Midpoint price as float
        """
        try:
            url = f"{POLYMARKET_API_URL}/midpoint"
            params = {"token_id": token_id}
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return float(data.get("mid", 0))
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch midpoint for {token_id}: {e}")
            return None
    
    # ==================== TRADING (requires auth) ====================
    
    async def place_order(
        self,
        token_id: str,
        side: str,  # "BUY" or "SELL"
        size: float,
        price: float,
        order_type: str = "GTC"  # Good Till Cancel
    ) -> Optional[Dict]:
        """
        Place an order on Polymarket
        
        Args:
            token_id: Token to trade
            side: "BUY" or "SELL"
            size: Amount to trade
            price: Price per token
            order_type: Order type (GTC, FOK, etc.)
            
        Returns:
            Order confirmation or None if failed
        """
        if not self.private_key:
            logger.error("Cannot place order: private key not configured")
            return None
        
        # TODO: Implement order signing with py-clob-client
        # This requires the py-clob-client library for proper signing
        logger.warning("Order placement not yet implemented - requires wallet configuration")
        return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        if not self.private_key:
            logger.error("Cannot cancel order: private key not configured")
            return False
        
        # TODO: Implement order cancellation
        logger.warning("Order cancellation not yet implemented")
        return False
    
    async def get_open_orders(self) -> List[Dict]:
        """
        Get all open orders for the configured wallet
        
        Returns:
            List of open orders
        """
        if not self.private_key:
            logger.error("Cannot get orders: private key not configured")
            return []
        
        # TODO: Implement with authentication
        return []
    
    # ==================== ANALYSIS ====================
    
    async def analyze_market_opportunity(self, market: Dict) -> Dict:
        """
        Analyze a market for equilibrage opportunity
        
        Args:
            market: Market data dictionary
            
        Returns:
            Analysis with divergence and score
        """
        tokens = market.get("tokens", [])
        if len(tokens) < 2:
            return {"score": 0, "divergence": 0, "reason": "Invalid market structure"}
        
        prices = []
        for token in tokens:
            price = await self.get_midpoint_price(token.get("token_id", ""))
            if price:
                prices.append(price)
        
        if len(prices) < 2:
            return {"score": 0, "divergence": 0, "reason": "Could not fetch prices"}
        
        # Calculate divergence from equilibrium (YES + NO should = 1.0)
        total = sum(prices)
        divergence = abs(1.0 - total)
        
        # Score based on divergence (higher divergence = higher score)
        # But also consider liquidity and volume
        score = min(10, int(divergence * 100))  # Scale divergence to 1-10
        
        return {
            "market_id": market.get("id", ""),
            "market_name": market.get("question", "Unknown"),
            "price_yes": prices[0] if len(prices) > 0 else 0,
            "price_no": prices[1] if len(prices) > 1 else 0,
            "total": total,
            "divergence": divergence,
            "score": score,
            "analyzed_at": datetime.now().isoformat()
        }


# Global client instance (will be initialized with config)
polymarket_client: Optional[PolymarketClient] = None


def get_polymarket_client() -> PolymarketClient:
    """Get or create Polymarket client instance"""
    global polymarket_client
    if polymarket_client is None:
        from backend.config import settings
        polymarket_client = PolymarketClient(
            api_key=settings.polymarket_api_key,
            private_key=settings.wallet_private_key
        )
    return polymarket_client
