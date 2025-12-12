"""
WebSocket Manager
Handles real-time connections and broadcasting events to frontend.
"""
from fastapi import WebSocket
from typing import List, Dict, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        """Accept new websocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Handle disconnection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")
            
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
            
        # Add timestamp if missing
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
            
        json_msg = json.dumps(message)
        
        # Send to all
        to_remove = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json_msg)
            except Exception as e:
                logger.error(f"Error sending to WS client: {e}")
                to_remove.append(connection)
                
        # Clean up dead connections
        for dead in to_remove:
            self.disconnect(dead)


# Global instance
manager = ConnectionManager()


def get_ws_manager() -> ConnectionManager:
    return manager
