"""Utility functions for aa_kanban."""

import logging
import requests

logger = logging.getLogger(__name__)

def send_discord_webhook(url: str, message: str) -> bool:
    """Send a basic text message to a Discord webhook URL.
    
    Returns True if successful, False otherwise.
    """
    if not url:
        return False
        
    payload = {
        "content": message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send Discord webhook: {e}")
        return False
