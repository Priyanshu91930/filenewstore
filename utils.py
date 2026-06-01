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
VERIFIED = {}

async def get_verify_shorted_link(link):
    if SHORTLINK_URL == "api.shareus.io":
        url = f'https://{SHORTLINK_URL}/easy_api'
        params = {
            "key": SHORTLINK_API,
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
  #      response = requests.get(f"https://{SHORTLINK_URL}/api?api={SHORTLINK_API}&url={link}")
 #       data = response.json()
  #      if data["status"] == "success" or rget.status_code == 200:
   #         return data["shortenedUrl"]
        shortzy = Shortzy(api_key=SHORTLINK_API, base_site=SHORTLINK_URL)
        link = await shortzy.convert(link)
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

TMA_VERIFIED = {}  # {user_id: iso_date_string}

def _generate_tma_token(user_id: int) -> str:
    """Generate a short-lived HMAC token to verify the TMA ad completion."""
    ts = str(int(time.time()))
    raw = f"{user_id}:{ts}"
    sig = hmac.new(TMA_SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{ts}-{sig}"

def _validate_tma_token(user_id: int, token: str, max_age_sec: int = 600) -> bool:
    """Validate a TMA token. Returns True if the token is valid and not expired."""
    try:
        ts_str, sig = token.split("-", 1)
        ts = int(ts_str)
        if int(time.time()) - ts > max_age_sec:
            return False
        raw = f"{user_id}:{ts_str}"
        expected_sig = hmac.new(TMA_SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()[:16]
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False

async def get_tma_link(bot, user_id: int, app_url: str, file_data: str = "") -> str:
    """Build the Mini App URL containing the user_id, a signed token, and optional file_data.

    file_data is the raw /start parameter (e.g. base64-encoded file id or BATCH-xxx).
    It is embedded in the TMA URL so the Mini App can construct the exact bot deeplink
    to deliver the file AFTER the user watches the ad.
    """
    token = _generate_tma_token(user_id)
    url = f"{app_url}?uid={user_id}&token={token}"
    if file_data:
        from urllib.parse import quote
        url += f"&file={quote(file_data)}"
    return url

async def verify_tma_user(user_id: int, token: str) -> bool:
    """Validate the token and mark the user as TMA-verified for today."""
    if not _validate_tma_token(user_id, token):
        return False
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    TMA_VERIFIED[user_id] = str(today)
    return True

async def check_tma_verification(user_id: int) -> bool:
    """Return True if the user already completed TMA verification today."""
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    if user_id in TMA_VERIFIED:
        exp_str = TMA_VERIFIED[user_id]
        years, month, day = exp_str.split('-')
        comp = date(int(years), int(month), int(day))
        return comp >= today
    return False
