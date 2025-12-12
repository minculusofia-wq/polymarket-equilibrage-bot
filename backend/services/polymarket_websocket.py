"""
Polymarket WebSocket Client
Handles real-time data streaming from Polymarket CLOB
"""
import asyncio
import json
import logging
from typing import List, Dict, Callable, Optional, Set
import websockets

logger = logging.getLogger(__name__)

# Polymarket CLOB WebSocket Endpoint
WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

class PolymarketWebSocketClient:
    """
    Async WebSocket client for Polymarket
    """
    def __init__(self, callback: Optional[Callable[[Dict], None]] = None):
        self.ws_url = WS_URL
        self.ws = None
        self.running = False
        self.callback = callback
        self.subscribed_assets: Set[str] = set()
        self.lock = asyncio.Lock()
        
    async def connect(self):
        """Establish WebSocket connection"""
        import ssl
        
        try:
            logger.info(f"Connecting to Polymarket WS: {self.ws_url}")
            # Bypass SSL verify for mac env issues
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            self.ws = await websockets.connect(self.ws_url, ssl=ssl_context, ping_interval=20, ping_timeout=20)
            self.running = True
            logger.info("Connected to Polymarket WS")
            
            # Start listener loop
            asyncio.create_task(self._listen())
            # Bypass SSL verify for mac env issues
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            self.ws = await websockets.connect(self.ws_url, ssl=ssl_context, ping_interval=20, ping_timeout=20)
            self.running = True
            logger.info("Connected to Polymarket WS")
            
            # Start listener loop
            asyncio.create_task(self._listen())
            
        except Exception as e:
            logger.error(f"Failed to connect to WS: {e}")
            self.running = False
            raise

    async def _listen(self):
        """Listen for messages"""
        while self.running and self.ws:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                # Check for event types
                # Typically: [{"event_type": "book", "market": "...", "data": ...}]
                if isinstance(data, list):
                    for item in data:
                        await self._handle_message(item)
                else:
                    await self._handle_message(data)
                    
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WS Connection closed, attempting reconnect...")
                await self._reconnect()
                break
            except Exception as e:
                logger.error(f"Error in WS listener: {e}")
                await asyncio.sleep(1)

    async def _handle_message(self, data: Dict):
        """Process incoming message"""
        # Distribute to callback
        if self.callback:
            try:
                # Run callback (maybe async?)
                if asyncio.iscoroutinefunction(self.callback):
                    await self.callback(data)
                else:
                    self.callback(data)
            except Exception as e:
                logger.error(f"Error in callback: {e}")

    async def subscribe(self, asset_ids: List[str]):
        """
        Subscribe to orderbook/price updates for assets
        asset_ids: List of token_ids (tokens, not condition IDs usually)
        """
        if not self.ws or not self.running:
            logger.warning("WS not connected, cannot subscribe")
            return

        # Format subscription message - CLOB typically expects specific format
        # Common format: {"assets": [...], "type": "market"}
        # Or checking docs: usually subscribe to "book" or "price"
        
        # Taking generic approach for CLOB usually:
        # { "type": "subscribe", "channel": "book", "token_ids": [...] }
        # Let's try standard CLOB simplified
        
        payload = {
            "type": "subscribe",
            "assets": asset_ids,
            "channel": "book"  # or price, trade
        }
        
        try:
            await self.ws.send(json.dumps(payload))
            self.subscribed_assets.update(asset_ids)
            logger.info(f"Subscribed to {len(asset_ids)} assets")
        except Exception as e:
            logger.error(f"Failed to subscribe: {e}")

    async def _reconnect(self):
        """Reconnect logic"""
        self.running = False
        if self.ws:
            await self.ws.close()
        
        await asyncio.sleep(5)
        await self.connect()
        # Resubscribe
        if self.subscribed_assets:
            await self.subscribe(list(self.subscribed_assets))

    async def close(self):
        """Close connection"""
        self.running = False
        if self.ws:
            await self.ws.close()
