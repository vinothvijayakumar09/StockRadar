"""
🇮🇳 Indian Stock Alert Agent - Google ADK Framework
- 100% Free & Open Source
- Uses: Google ADK + Mistral AI + NSE API + feedparser + ntfy.sh
"""
from __future__ import annotations

import time
from datetime import datetime

from config import Config
from logger import log
from agent_core import IndianStockAgent
from tools import send_notification


def run():
    """Main entry point for the ADK-based stock agent"""
    log("🚀 Indian Stock Alert Agent started! (Google ADK Framework)")
    log(f"Framework: Google ADK v2.0")
    log(f"LLM Mode: {Config.LLM_MODE}")
    log(f"ntfy Topic: ntfy.sh/{Config.NTFY_TOPIC or '(not set)'}")
    log(f"YouTube Channel: {'Enabled' if Config.YOUTUBE_CHANNEL_ID else 'Disabled'}")
    log(f"Checking news every {Config.CHECK_INTERVAL_MINUTES} minutes")
    
    # Initialize ADK agent
    agent = IndianStockAgent()
    log(f"Agent initialized: {agent.name} v{agent.version}")
    
    # Send startup notification
    send_notification(
        title="🚀 Stock Agent is LIVE (ADK Framework)",
        body="Monitoring Indian market news with Google ADK. Alerts incoming when stocks are likely to move!",
        direction="UP",
    )
    
    # Main agent loop
    while True:
        try:
            # Run one agent cycle
            agent.run_cycle()
            
            log(f"Sleeping {Config.CHECK_INTERVAL_MINUTES} minutes...")
            time.sleep(Config.CHECK_INTERVAL_MINUTES * 60)
            
        except KeyboardInterrupt:
            log("Agent stopped by user.")
            break
        except Exception as e:
            log(f"Unexpected error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            time.sleep(60)


if __name__ == "__main__":
    run()
