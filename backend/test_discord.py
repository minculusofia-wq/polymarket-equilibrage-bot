
import asyncio
import logging
import sys
import os

# Add parent dir
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.notification import get_notification_service
from backend.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST_DISCORD")

async def main():
    logger.info("--- TEST DISCORD NOTIFICATION ---")
    
    if not settings.discord_webhook_url:
        logger.error("❌ DISCORD_WEBHOOK_URL is missing in settings!")
        return

    logger.info(f"Using Webhook: {settings.discord_webhook_url[:30]}...")
    
    service = get_notification_service()
    
    logger.info("Sending test alert...")
    success = await service.send_discord_alert(
        title="🔔 Polypulse Bot Connected",
        description="Le système de notification Discord est opérationnel ! Vous recevrez ici les meilleures opportunités.",
        color=0x00FF00, # Green
        fields=[
            {"name": "Status", "value": "Online", "inline": True},
            {"name": "Mode", "value": "Sniper Active", "inline": True}
        ]
    )
    
    if success:
        logger.info("✅ Test notification sent successfully!")
    else:
        logger.error("❌ Failed to send notification (Check URL or Network)")

if __name__ == "__main__":
    asyncio.run(main())
