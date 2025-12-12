
import asyncio
import logging
import sys
import os

# Add parent dir
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.advanced_scanner import get_advanced_scanner, ScanConfig
from backend.services.polymarket_client import get_polymarket_client
from backend.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFY_SCAN")

async def main():
    logger.info("--- STARTING VERIFICATION SCAN ---")
    
    # 1. Config
    logger.info(f"API Key populated: {bool(settings.polymarket_api_key)}")
    logger.info(f"Using Scanner Config: Min Score=1")
    
    # 2. Init Scanner
    scan_config = ScanConfig(min_score=1, max_concurrent_scans=5)
    scanner = get_advanced_scanner(scan_config)
    await scanner.initialize()
    
    # 3. Run Scan
    logger.info("Scanning top 10 active markets...")
    opportunities = await scanner.scan_all_markets(limit=10)
    
    logger.info(f"Scan Finished. Found {len(opportunities)} opportunities.")
    
    for i, opp in enumerate(opportunities):
        logger.info(f"[{i+1}] {opp.market_name}")
        logger.info(f"    ID: {opp.market_id}")
        logger.info(f"    Prices: YES={opp.price_no:.3f} | NO={opp.price_no:.3f}")
        logger.info(f"    Score: {opp.total_score}/10")
        logger.info("-" * 40)
        
    await scanner.close()

if __name__ == "__main__":
    asyncio.run(main())
