"""Routers package"""
from backend.routers.scanner import router as scanner_router
from backend.routers.positions import router as positions_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.trading import router as trading_router

__all__ = [
    "scanner_router",
    "positions_router",
    "dashboard_router",
    "trading_router",
]
