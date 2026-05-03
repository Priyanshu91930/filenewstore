# © Telegram : @Brainaxe190 , GitHub : @VJBots

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import requests
import json
from motor.motor_asyncio import AsyncIOMotorClient
from config import CLONE_DB_URI, CDB_NAME

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

client = AsyncIOMotorClient(CLONE_DB_URI)
db = client[CDB_NAME]
col = db["users"]

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

async def get_short_link(user, link):
    api_key = user["shortener_api"]
    base_site = user["base_site"]
    print(user)
    response = requests.get(f"https://{base_site}/api?api={api_key}&url={link}")
    data = response.json()
    if data["status"] == "success" or rget.status_code == 200:
        return data["shortenedUrl"]

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

# Composite key approach: {"bot_id": bot_id, "user_id": user_id}
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
        user = await col.find_one({"bot_id": bot_id, "user_id": user_id})
    
    # Migration/Check for caption_prefix
    if "caption_prefix" not in user:
        await col.update_one({"bot_id": bot_id, "user_id": user_id}, {"$set": {"caption_prefix": ""}})
        user["caption_prefix"] = ""
    return user

async def update_user_info(bot_id, user_id, value:dict):
    bot_id = int(bot_id)
    user_id = int(user_id)
    myquery = {"bot_id": bot_id, "user_id": user_id}
    newvalues = { "$set": value }
    await col.update_one(myquery, newvalues)

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
