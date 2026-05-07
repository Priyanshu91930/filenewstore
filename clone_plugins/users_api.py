# © Telegram : @Brainaxe190 , GitHub : @VJBots
# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import aiohttp
import json
from motor.motor_asyncio import AsyncIOMotorClient
from config import CLONE_DB_URI, CDB_NAME

# Async DB Setup
client = AsyncIOMotorClient(CLONE_DB_URI)
db = client[CDB_NAME]
col = db["users"]

async def get_short_link(user, link):
    api_key = user.get("shortener_api")
    base_site = user.get("base_site")
    if not api_key or not base_site:
        return link
        
    # Clean URL to prevent crashes
    clean_site = base_site.replace("https://", "").replace("http://", "").strip("/")
    url = f"https://{clean_site}/api?api={api_key}&url={link}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        return data.get("shortenedUrl", link)
    except Exception as e:
        print(f"Shortener error: {e}")
        
    return link

async def get_user(bot_id, user_id):
    bot_id = int(bot_id)
    user_id = int(user_id)
    user = await col.find_one({"bot_id": bot_id, "user_id": user_id})
    if not user:
        res = {
            "bot_id": bot_id,
            "user_id": user_id,
            "shortener_api": None,
            "base_site": None,
            "caption_prefix": "",
        }
        await col.insert_one(res)
        user = res
    
    # Ensure fields exist
    if "caption_prefix" not in user:
        await col.update_one({"bot_id": bot_id, "user_id": user_id}, {"$set": {"caption_prefix": ""}})
        user["caption_prefix"] = ""
        
    return user

async def update_user_info(bot_id, user_id, value:dict):
    bot_id = int(bot_id)
    user_id = int(user_id)
    await col.update_one({"bot_id": bot_id, "user_id": user_id}, {"$set": value})
