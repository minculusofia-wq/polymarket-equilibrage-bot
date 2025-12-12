"""
data:
Notification Service
Handles sending alerts to external platforms (Discord, etc.)
"""
import logging
import httpx
from typing import Optional, Dict, List, Any
from datetime import datetime
from backend.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending notifications"""
    
    def __init__(self):
        self.webhook_url = settings.discord_webhook_url
        self.http_client = httpx.AsyncClient(timeout=10.0)
        
    async def close(self):
        await self.http_client.aclose()
        
    async def send_discord_alert(self, 
                               title: str, 
                               description: str, 
                               color: int = 0x00ff00, 
                               fields: List[Dict[str, Any]] = None):
        """
        Send a rich embed to Discord
        
        Args:
            title: Embed title
            description: Main body text
            color: Hex color integer (default green)
            fields: List of dicts with {"name": "...", "value": "...", "inline": bool}
        """
        if not self.webhook_url:
            return

        try:
            embed = {
                "title": title,
                "description": description,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "Polymarket Equilibrage Bot"},
            }
            
            if fields:
                embed["fields"] = fields
                
            payload = {
                "username": "Polymarket Bot",
                "embeds": [embed]
            }
            
            response = await self.http_client.post(self.webhook_url, json=payload)
            response.raise_for_status()
            logger.info(f"Sent Discord notification: {title}")
            
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")

    async def notify_opportunity(self, opportunity: Any):
        """
        Notify about a high-score opportunity
        opportunity: OpportunityScore object
        """
        if not self.webhook_url:
            return
            
        # Determine color based on score
        color = 0x00ff00  # Green
        if opportunity.total_score >= 9:
            color = 0xff0000  # Red (Hot!)
        elif opportunity.total_score >= 7:
            color = 0xffa500  # Orange
            
        fields = [
            {"name": "Score", "value": f"**{opportunity.total_score}/10**", "inline": True},
            {"name": "Divergence", "value": f"{opportunity.divergence_score:.2f}", "inline": True},
            {"name": "Prices", "value": f"YES: {opportunity.price_yes:.3f} | NO: {opportunity.price_no:.3f}", "inline": False},
            {"name": "Total Cost", "value": f"{opportunity.price_yes + opportunity.price_no:.4f}", "inline": True},
            {"name": "Link", "value": f"[View Market](https://polymarket.com/event/{opportunity.market_id})", "inline": False}
        ]
        
        await self.send_discord_alert(
            title=f"🎯 Opportunity Detected: {opportunity.market_name}",
            description="A high-score arbitrage opportunity has been found.",
            color=color,
            fields=fields
        )

# Global instance
_notification_service: Optional[NotificationService] = None

def get_notification_service() -> NotificationService:
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
