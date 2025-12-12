from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base, get_db
from backend.config import settings
from backend.routers import scanner_router, positions_router, dashboard_router, trading_router
from backend.services.auto_trading import get_auto_trading_engine
from backend.services.websocket_manager import get_ws_manager
from backend.services.advanced_scanner import get_advanced_scanner


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    
    # Check DB connection
    try:
        from backend.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        
    # Check Redis
    try:
        redis = get_redis_client()
        await redis.ping()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("📊 Database tables created")
    
    # Initialize auto trading engine (but don't start until user enables)
    trading_engine = get_auto_trading_engine()
    logger.info("🤖 Trading engine initialized (standby)")

    # Initialize Scanner (and WS if Sniper Mode enabled)
    scanner = get_advanced_scanner()
    await scanner.initialize()
    logger.info("🔍 Advanced scanner initialized")
    
    logger.info(f"🔧 Debug mode: {settings.debug}")
    logger.info("🚀 Polymarket Bot API ready")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    
    # Close scanner resources
    await scanner.close()
    logger.info("🔍 Advanced scanner closed")
    
    # Stop trading engine if running
    if trading_engine.is_running:
        trading_engine.stop()
        logger.info("🤖 Trading engine stopped")
    
    logger.info("👋 Polymarket Bot API stopped")


# Initialize FastAPI app
app = FastAPI(
    title="Polymarket Equilibrage Bot API",
    description="API for autonomous Polymarket trading bot",
    version="0.2.0",
    debug=settings.debug,
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard_router)
app.include_router(scanner_router)
app.include_router(positions_router)
app.include_router(trading_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    manager = get_ws_manager()
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and process incoming messages if needed
            # For now we only push data, but we need to await receive to keep socket open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Polymarket Equilibrage Bot",
        "version": "0.2.0",
        "status": "running",
        "features": [
            "Advanced parallel scanner",
            "Autonomous trading",
            "Stop-Loss / Take-Profit",
            "Panic button"
        ],
        "docs": "/docs"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        db.execute(text("SELECT 1"))
        
        trading_engine = get_auto_trading_engine()
        
        return {
            "status": "healthy",
            "database": "connected",
            "trading_engine": "running" if trading_engine.is_running else "stopped",
            "version": "0.2.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
