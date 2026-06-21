# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import sys
import glob
import importlib
import traceback
from pathlib import Path
from pyrogram import idle
import logging
import logging.config
# Load global small-caps font patcher
import font_patcher

# Force stdout to flush immediately — critical for Docker log visibility
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# ── Logging Setup ────────────────────────────────────────────────────────────
# Override console handler to DEBUG so all logs appear in Docker
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
# Load file config on top (for file handler only)
try:
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
except Exception as _lc_err:
    print(f"[WARNING] Could not load logging.conf: {_lc_err}")

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("motor").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)
# ────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)
logger.info("=== Bot startup initiated ===")

try:
    from pyrogram import Client, __version__
    from pyrogram.raw.all import layer
    logger.info(f"Pyrogram version: {__version__} | Layer: {layer}")

    from config import LOG_CHANNEL, ON_HEROKU, CLONE_MODE, PORT
    from typing import Union, Optional, AsyncGenerator
    from pyrogram import types
    from Script import script
    from datetime import date, datetime
    import pytz
    from aiohttp import web
    from TechVJ.server import web_server

    import asyncio
    from pyrogram import idle
    from plugins.clone import restart_bots
    from TechVJ.bot import StreamBot
    from TechVJ.utils.keepalive import ping_server
    from TechVJ.bot.clients import initialize_clients
    logger.info("All imports successful")
except Exception as import_err:
    print(f"[CRITICAL] Import failed: {import_err}")
    traceback.print_exc()
    sys.exit(1)

loop = asyncio.get_event_loop()



# ── Auto-download Telegram WebApp JS (self-host to avoid user-side ISP blocks) ──
def _ensure_tg_webapp_js():
    """Download telegram-web-app.js from telegram.org at startup so it can be
    served from our own domain. This means users with blocked telegram.org (ISP
    bans) can still load the Mini App SDK correctly."""
    import os, urllib.request
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    dest = os.path.join(static_dir, "telegram-web-app.js")
    # Only download if file doesn't exist or is older than 24 hours
    should_download = not os.path.exists(dest)
    if not should_download:
        import time
        if time.time() - os.path.getmtime(dest) > 86400:  # 24 hours
            should_download = True
    if should_download:
        try:
            url = "https://telegram.org/js/telegram-web-app.js"
            logger.info(f"Downloading {url} → {dest}")
            urllib.request.urlretrieve(url, dest)
            logger.info("telegram-web-app.js downloaded successfully (self-hosted)")
        except Exception as e:
            logger.warning(f"Could not download telegram-web-app.js: {e} — CDN fallback will be used")

_ensure_tg_webapp_js()
# ─────────────────────────────────────────────────────────────────────────────

async def start():

    logger.info("=== async start() called ===")
    try:
        logger.info("Starting StreamBot...")
        await StreamBot.start()
        logger.info("StreamBot started successfully")

        bot_info = await StreamBot.get_me()
        StreamBot.username = bot_info.username
        logger.info(f"Main bot: @{bot_info.username} (id={bot_info.id})")

        # Load main bot settings from MongoDB
        try:
            from plugins.clone import async_mongo_db
            db_config = await async_mongo_db.settings.find_one({"_id": "main_settings"})
            if db_config:
                import config
                if "stream_mode" in db_config:
                    config.STREAM_MODE = db_config["stream_mode"]
                    logger.info(f"Loaded STREAM_MODE={config.STREAM_MODE} from DB")
                if "tma_mode" in db_config:
                    config.TMA_MODE = db_config["tma_mode"]
                    logger.info(f"Loaded TMA_MODE={config.TMA_MODE} from DB")
        except Exception as e:
            logger.error(f"Error loading main bot settings from db: {e}")


        logger.info("Initializing multi-clients...")
        await initialize_clients()
        logger.info("Clients initialized")

        if ON_HEROKU:
            logger.info("Heroku detected — starting ping server task")
            asyncio.create_task(ping_server())

        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time_str = now.strftime("%H:%M:%S %p")

        logger.info(f"Setting up web server on port {PORT}...")
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()
        logger.info(f"Web server running on port {PORT}")

        logger.info(f"Sending restart message to LOG_CHANNEL={LOG_CHANNEL}")
        await StreamBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time_str))

        if CLONE_MODE:
            logger.info("CLONE_MODE=True — restarting clone bots...")
            await restart_bots()
            logger.info("Clone bots started")

        logger.info("=== Bot fully started! Entering idle... ===")
        print("Bot Started Powered By @viralverse0909")
        await idle()

    except Exception as e:
        logger.critical(f"FATAL ERROR in start(): {e}")
        traceback.print_exc()
        raise


# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logger.info('Service Stopped Bye 👋')
    except Exception as fatal:
        logger.critical(f"Bot crashed: {fatal}")
        traceback.print_exc()
        sys.exit(1)


# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
