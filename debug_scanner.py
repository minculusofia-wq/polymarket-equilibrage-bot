import asyncio
import logging
from backend.services.advanced_scanner import get_advanced_scanner, ScanConfig
from backend.database import SessionLocal
from backend.models.scanner_config import ScannerConfig as DBConfig

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend.services.advanced_scanner")
logger.setLevel(logging.DEBUG)

async def debug_scan():
    print("--- Starting Debug Scan ---")
    
    db = SessionLocal()
    config = db.query(DBConfig).first()
    db.close()
    
    if not config:
        print("❌ No config found in DB!")
        return

    print(f"Config loaded: Min Score={config.min_score_to_show}, Vol={config.min_volume_24h}, Liq={config.min_liquidity}")

    # Relax filters for debugging
    scan_config = ScanConfig(
        min_score=0,
        min_volume=0,
        min_liquidity=0,
        max_spread_percent=0.50 # 50% spread allowed
    )
    scanner = get_advanced_scanner(scan_config)
    
    # Run scan
    print("Fetching markets...")
    await scanner.initialize()
    
    # Manually fetch to see what we are getting
    markets = await scanner.client.get_markets(limit=5)
    print(f"DEBUG: First Market Keys: {markets[0].keys()}")
    print(f"DEBUG: First Market Full: {markets[0]}")
    print(f"DEBUG: First 5 markets RAW:")
    for m in markets:
         print(f"- {m.get('question')} | Vol: {m.get('volume24hr')} | Liq: {m.get('liquidity')}")
    
    opps = await scanner.scan_all_markets(limit=10)
    
    print(f"\n--- Scan Complete. Found {len(opps)} opportunities ---")
    for op in opps:
        print(f"[{op.total_score}/10] {op.market_name}")
        print(f"   Prices: Yes {op.price_yes:.2f} | No {op.price_no:.2f} | Sum: {op.price_yes + op.price_no:.2f}")
        print(f"   Spread: {op.spread_percent:.1%} | Profit: {op.estimated_net_profit:.1%}")


    if len(opps) == 0:
        print("\nPossible reasons for 0 results:")
        print("1. API returned 0 markets (check connection)")
        print(f"2. Filters too strict (Vol > {config.min_volume_24h}, Liq > {config.min_liquidity})")
        print("3. Scoring logic returned 0 for all")

if __name__ == "__main__":
    asyncio.run(debug_scan())
