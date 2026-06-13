# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import logging, asyncio, os, re, random, pytz, aiohttp, requests, string, json, http.client, hmac, hashlib, time
from datetime import date, datetime
from config import SHORTLINK_API, SHORTLINK_URL, FORCE_SUB_CHANNELS, UNIVERSAL_FORCE_SUB_CHANNEL, TMA_SECRET_KEY
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shortzy import Shortzy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TOKENS = {}

from collections import UserDict
import motor.motor_asyncio
from config import DB_URI

class MongoDict(UserDict):
    def __init__(self, collection_name):
        super().__init__()
        self.collection_name = collection_name
        self._client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.db = self._client["cloned_vjbotz"]
        self.col = self.db[collection_name]
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            asyncio.create_task(self._async_load())
        else:
            loop.run_until_complete(self._async_load())

    async def _async_load(self):
        try:
            cursor = self.col.find({})
            async for doc in cursor:
                # Keep keys consistent as they might be stored as strings in MongoDB
                key = doc["_id"]
                val = doc["val"]
                # If key is string digits, convert to integer user ID
                if isinstance(key, str) and key.isdigit():
                    key = int(key)
                self.data[key] = val
        except Exception as e:
            logger.error(f"Error loading MongoDict {self.collection_name}: {e}")

    def __setitem__(self, key, value):
        self.data[key] = value
        async def do_update():
            try:
                await self.col.update_one(
                    {"_id": str(key)},
                    {"$set": {"val": value}},
                    upsert=True
                )
            except Exception as e:
                logger.error(f"Error in MongoDict update: {e}")
        asyncio.create_task(do_update())

    def pop(self, key, default=None):
        val = self.data.pop(key, default)
        async def do_delete():
            try:
                await self.col.delete_one({"_id": str(key)})
            except Exception as e:
                logger.error(f"Error in MongoDict delete: {e}")
        asyncio.create_task(do_delete())
        return val

VERIFIED = MongoDict("std_verifications")

