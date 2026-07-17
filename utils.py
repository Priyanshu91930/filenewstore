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
    today = datetime.now(tz).date()
    VERIFIED[user.id] = str(today)

async def check_verification(bot, userid):
    user = await bot.get_users(userid)
    tz = pytz.timezone('Asia/Kolkata')
    today = datetime.now(tz).date()
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

TMA_VERIFIED = MongoDict("tma_verifications")  # {user_id: unix_timestamp or dict}

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
    """Validate the token and mark the user as TMA-verified with 3 free links or time validity."""
    if not validate_tma_token(user_id, token, max_age_sec=timeout or TMA_TIMEOUT):
        return False
    
    key = f"{bot_id}_{user_id}" if bot_id else user_id
    
    tma_type = "links"
    if bot_id:
        try:
            from plugins.clone import async_mongo_db
            bot_doc = await async_mongo_db.bots.find_one({"bot_id": bot_id})
            tma_type = bot_doc.get("tma_type", "links") if bot_doc else "links"
        except:
            pass
            
    if tma_type == "links":
        # 3 free links valid for exactly 1 hour
        TMA_VERIFIED[key] = {
            "links": 3,
            "verified_at": int(time.time())
        }
    else:
        TMA_VERIFIED[key] = int(time.time())

    # Record stats in MongoDB + increment total_verifications counter
    try:
        from plugins.clone import async_mongo_db
        import pytz
        from datetime import datetime
        tz = pytz.timezone('Asia/Kolkata')
        today_str = datetime.now(tz).strftime('%Y-%m-%d')
        
        await async_mongo_db.tma_stats.update_one(
            {"bot_id": bot_id, "user_id": user_id, "date": today_str},
            {"$inc": {"ads_watched": 1}},
            upsert=True
        )
        # Track lifetime verification count per user per bot (used for API alternation)
        await async_mongo_db.tma_verify_count.update_one(
            {"bot_id": bot_id, "user_id": user_id},
            {"$inc": {"count": 1}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error updating tma_stats: {e}")

    return True

async def check_tma_verification(user_id: int, timeout: int = 0, bot_id: int = None) -> bool:
    """Return True if the user already completed TMA verification and has validity left."""
    tma_type = "links"
    bot_tma_timeout = timeout or TMA_TIMEOUT
    if bot_id:
        try:
            from plugins.clone import async_mongo_db
            bot_doc = await async_mongo_db.bots.find_one({"bot_id": bot_id})
            tma_type = bot_doc.get("tma_type", "links") if bot_doc else "links"
            bot_tma_timeout = bot_doc.get("token_timeout", TMA_TIMEOUT) if bot_doc else TMA_TIMEOUT
        except:
            pass

    key = f"{bot_id}_{user_id}" if bot_id else user_id
    if key in TMA_VERIFIED:
        try:
            val = TMA_VERIFIED[key]
            
            # Discard legacy non-dictionary formats
            if not isinstance(val, dict):
                TMA_VERIFIED.pop(key, None)
                return False

            if tma_type == "links":
                verified_at = val.get("verified_at", 0)
                elapsed = time.time() - verified_at
                # 1 hour expiration limit
                if elapsed > 3600:
                    TMA_VERIFIED.pop(key, None)
                    return False
                links = val.get("links", 0)
                if links > 0:
                    return True
            else:
                ts = val.get("verified_at", 0)
                if ts <= 10000:
                    ts = int(time.time())
                    val["verified_at"] = ts
                    TMA_VERIFIED[key] = val
                elapsed = time.time() - ts
                if elapsed < bot_tma_timeout:
                    return True
        except Exception as e:
            logger.error(f"Error checking TMA verification: {e}")
    return False

async def consume_tma_link(user_id: int, bot_id: int = None) -> int:
    """Decrement the user's remaining TMA links by 1 if bot is in link mode. Returns remaining links count."""
    tma_type = "links"
    if bot_id:
        try:
            from plugins.clone import async_mongo_db
            bot_doc = await async_mongo_db.bots.find_one({"bot_id": bot_id})
            tma_type = bot_doc.get("tma_type", "links") if bot_doc else "links"
        except:
            pass

    if tma_type != "links":
        return 3

    key = f"{bot_id}_{user_id}" if bot_id else user_id
    if key in TMA_VERIFIED:
        try:
            val = TMA_VERIFIED[key]
            if not isinstance(val, dict):
                TMA_VERIFIED.pop(key, None)
                return 0
            
            links = val.get("links", 0)
            new_val = max(0, links - 1)
            val["links"] = new_val
            TMA_VERIFIED[key] = val
            return new_val
        except Exception as e:
            logger.error(f"Error in consume_tma_link: {e}")
    return 0

def get_tma_cooldown_remaining(user_id: int, bot_id: int = None) -> int:
    """Returns remaining cooldown seconds if user has 0 links left but 1 hour has not passed. Returns 0 otherwise."""
    key = f"{bot_id}_{user_id}" if bot_id else user_id
    if key in TMA_VERIFIED:
        try:
            val = TMA_VERIFIED[key]
            if isinstance(val, dict):
                links = val.get("links", 0)
                verified_at = val.get("verified_at", 0)
                elapsed = time.time() - verified_at
                if links <= 0 and elapsed <= 3600:
                    return max(0, int(3600 - elapsed))
        except:
            pass
    return 0

async def schedule_tma_renewal_msg(client, chat_id: int, bot_id: int = None, delay: int = 3600):
    """Wait for the 1-hour validity window to finish, then proactively prompt the user to renew."""
    await asyncio.sleep(delay)
    try:
        from utils import check_tma_verification, is_vip, get_tma_link
        from config import URL
        import script
        
        me = client.me or await client.get_me()
        user_is_vip = await is_vip(me.id, chat_id)
        if user_is_vip:
            return
            
        # If they haven't verified again (i.e. check_tma_verification returns False)
        if not await check_tma_verification(chat_id, bot_id=me.id):
            tma_app_url = f"{URL.rstrip('/')}/tma"
            tma_link = await get_tma_link(client, chat_id, tma_app_url, bot_username=me.username)
            btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=types.WebAppInfo(url=tma_link))]]
            try:
                from plugins.clone import clone_mongo_db
                plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
                if plan_cfg:
                    btn.append([InlineKeyboardButton("💳 Buy Plan (Skip Ads)", callback_data="buy_plan")])
            except:
                pass
                
            await client.send_message(
                chat_id=chat_id,
                text="<b>⏰ Your 1-hour validity has completed!</b>\n\nPlease watch a short ad again to unlock 3 more links.",
                reply_markup=InlineKeyboardMarkup(btn),
                protect_content=True
            )
    except Exception as e:
        logger.error(f"Error in scheduled TMA renewal message: {e}")

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
    """Build the target unlock link and shorten it.
    
    Alternates between primary API and secondary API on every verification
    to avoid bot traffic detection on shortlink sites (same-IP issue).
    Odd verifications → primary API, Even verifications → secondary API.
    """
    link = f"https://t.me/{bot_username}?start=unlock-{user_id}-{token}-{file_data}"
    
    # Query database for the bot's configured API Key and shortener URL
    import motor.motor_asyncio
    from config import DB_URI
    
    db_client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
    db = db_client["cloned_vjbotz"]
    
    primary_api_key = None
    primary_shortener_url = "vplink.in"
    secondary_api_key = None
    secondary_shortener_url = "vplink.in"
    tertiary_api_key = None
    tertiary_shortener_url = "alpha-links.in"
    
    bot = await db.bots.find_one({"username": bot_username})
    if bot:
        primary_api_key = bot.get("shortener_api")
        primary_shortener_url = bot.get("shortener_site") or "vplink.in"
        secondary_api_key = bot.get("secondary_shortener_api")
        secondary_shortener_url = bot.get("secondary_shortener_site") or primary_shortener_url
        tertiary_api_key = bot.get("tertiary_shortener_api")
        tertiary_shortener_url = bot.get("tertiary_shortener_site") or "alpha-links.in"
        bot_id = bot.get("bot_id")
    else:
        # Check if it's the main bot
        from config import BOT_USERNAME
        if bot_username.lower() == BOT_USERNAME.lower():
            from config import SHORTLINK_API, SHORTLINK_URL
            primary_api_key = SHORTLINK_API
            primary_shortener_url = SHORTLINK_URL
            # Try to load secondary/tertiary shortener settings for main bot
            try:
                from config import SECONDARY_SHORTLINK_API, SECONDARY_SHORTLINK_URL
                secondary_api_key = SECONDARY_SHORTLINK_API
                secondary_shortener_url = SECONDARY_SHORTLINK_URL or primary_shortener_url
            except ImportError:
                secondary_api_key = None
                secondary_shortener_url = primary_shortener_url
                
            try:
                from config import TERTIARY_SHORTLINK_API, TERTIARY_SHORTLINK_URL
                tertiary_api_key = TERTIARY_SHORTLINK_API
                tertiary_shortener_url = TERTIARY_SHORTLINK_URL or "alpha-links.in"
            except ImportError:
                tertiary_api_key = None
                tertiary_shortener_url = "alpha-links.in"
            
            # Use pseudo bot_id for tracking main bot verifications count
            bot_id = 999999999
        else:
            bot_id = None

    # Dynamically build a list of all configured APIs
    apis = []
    if primary_api_key and primary_api_key != "None":
        apis.append((primary_api_key, primary_shortener_url, "PRIMARY"))
    if secondary_api_key and secondary_api_key != "None":
        apis.append((secondary_api_key, secondary_shortener_url, "SECONDARY"))
    if tertiary_api_key and tertiary_api_key != "None":
        apis.append((tertiary_api_key, tertiary_shortener_url, "TERTIARY"))

    # Rotate through all available configured APIs based on verification count
    if apis and bot_id:
        try:
            count_doc = await db.tma_verify_count.find_one({"bot_id": bot_id, "user_id": user_id})
            verify_count = count_doc.get("count", 0) if count_doc else 0
            selected_idx = verify_count % len(apis)
            api_key, shortener_url, label = apis[selected_idx]
            logger.info(f"[get_tma_shortlink] Using {label} API for user {user_id} (count={verify_count})")
            shortened_verify_url = await get_verify_shorted_link(link, api_key=api_key, shortener_url=shortener_url)
        except Exception as e:
            logger.error(f"Error dynamically selecting shortener API: {e}")
            shortened_verify_url = await get_verify_shorted_link(link, api_key=primary_api_key, shortener_url=primary_shortener_url)
    else:
        shortened_verify_url = await get_verify_shorted_link(link, api_key=primary_api_key, shortener_url=primary_shortener_url)
        
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
