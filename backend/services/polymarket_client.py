"""
Polymarket Client - Real API Integration
Connects directly to Polymarket CLOB API for market data and trading.
"""
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

logger = logging.getLogger(__name__)

# Polymarket API endpoints
POLYMARKET_API_URL = "https://clob.polymarket.com"
GAMMA_API_URL = "https://gamma-api.polymarket.com"


class PolymarketClient:
    """Client for Polymarket CLOB API and Chain Interactions"""
    
    def __init__(self, api_key: Optional[str] = None, private_key: Optional[str] = None, web3_provider_url: Optional[str] = None):
        self.api_key = api_key
        self.private_key = private_key
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Initialize Web3
        self.w3 = None
        if web3_provider_url:
            try:
                self.w3 = Web3(Web3.HTTPProvider(web3_provider_url))
                self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)  # For Polygon/PoA
                logger.info(f"Web3 initialized with provider: {web3_provider_url[:20]}...")
            except Exception as e:
                logger.error(f"Failed to initialize Web3: {e}")
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
        
    def check_chain_connection(self) -> Dict[str, Any]:
        """
        Check Web3 connection status
        
        Returns:
            Dict with connection status and block number
        """
        if not self.w3:
            return {"connected": False, "error": "Web3 not initialized"}
        
        try:
            connected = self.w3.is_connected()
            block_number = self.w3.eth.block_number if connected else None
            return {
                "connected": connected,
                "block_number": block_number,
                "provider": "Alchemy/Polygon"
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    
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
            # Sort by volume to get meaningful opportunities
            # Gamma API usually uses 'order' or 'sort'. 
            # Trying 'order' -> volume24hr (Gamma specific)
            params = {}
            params["limit"] = limit
            params["active"] = "true"
            params["closed"] = "false" 
            # Sort by liquidity to ensure tradeable markets (Volume can be historical/dead)
            params["order"] = "liquidity"
            params["ascending"] = "false"
            
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
    
    # ==================== TRADING (Real Execution) ====================
    
    async def place_order(
        self,
        token_id: str,
        side: str,  # "BUY" or "SELL"
        size: float,
        price: float,
        order_type: str = "GTC"  # Good Till Cancel
    ) -> Optional[Dict]:
        """
        Place an order on Polymarket using py-clob-client
        """
        if not self.private_key:
            logger.error("Cannot place order: private key not configured")
            return None
            
        try:
            from py_clob_client.clob_types import OrderArgs, OrderType
            from py_clob_client.order_builder.constants import BUY, SELL
            
            # Map side and type
            clob_side = BUY if side.upper() == "BUY" else SELL
            clob_type = OrderType.GTC if order_type.upper() == "GTC" else OrderType.FOK
            
            # Create order args
            order_args = OrderArgs(
                price=price,
                size=size,
                side=clob_side,
                token_id=token_id,
            )
            
            logger.info(f"Placing order: {side} {size} @ {price} (Token: {token_id})")
            
            # Check if using L2 creds or just PK
            # We initialize ClobClient on demand to avoid blocking init if keys missing
            if not hasattr(self, 'clob_client') or not self.clob_client:
                 self._init_clob_client()
            
            if not self.clob_client:
                 logger.error("ClobClient initialization failed, cannot place order")
                 return None

            # Execute via sync call wrapper (as py-clob-client is sync by default)
            # For async context, we should ideally run in threadpool, but for now direct call is OK for MVP
            try:
                resp = self.clob_client.create_and_post_order(order_args)
                logger.info(f"Order placed successfully: {resp}")
                return resp
            except Exception as order_error:
                logger.error(f"py-clob-client error placing order: {order_error}")
                # Log usage details for debugging
                logger.error(f"Order Details - Price: {price}, Size: {size}, Side: {side}, Token: {token_id}")
                return None
            
        except Exception as e:
            logger.error(f"Unexpected error in place_order: {e}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order"""
        if not self.private_key:
            return False
            
        try:
            if not hasattr(self, 'clob_client') or not self.clob_client:
                 self._init_clob_client()
                 
            self.clob_client.cancel(order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            return False
    
    async def get_open_orders(self) -> List[Dict]:
        """Get all open orders"""
        if not self.private_key:
            return []
            
        try:
            if not hasattr(self, 'clob_client') or not self.clob_client:
                 self._init_clob_client()
                 
            # Assuming get_open_orders returns list
            if self.clob_client:
                orders = self.clob_client.get_open_orders()
                return orders
            return []
        except Exception as e:
            logger.error(f"Failed to get open orders: {e}")
            return []

    def _init_clob_client(self):
        """Initialize py-clob-client"""
        try:
            from py_clob_client.client import ClobClient
            from py_clob_client.constants import POLYGON
            from backend.config import settings
            
            if not settings.wallet_private_key:
                logger.warning("Wallet private key not set, skipping ClobClient init")
                self.clob_client = None
                return

            creds = None
            if settings.polymarket_api_key and settings.polymarket_api_secret and settings.polymarket_api_passphrase:
                from py_clob_client.clob_types import ApiCreds
                creds = ApiCreds(
                    api_key=settings.polymarket_api_key,
                    api_secret=settings.polymarket_api_secret,
                    api_passphrase=settings.polymarket_api_passphrase
                )
            
            # Ensure key format is correct (hex string)
            key = settings.wallet_private_key
            if key.startswith('0x'):
                key = key[2:]
                
            self.clob_client = ClobClient(
                host="https://clob.polymarket.com",
                key=key,
                chain_id=137, # Polygon Mainnet
                creds=creds
            )
            logger.info("ClobClient initialized successfully")
        except Exception as e:
            logger.error(f"Could not initialize ClobClient: {e}")
            self.clob_client = None
    
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
            private_key=settings.wallet_private_key,
            web3_provider_url=settings.web3_provider_url
        )
    return polymarket_client