async def get_verify_shorted_link(link, api_key=None, shortener_url=None):
    api = api_key or SHORTLINK_API
    site = shortener_url or SHORTLINK_URL
    if not api or not site or api == "None" or site == "None":
        return link
    site = site.replace("https://", "").replace("http://", "").strip("/")
    
    if site == "api.shareus.io":
        url = f'https://{site}/easy_api'
        params = {
            "key": api,
            "link": link,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.text()
                    return data
        except Exception as e:
            logger.error(e)
            return link
    else:
        try:
            shortzy = Shortzy(api_key=api, base_site=site)
            link = await shortzy.convert(link)
            return link
        except Exception as e:
            logger.error(e)
            return link

async def check_token(bot, userid, token):
    user = await bot.get_users(userid)
    if user.id in TOKENS.keys():
        TKN = TOKENS[user.id]
        if token in TKN.keys():
            is_used = TKN[token]
            if is_used == True:
                return False
            else:
                return True
    else:
        return False

async def get_token(bot, userid, link):
    user = await bot.get_users(userid)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    link = f"{link}verify-{user.id}-{token}"
    shortened_verify_url = await get_verify_shorted_link(link)
    return str(shortened_verify_url)

async def verify_user(bot, userid, token):
    user = await bot.get_users(userid)
    TOKENS[user.id] = {token: True}
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    VERIFIED[user.id] = str(today)

async def check_verification(bot, userid):
    user = await bot.get_users(userid)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    if user.id in VERIFIED.keys():
        EXP = VERIFIED[user.id]
        years, month, day = EXP.split('-')
        comp = date(int(years), int(month), int(day))
        if comp<today:
            return False
        else:
            return True
    else:
        return False
async def is_subscribed(bot, message):
    if not FORCE_SUB_CHANNELS:
        return True
    not_joined = []
    for channel_id in FORCE_SUB_CHANNELS:
        try:
            member = await bot.get_chat_member(channel_id, message.from_user.id)
            if member.status == "kicked":
                return "kicked"
        except UserNotParticipant:
            not_joined.append(channel_id)
        except Exception as e:
            logger.error(f"Error checking membership for {channel_id}: {e}")
            continue
    return not_joined if not_joined else True

async def is_subscribed_universal(bot, message):
    if not UNIVERSAL_FORCE_SUB_CHANNEL:
        return True
    try:
        member = await bot.get_chat_member(UNIVERSAL_FORCE_SUB_CHANNEL, message.from_user.id)
        if member.status == "kicked":
            return "kicked"
    except UserNotParticipant:
        try:
            # Verify the channel is actually accessible before requiring it
            await bot.get_chat(UNIVERSAL_FORCE_SUB_CHANNEL)
            return [UNIVERSAL_FORCE_SUB_CHANNEL]
        except:
            return True
    except Exception as e:
        # If the channel is invalid or bot is not in it, just skip the check silently to avoid log spam
        if "CHANNEL_INVALID" in str(e) or "CHAT_ADMIN_REQUIRED" in str(e):
            return True
        logger.error(f"Error checking universal membership: {e}")
        return True
    return True

# ─── Telegram Mini App (Monetag) Verification Helpers ───────────────────────

TMA_VERIFIED = MongoDict("tma_verifications")  # {user_id: unix_timestamp of verification}

# Global TMA timeout in seconds. Can be overridden per-bot via token_timeout in DB.
# Default: 10800 = 3 hours. Change this to adjust the global default.
try:
    from config import TMA_TIMEOUT as _CFG_TMA_TIMEOUT
except ImportError:
    _CFG_TMA_TIMEOUT = 10800
TMA_TIMEOUT = _CFG_TMA_TIMEOUT  # seconds

def _generate_tma_token(user_id: int) -> str:
    """Generate a short-lived HMAC token to verify the TMA ad completion."""
    ts = str(int(time.time()))
    raw = f"{user_id}:{ts}"
    sig = hmac.new(TMA_SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{ts}-{sig}"

def validate_tma_token(user_id: int, token: str, max_age_sec: int = 0) -> bool:
    """Validate a TMA token. Returns True if the token is valid and not expired."""
    _max_age = max_age_sec or TMA_TIMEOUT
    try:
        ts_str, sig = token.split("-", 1)
        ts = int(ts_str)
        if int(time.time()) - ts > _max_age:
            return False
        raw = f"{user_id}:{ts_str}"
        expected_sig = hmac.new(TMA_SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()[:16]
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False

async def get_tma_link(bot, user_id: int, app_url: str, file_data: str = "", bot_username: str = "") -> str:
    """Build the Mini App URL containing the user_id, a signed token, and optional file_data.

    file_data is the raw /start parameter (e.g. base64-encoded file id or BATCH-xxx).
    It is embedded in the TMA URL so the Mini App can construct the exact bot deeplink
    to deliver the file AFTER the user watches the ad.
    """
    token = _generate_tma_token(user_id)
    # Automatically convert http:// to https:// to satisfy Telegram's strict WebApp URL requirements
    if app_url.startswith("http://"):
        app_url = "https://" + app_url[7:]
    url = f"{app_url}?uid={user_id}&token={token}"
    if bot_username:
        url += f"&bot={bot_username}"
    if file_data:
        from urllib.parse import quote
        url += f"&file={quote(file_data)}"
    return url

async def verify_tma_user(user_id: int, token: str, timeout: int = 0, bot_id: int = None) -> bool:
    """Validate the token and mark the user as TMA-verified.
    timeout: validity in seconds (0 = use global TMA_TIMEOUT).
    """
    if not validate_tma_token(user_id, token, max_age_sec=timeout or TMA_TIMEOUT):
        return False
    key = f"{bot_id}_{user_id}" if bot_id else user_id
    TMA_VERIFIED[key] = time.time()
    return True

async def check_tma_verification(user_id: int, timeout: int = 0, bot_id: int = None) -> bool:
    """Return True if the user already completed TMA verification within the configured window.
    timeout: override validity in seconds (0 = use global TMA_TIMEOUT).
    """
    tmo = timeout or TMA_TIMEOUT
    if bot_id:
        key = f"{bot_id}_{user_id}"
        if key in TMA_VERIFIED:
            verified_time = TMA_VERIFIED[key]
            if time.time() - verified_time < tmo:
                return True
    if user_id in TMA_VERIFIED:
        verified_time = TMA_VERIFIED[user_id]
        if time.time() - verified_time < tmo:
            return True
    return False

# ─── One-time Token Consumption Helper ────────────────────────────────────
async def is_token_consumed(token: str) -> bool:
    """Check if the TMA verification token has already been consumed."""
    try:
        from plugins.clone import async_mongo_db
        res = await async_mongo_db.consumed_tokens.find_one({"_id": token})
        return res is not None
    except Exception as e:
        logger.error(f"Error checking token consumption: {e}")
        return False

async def consume_token(token: str):
    """Consume the TMA verification token so it cannot be used again."""
    try:
        from plugins.clone import async_mongo_db
        # Store with expireAt so MongoDB automatically cleans it up after 24 hours
        await async_mongo_db.consumed_tokens.update_one(
            {"_id": token},
            {"$set": {"consumed_at": time.time(), "expireAt": datetime.fromtimestamp(time.time() + 86400)}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error consuming token: {e}")

async def get_tma_shortlink(user_id: int, token: str, file_data: str, bot_username: str) -> str:
    """Build the target unlock link and shorten it."""
    link = f"https://t.me/{bot_username}?start=unlock-{user_id}-{token}-{file_data}"
    
    # Query database for the bot's configured API Key and shortener URL
    import motor.motor_asyncio
    from config import DB_URI
    
    client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
    db = client["cloned_vjbotz"]
    
    api_key = None
    shortener_url = "vplink.in"
    
    bot = await db.bots.find_one({"username": bot_username})
    if bot:
        api_key = bot.get("shortener_api")
        shortener_url = bot.get("shortener_site") or "vplink.in"
    else:
        # Check if it's the main bot
        from config import BOT_USERNAME
        if bot_username.lower() == BOT_USERNAME.lower():
            from config import SHORTLINK_API, SHORTLINK_URL
            api_key = SHORTLINK_API
            shortener_url = SHORTLINK_URL
            
    shortened_verify_url = await get_verify_shorted_link(link, api_key=api_key, shortener_url=shortener_url)
    return str(shortened_verify_url)

async def is_vip(bot_id: int, user_id: int) -> bool:
    try:
        from plugins.clone import async_mongo_db
        vip_user = await async_mongo_db.vip_users.find_one({"bot_id": bot_id, "user_id": user_id})
        if not vip_user:
            return False
        expiry = vip_user.get("expiry")
        if expiry is None:  # Lifetime
            return True
        if time.time() < expiry:
            return True
        # Expired - remove from DB
        await async_mongo_db.vip_users.delete_one({"bot_id": bot_id, "user_id": user_id})
        return False
    except Exception as e:
        logger.error(f"Error checking VIP status: {e}")
        return False
