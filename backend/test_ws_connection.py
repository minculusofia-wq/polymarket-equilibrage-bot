import asyncio
import logging
import sys
import os

# Add path
sys.path.append(os.getcwd())

from backend.services.polymarket_websocket import PolymarketWebSocketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WS_TEST")

async def test_ws():
    logger.info("Testing WebSocket connection...")
    
    events = []
    
    async def callback(data):
        events.append(data)
        logger.info(f"Received event: {str(data)[:100]}...")

    client = PolymarketWebSocketClient(callback=callback)
    
    try:
        await client.connect()
        logger.info("Connected.")
        
        # Subscribe to something?
        # Trying a dummy subscription to see if we get ANY response or heartbeat
        # Without valid market/token IDs, we might just get a connection and no events
        # But connection success is the main test here
        
        logger.info("Waiting for events (5s)...")
        await asyncio.sleep(5)
        
        # Manually verify we are connected
        if client.ws and not client.ws.closed:
             logger.info("SUCCESS: WS Connection maintained")
        else:
             logger.error("FAILURE: WS Connection closed")

    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_ws())
