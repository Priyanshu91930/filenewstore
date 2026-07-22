# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import os
import logging
import random
import asyncio
from Script import script
from validators import domain
from clone_plugins.dbusers import clonedb
from clone_plugins.users_api import get_user, update_user_info
from clone_plugins.genlink import _ask
from pyrogram import Client, filters, enums
from plugins.clone import async_mongo_db as mongo_db
from pyrogram.errors import ChatAdminRequired, FloodWait, UserNotParticipant
from config import BOT_USERNAME, ADMINS, LOG_CHANNEL, PICS, CUSTOM_FILE_CAPTION, AUTO_DELETE_TIME, AUTO_DELETE, UNIVERSAL_FORCE_SUB_CHANNEL, URL
from utils import is_subscribed_universal, check_tma_verification, get_tma_link, verify_tma_user, is_token_consumed, consume_token, validate_tma_token, is_vip, TMA_TIMEOUT, MongoDict, consume_tma_link, get_tma_cooldown_remaining, schedule_tma_renewal_msg
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto, WebAppInfo
import re
import json
import base64
import time
import string
from shortzy import Shortzy

logger = logging.getLogger(__name__)

CLONE_TOKENS = {}
CLONE_VERIFIED = MongoDict("clone_verifications")
BATCH_FILES = {}

def from_small_caps(text: str) -> str:
    if not isinstance(text, str):
        return text
    small_caps = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    normal_chars = "abcdefghijklmnopqrstuvwxyz"
    trans = str.maketrans(small_caps, normal_chars)
    return text.translate(trans)

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

def get_size(size):
    """Get size in readable format"""

    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

def parse_stars_prices(plans_text):
    prices = {
        "1d": None,
        "1w": None,
        "1m": None,
        "3m": None,
        "6m": None,
        "lifetime": None
    }
    
    if not plans_text:
        return prices
        
    # Remove HTML tags to process clean text
    text = re.sub(r'<[^>]+>', '', plans_text).lower()
    
    # Also handle the small caps unicode characters some users use
    text_raw = re.sub(r'<[^>]+>', '', plans_text)
    
    # Split by lines
    lines = text.split('\n')
    raw_lines = text_raw.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        raw_line = raw_lines[i].strip()
        
        # Find all integers
        numbers = re.findall(r'\b\d+\b', line)
        if not numbers:
            continue
            
        # Check matching keywords in both lowercased and raw lines
        if any(kw in line for kw in ["1 day", "1day", "daily"]) or any(kw in raw_line for kw in ["1 ᴅᴀʏ"]):
            price_candidates = [int(n) for n in numbers if n not in ["1"]]
            if price_candidates:
                prices["1d"] = price_candidates[0]
            elif len(numbers) == 1:
                prices["1d"] = int(numbers[0])
        elif any(kw in line for kw in ["1 week", "1week", "7 days", "7days"]) or any(kw in raw_line for kw in ["1 ᴡᴇᴇᴋ"]):
            price_candidates = [int(n) for n in numbers if n not in ["1", "7"]]
            if price_candidates:
                prices["1w"] = price_candidates[0]
            elif len(numbers) == 1:
                prices["1w"] = int(numbers[0])
        elif any(kw in line for kw in ["1 month", "1month", "30 days", "30days", "monthly"]) or any(kw in raw_line for kw in ["1 ᴍᴏɴᴛʜ"]):
            price_candidates = [int(n) for n in numbers if n not in ["1", "30"]]
            if price_candidates:
                prices["1m"] = price_candidates[0]
            elif len(numbers) == 1:
                prices["1m"] = int(numbers[0])
        elif any(kw in line for kw in ["3 month", "3month", "90 days", "90days"]) or any(kw in raw_line for kw in ["3 ᴍᴏɴᴛʜ"]):
            price_candidates = [int(n) for n in numbers if n not in ["3", "90"]]
            if price_candidates:
                prices["3m"] = price_candidates[0]
            elif len(numbers) == 1:
                prices["3m"] = int(numbers[0])
        elif any(kw in line for kw in ["6 month", "6month", "180 days", "180days", "half year"]) or any(kw in raw_line for kw in ["6 ᴍᴏɴᴛʜ"]):
            price_candidates = [int(n) for n in numbers if n not in ["6", "180"]]
            if price_candidates:
                prices["6m"] = price_candidates[0]
            elif len(numbers) == 1:
                prices["6m"] = int(numbers[0])
        elif any(kw in line for kw in ["lifetime", "life time", "life-time", "forever"]) or any(kw in raw_line for kw in ["ʟɪғᴇᴛɪᴍᴇ"]):
            price_candidates = [int(n) for n in numbers]
            if price_candidates:
                prices["lifetime"] = price_candidates[0]
                
    return prices

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

async def get_invalid_link_btn(client, user_id, data):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    tma_mode = bot_doc.get("tma_mode", False) if bot_doc else False
    shortener_api = bot_doc.get("shortener_api") if bot_doc else None
    if not shortener_api:
        tma_mode = False
    if tma_mode:
        tma_app_url = f"{URL.rstrip('/')}/tma"
        file_data = ""
        if data:
            if data.startswith("unlock-"):
                parts = data.split("-", 4)
                file_data = parts[4] if len(parts) >= 5 else ""
            elif data.startswith("verify-"):
                parts = data.split("-", 3)
                file_data = parts[3] if len(parts) == 4 else ""
            elif not data.startswith("tma-") and not data.startswith("verify-") and not data.startswith("unlock-"):
                file_data = data
        tma_link = await get_tma_link(client, user_id, tma_app_url, file_data=file_data, bot_username=me.username)
        return InlineKeyboardMarkup([[InlineKeyboardButton("Click Here to Get Verification", web_app=WebAppInfo(url=tma_link))]])
    else:
        return InlineKeyboardMarkup([[InlineKeyboardButton("Click Here to Get Verification", url=f"https://t.me/{me.username}?start=true")]])

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    me = client.me or await client.get_me()
    # Clear any stale user state
    await mongo_db.user_states.delete_one({"bot_id": me.id, "user_id": message.from_user.id})
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    
    # Deactivation Check
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    if not await clonedb.is_user_exist(me.id, message.from_user.id):
        await clonedb.add_user(me.id, message.from_user.id)
    
    # Universal Force Sub Check for Clones
    chk = await is_subscribed_universal(client, message)
    if chk == "kicked":
        return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
    
    if type(chk) == list:
        buttons = []
        for channel_id in chk:
            try:
                chat = await client.get_chat(channel_id)
                link = chat.invite_link or f"https://t.me/{chat.username}"
                buttons.append([InlineKeyboardButton("ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=link)])
            except: continue
        buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=true")])
        return await message.reply_text(
            text="<b>ʜᴇʏ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    clone_force_channels = bot_doc.get('force_sub_channels', []) if bot_doc else []
    force_sub_mode = bot_doc.get('force_sub_mode', 'normal') if bot_doc else 'normal'
    
    if clone_force_channels:
        not_joined = []
        
        async def check_sub(ch_id):
            try:
                member = await client.get_chat_member(ch_id, message.from_user.id)
                if member.status == enums.ChatMemberStatus.BANNED:
                    return "kicked"
                if member.status == enums.ChatMemberStatus.LEFT:
                    return ch_id
            except:
                if force_sub_mode == 'joinreq':
                    req = await mongo_db.join_reqs.find_one({"bot_id": me.id, "user_id": message.from_user.id, "channel_id": ch_id})
                    if req: return None
                return ch_id
            return None

        results = await asyncio.gather(*[check_sub(ch) for ch in clone_force_channels])
        if "kicked" in results:
            return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
        
        not_joined = [r for r in results if r is not None]

        if not_joined:
            buttons = []
            for i, channel_id in enumerate(not_joined, start=1):
                try:
                    chat = await client.get_chat(channel_id)
                    if force_sub_mode == 'joinreq':
                        try:
                            inv = await client.create_chat_invite_link(channel_id, creates_join_request=True)
                            link = inv.invite_link
                        except:
                            link = chat.invite_link or (f"https://t.me/{chat.username}" if chat.username else None)
                    else:
                        link = chat.invite_link or f"https://t.me/{chat.username}"
                    
                    if link:
                        buttons.append([InlineKeyboardButton(f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {i} ➔ {chat.title}", url=link)])
                    else:
                        buttons.append([InlineKeyboardButton(f"⚠️ Bot Not Admin in Channel {i}", url=f"https://t.me/{me.username}")])
                except: 
                    buttons.append([InlineKeyboardButton(f"⚠️ Bot Not Admin in Channel {i}", url=f"https://t.me/{me.username}")])
            
            try_url = f"https://t.me/{me.username}?start={message.command[1]}" if len(message.command) > 1 else f"https://t.me/{me.username}?start=true"
            buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=try_url)])
            mode_hint = " (Click to send join request)" if force_sub_mode == 'joinreq' else ""
            return await message.reply_text(
                text=f"<b>📢 ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ(s) ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!{mode_hint}</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    # ──────────────────────────────────────────────────────────────────────

    logger.info(f"Starting file delivery for user {message.from_user.id}")

    # Bot Mode Check (Public/Private)
    bot_mode = bot_doc.get("bot_mode", "public") if bot_doc else "public"
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if bot_mode == "private" and message.from_user.id != owner_id and message.from_user.id not in mods:
        if len(message.command) == 2:
            return await message.reply_text("<b>🔒 This bot is in Private Mode. Only owner and moderators can access files.</b>")
    
    if len(message.command) != 2 or message.command[1] == "true":
        portal_url = f"{URL.rstrip('/')}/portal?uid={message.from_user.id}&bot={me.username}"
        buttons = [[
            InlineKeyboardButton('Viral Videos 💦', web_app=WebAppInfo(url=portal_url))
        ],[
            InlineKeyboardButton('⚙️ sᴇᴛᴛɪɴɢs', callback_data='settings'),
            InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ᴄʟᴏɴᴇ', url=f'https://t.me/{BOT_USERNAME}?start=clone')
        ],[
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        # Custom Start Message
        start_txt = bot_doc.get("start_text") if bot_doc else None
        if not start_txt:
            start_txt = script.CLONE_START_TXT
        try:
            start_txt = start_txt.format(message.from_user.mention, me.mention, mention=message.from_user.mention, mention2=me.mention)
        except: pass
            
        start_photo = bot_doc.get("start_photo") if bot_doc else None
        
        # Only use the stored photo if it's a URL (http/https).
        # Telegram file_ids from other bots don't work cross-bot.
        if start_photo and not start_photo.startswith("http"):
            start_photo = None  # Reset - will fall back to PICS
        
        if not start_photo:
            start_photo = random.choice(PICS)
            
        sent = False
        if start_photo:
            try:
                await message.reply_photo(
                    photo=start_photo,
                    caption=start_txt,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                sent = True
            except Exception as e:
                logger.error(f"Clone bot start_photo error: {e} | photo value: {start_photo}")
        if not sent:
            await message.reply_text(
                text=start_txt,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        return

    data = message.command[1]
    logger.info(f"Processing payload data: {data}")

    # Check Paid Link
    if data not in ["joinref", "clone"] and not data.startswith("ref_") and not data.startswith("verifyclone_"):
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        paid_links_enabled = bot_doc.get("paid_links", False) if bot_doc else False
        user_is_vip = await is_vip(me.id, message.from_user.id)
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        is_owner_or_mod = (message.from_user.id == owner_id or message.from_user.id in mods)
        
        if paid_links_enabled and not user_is_vip and not is_owner_or_mod:
            check_payload = data
            if data.startswith("unlock-"):
                parts = data.split("-", 4)
                if len(parts) >= 5:
                    check_payload = parts[4]
            
            # Convert small caps to normal lowercase to handle manual inputs
            check_payload = from_small_caps(check_payload)
            
            # Check if this user has already paid for/unlocked this specific link (case-insensitive)
            user_unlocked = await mongo_db.paid_unlocks.find_one({
                "bot_id": me.id,
                "user_id": message.from_user.id,
                "payload": re.compile(f"^{re.escape(check_payload)}$", re.IGNORECASE)
            })
            
            if not user_unlocked:
                paid_doc = await mongo_db.paid_links.find_one({
                    "bot_id": me.id, 
                    "payload": re.compile(f"^{re.escape(check_payload)}$", re.IGNORECASE)
                })
                
                title = "Paid File"
                price = "Paid Link"
                qr_file_id = None
                
                if paid_doc:
                    title = paid_doc.get("title", "Paid File")
                    price = paid_doc.get("price", "N/A")
                    qr_file_id = paid_doc.get("qr_file_id")
                else:
                    # Look up fallback details from plans_config
                    plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
                    if plan_cfg:
                        qr_file_id = plan_cfg.get("alt_payment_qr") or plan_cfg.get("upi_qr") or plan_cfg.get("paypal_qr")
                
                caption = f"💰 **Paid File: {title}**\n💵 **Price:** {price}\n\nPlease scan the QR code to pay, and tap the button below to submit your payment screenshot."
                btn = [[InlineKeyboardButton("📤 Submit Screenshot", callback_data=f"sub_pay_{check_payload}")]]
                if qr_file_id:
                    return await message.reply_photo(photo=qr_file_id, caption=caption, reply_markup=InlineKeyboardMarkup(btn))
                else:
                    return await message.reply_text(text=caption, reply_markup=InlineKeyboardMarkup(btn))

    # ── Referral Campaign Start Handler ──
    if data == "joinref":
        from clone_plugins.db_referral import is_campaign_active
        if not await is_campaign_active(me.id):
            return await message.reply_text("<b>❌ No active referral campaign is running at the moment.</b>")
        
        buttons = [
            [InlineKeyboardButton("✅ Confirm & Join", callback_data="confirm_join_ref")],
            [InlineKeyboardButton("❌ Cancel", callback_data="close_data")]
        ]
        return await message.reply_text(
            text="<b>📢 Referral Program</b>\n\nAre you sure you want to join this referral program and generate your own referral link?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    if data.startswith("ref_"):
        try:
            referrer_id = int(data.split("_")[1])
        except Exception:
            return await message.reply_text("<b>❌ Invalid referral link.</b>")
            
        from clone_plugins.db_referral import is_campaign_active, get_campaign, add_referral
        
        if not await is_campaign_active(me.id):
            return await message.reply_text("<b>❌ This referral campaign has expired or is inactive.</b>")
            
        if referrer_id == message.from_user.id:
            return await message.reply_text("<b>❌ You cannot refer yourself!</b>")
            
        camp = await get_campaign(me.id)
        channel_id = camp.get("channel") if camp else None
        if channel_id:
            try:
                member = await client.get_chat_member(channel_id, message.from_user.id)
                if member.status in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT]:
                    chat = await client.get_chat(channel_id)
                    link = chat.invite_link or (f"https://t.me/{chat.username}" if chat.username else None)
                    buttons = [
                        [InlineKeyboardButton("📢 Join Campaign Channel", url=link)],
                        [InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{me.username}?start=ref_{referrer_id}")]
                    ]
                    return await message.reply_text(
                        text=f"<b>📢 To support the referrer, you must join our campaign channel first!</b>",
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
            except Exception as e:
                logger.error(f"Error checking referral channel subscription: {e}")
                
        success = await add_referral(me.id, message.from_user.id, referrer_id)
        if success:
            try:
                await client.send_message(
                    chat_id=referrer_id,
                    text=f"<b>🎉 New Referral!</b>\n\nA user has successfully joined using your link."
                )
            except Exception:
                pass
            await message.reply_text("<b>✅ You have successfully supported your referrer!</b>")
        else:
            await message.reply_text("<b>✅ You have already supported your referrer!</b>")
        return
    # ─────────────────────────────────────

    is_unlocked = False
    if data.split("-", 1)[0] == "unlock":
        parts = data.split("-", 4)
        if len(parts) >= 5:
            _, userid_str, ts, sig, file_data = parts
            token = f"{ts}-{sig}"
            if str(message.from_user.id) == userid_str:
                if validate_tma_token(message.from_user.id, token):
                    if await is_token_consumed(token):
                        reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
                        return await message.reply_text(text="<b>This link is not valid, either it is used or broken.</b>", reply_markup=reply_markup, protect_content=True)

                    # Bypass Check: If verified in less than 2.5 min (150 seconds)
                    try:
                        ts_val = int(ts)
                        elapsed = time.time() - ts_val
                        if elapsed < 150:
                            await consume_token(token)
                            me = client.me or await client.get_me()
                            plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
                            plan_enabled = bot_doc.get("plan_enabled", True) if bot_doc else True
                            upsell_btn = []
                            if plan_cfg and plan_enabled:
                                upsell_btn.append([InlineKeyboardButton("💳 Get VIP Plan — Watch Ad-Free!", callback_data="buy_plan")])
                            else:
                                upsell_btn.append([InlineKeyboardButton("💳 Get VIP Plan — Watch Ad-Free!", url=f"https://t.me/{me.username}?start=true")])
                            return await message.reply_text(
                                text=script.TMA_BYPASS_WARNING_TEXT.format(message.from_user.mention),
                                reply_markup=InlineKeyboardMarkup(upsell_btn) if upsell_btn else None,
                                protect_content=True
                            )
                    except Exception as e:
                        logger.error(f"Error in bypass check: {e}")

                    await consume_token(token)
                    is_unlocked = True
                    data = file_data
                    await verify_tma_user(message.from_user.id, token, bot_id=me.id)
                    # Schedule reminder after 1 hour (3600 seconds)
                    asyncio.create_task(schedule_tma_renewal_msg(client, message.from_user.id, bot_id=me.id, delay=3600))
                    await message.reply_text(
                        text=script.TMA_VERIFIED_TEXT.format(message.from_user.mention),
                        protect_content=True
                    )
                else:
                    reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
                    return await message.reply_text(text="<b>This link is not valid, either it is used or broken.</b>", reply_markup=reply_markup, protect_content=True)
            else:
                return await message.reply_text(text="<b>This verification link belongs to another user!</b>", protect_content=True)
        else:
            reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
            return await message.reply_text(text="<b>This link is not valid, either it is used or broken.</b>", reply_markup=reply_markup, protect_content=True)

    if data.split("-", 1)[0] == "tma":
        parts = data.split("-")
        if len(parts) >= 3:
            tma_uid = int(parts[1])
            tma_token = "-".join(parts[2:])
            if message.from_user.id != tma_uid:
                reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
                return await message.reply_text(
                    text="<b>This link is not valid, either it is used or broken.</b>",
                    reply_markup=reply_markup,
                    protect_content=True
                )
            
            # Bypass Check: If verified in less than 2.5 min (150 seconds)
            try:
                ts_val = int(tma_token.split("-")[0])
                elapsed = time.time() - ts_val
                if elapsed < 150:
                    await consume_token(tma_token)
                    me = client.me or await client.get_me()
                    plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
                    plan_enabled = bot_doc.get("plan_enabled", True) if bot_doc else True
                    upsell_btn = []
                    if plan_cfg and plan_enabled:
                        upsell_btn.append([InlineKeyboardButton("💳 Get VIP Plan — Watch Ad-Free!", callback_data="buy_plan")])
                    else:
                        upsell_btn.append([InlineKeyboardButton("💳 Get VIP Plan — Watch Ad-Free!", url=f"https://t.me/{me.username}?start=true")])
                    return await message.reply_text(
                        text=script.TMA_BYPASS_WARNING_TEXT.format(message.from_user.mention),
                        reply_markup=InlineKeyboardMarkup(upsell_btn) if upsell_btn else None,
                        protect_content=True
                    )
            except Exception as e:
                logger.error(f"Error in bypass check: {e}")

            if await is_token_consumed(tma_token):
                reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
                return await message.reply_text(
                    text="<b>This link is not valid, either it is used or broken.</b>",
                    reply_markup=reply_markup,
                    protect_content=True
                )

            ok = await verify_tma_user(tma_uid, tma_token, bot_id=me.id)
            if ok:
                await consume_token(tma_token)
                # Schedule reminder after 1 hour (3600 seconds)
                asyncio.create_task(schedule_tma_renewal_msg(client, tma_uid, bot_id=me.id, delay=3600))
                await message.reply_text(
                    text=script.TMA_VERIFIED_TEXT.format(message.from_user.mention),
                    protect_content=True
                )
            else:
                reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
                await message.reply_text(
                    text="<b>This link is not valid, either it is used or broken.</b>",
                    reply_markup=reply_markup,
                    protect_content=True
                )
        return

    if data.startswith("verify-"):
        logger.info("Detected verification payload")
        parts = data.split("-", 3)
        if len(parts) >= 3:
            _, userid, token = parts[:3]
            file_data = parts[3] if len(parts) == 4 else None
        else:
            reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
            return await message.reply_text(
                text="<b>This link is not valid, either it is used or broken.</b>",
                reply_markup=reply_markup,
                protect_content=True
            )
            
        if str(message.from_user.id) != str(userid):
            reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
            return await message.reply_text(
                text="<b>This link is not valid, either it is used or broken.</b>",
                reply_markup=reply_markup,
                protect_content=True
            )
        
        key = f"{me.id}_{userid}"
        if key in CLONE_TOKENS and token in CLONE_TOKENS[key] and not CLONE_TOKENS[key][token]:
            CLONE_TOKENS[key][token] = True
            CLONE_VERIFIED[key] = time.time()
            await message.reply_text(f"<b>Hey {message.from_user.mention}, You are successfully verified!\nNow you have unlimited access for the validity period.</b>", protect_content=True)
            if file_data:
                logger.info(f"Verification success, redirecting to file: {file_data}")
                message.command[1] = file_data
                return await start(client, message)
            return
        else:
            reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
            return await message.reply_text(
                text="<b>This link is not valid, either it is used or broken.</b>",
                reply_markup=reply_markup,
                protect_content=True
            )

    if data.startswith("BATCH-"):
        logger.info("Detected BATCH payload")
        try:
            # Plan and TMA Verification Check for Batch
            tma_mode = bot_doc.get("tma_mode", False) if bot_doc else False
            shortener_api = bot_doc.get("shortener_api") if bot_doc else None
            if not shortener_api:
                tma_mode = False
            user_is_vip = await is_vip(me.id, message.from_user.id)
            plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
            plan_enabled = bot_doc.get("plan_enabled", True) if bot_doc else True
            is_verified = False
            
            if plan_cfg and plan_enabled and not user_is_vip:
                if tma_mode:
                    if not await check_tma_verification(message.from_user.id, bot_id=me.id):
                        ads_today = 0
                        try:
                            import pytz
                            from datetime import datetime
                            tz = pytz.timezone('Asia/Kolkata')
                            today_str = datetime.now(tz).strftime('%Y-%m-%d')
                            doc = await mongo_db.tma_stats.find_one({"bot_id": me.id, "user_id": message.from_user.id, "date": today_str})
                            if doc:
                                ads_today = doc.get("ads_watched", 0)
                        except Exception as e:
                            logger.error(f"Error checking daily ads: {e}")

                        tma_app_url = f"{URL.rstrip('/')}/tma"
                        tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data, bot_username=me.username)
                        btn = [
                            [InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))],
                            [InlineKeyboardButton("💳 Buy Plan (Skip Ads)", callback_data="buy_plan")]
                        ]
                        
                        if ads_today > 0:
                            unlock_text = f"<b>⚠️ 3 File Limit is Over!</b>\n\nHey {message.from_user.mention}, your 3 free files limit is over. Please watch another ad to unlock 3 more files, or purchase a VIP plan."
                        else:
                            unlock_text = script.TMA_UNLOCK_TEXT.format(message.from_user.mention)

                        return await message.reply_text(
                            text=unlock_text,
                            protect_content=True,
                            reply_markup=InlineKeyboardMarkup(btn)
                        )
                    else:
                        is_verified = True
                else:
                    btn = [[InlineKeyboardButton("💳 Buy VIP Plan to Unlock", callback_data="buy_plan")]]
                    return await message.reply_text(
                        text=f"<b>🔒 Hey {message.from_user.mention}, this file is locked!\n\nPlease purchase a VIP Plan to get instant access to files.</b>",
                        protect_content=True,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
            elif tma_mode and not user_is_vip:
                if not await check_tma_verification(message.from_user.id, bot_id=me.id):
                    ads_today = 0
                    try:
                        import pytz
                        from datetime import datetime
                        tz = pytz.timezone('Asia/Kolkata')
                        today_str = datetime.now(tz).strftime('%Y-%m-%d')
                        doc = await mongo_db.tma_stats.find_one({"bot_id": me.id, "user_id": message.from_user.id, "date": today_str})
                        if doc:
                            ads_today = doc.get("ads_watched", 0)
                    except Exception as e:
                        logger.error(f"Error checking daily ads: {e}")

                    tma_app_url = f"{URL.rstrip('/')}/tma"
                    tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data, bot_username=me.username)
                    btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))]]
                    
                    if ads_today > 0:
                        unlock_text = f"<b>⚠️ 3 File Limit is Over!</b>\n\nHey {message.from_user.mention}, your 3 free files limit is over. Please watch another ad to unlock 3 more files, or purchase a VIP plan."
                    else:
                        unlock_text = script.TMA_UNLOCK_TEXT.format(message.from_user.mention)

                    return await message.reply_text(
                        text=unlock_text,
                        protect_content=True,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                else:
                    is_verified = True
                if not is_verified and not is_unlocked:
                    tma_app_url = f"{URL.rstrip('/')}/tma"
                    tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data, bot_username=me.username)
                    btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))]]
                    return await message.reply_text(
                        text=script.TMA_UNLOCK_TEXT.format(message.from_user.mention),
                        protect_content=True,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                else:
                    is_verified = True
            
            # Deliver files if: TMA is off (no ad wall), OR user passed TMA, OR user already unlocked, OR user is VIP
            # Also deliver if plan is disabled (plan_enabled=False) regardless of TMA state
            if not tma_mode or is_verified or is_unlocked or user_is_vip or not plan_enabled:
                if tma_mode and not user_is_vip:
                    await consume_tma_link(message.from_user.id, bot_id=me.id)
                sts = await message.reply("<b>🔺 ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... ɢᴇᴛᴛɪɴɢ ʙᴀᴛᴄʜ ғɪʟᴇs</b>")
                batch_file_id = data.split("-", 1)[1]
                msgs = BATCH_FILES.get(batch_file_id)
                if not msgs:
                    from TechVJ.bot import StreamBot
                    decode_file_id = base64.urlsafe_b64decode(batch_file_id + "=" * (-len(batch_file_id) % 4)).decode("ascii")
                    # Use Main Bot to get the message from Log Channel
                    msg = await StreamBot.get_messages(LOG_CHANNEL, int(decode_file_id))
                    media = getattr(msg, msg.media.value)
                    # Download the JSON file using Main Bot
                    path = await StreamBot.download_media(media.file_id)
                    with open(path, "r") as f:
                        msgs = json.load(f)
                    os.remove(path)
                    BATCH_FILES[batch_file_id] = msgs
                
                for m_data in msgs:
                    try:
                        c_id = m_data.get("channel_id")
                        m_id = m_data.get("msg_id")
                        is_nofwd = (bot_doc.get("no_forward", False) if bot_doc else False) and not user_is_vip
                        reply_markup = InlineKeyboardMarkup([[
                            InlineKeyboardButton("Jᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/viralverse0909")
                        ]])
                        
                        stream_mode = bot_doc.get("stream_mode", False) if bot_doc else False
                        if stream_mode:
                            try:
                                info = await client.get_messages(c_id, int(m_id))
                                if info.video or info.document:
                                    if int(c_id) == int(LOG_CHANNEL):
                                        log_msg_id = m_id
                                    else:
                                        from TechVJ.bot import StreamBot
                                        sent_msg = await StreamBot.send_cached_media(chat_id=LOG_CHANNEL, file_id=getattr(info, info.media.value).file_id)
                                        log_msg_id = sent_msg.id
                                    
                                    from TechVJ.bot import StreamBot
                                    log_msg = await StreamBot.get_messages(LOG_CHANNEL, log_msg_id)
                                    
                                    from urllib.parse import quote_plus
                                    from TechVJ.utils.file_properties import get_name, get_hash
                                    
                                    me = client.me or await client.get_me()
                                    stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}&bot={me.username}&user={message.from_user.id}"
                                    download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}&bot={me.username}&user={message.from_user.id}"
                                    
                                    if stream and download and (stream.startswith("http://") or stream.startswith("https://")) and (download.startswith("http://") or download.startswith("https://")):
                                        button = [[
                                            InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
                                            InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
                                        ],[
                                            InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
                                        ],[
                                            InlineKeyboardButton("Jᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/viralverse0909")
                                        ]]
                                        reply_markup = InlineKeyboardMarkup(button)
                            except Exception as e:
                                logger.error(f"Clone batch stream button error: {e}")
                        
                        await client.copy_message(
                            chat_id=message.from_user.id, 
                            from_chat_id=c_id, 
                            message_id=m_id,
                            reply_markup=reply_markup,
                            protect_content=is_nofwd
                        )
                    except Exception as e:
                        logger.error(f"Batch copy error: {e}")
                
                await sts.delete()
                
                try:
                    base_url = URL.strip()
                    if not base_url.startswith("https://") and not base_url.startswith("http://"):
                        base_url = "https://" + base_url
                    elif base_url.startswith("http://"):
                        base_url = base_url.replace("http://", "https://")
                    portal_url = f"{base_url.rstrip('/')}/portal?uid={message.from_user.id}&bot={me.username}"
                    
                    await client.send_message(
                        chat_id=message.from_user.id,
                        text="<b>🍿 naya taza maal dekhlo</b>",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("💦 Tᴀᴢᴀ Mᴀᴀʟ 💦", web_app=WebAppInfo(url=portal_url))
                        ]])
                    )
                except Exception as final_msg_err:
                    logger.error(f"Error sending final portal link message: {final_msg_err}")

                # ── VIP Upsell for TMA-verified non-VIP users ──
                if tma_mode and not user_is_vip:
                    try:
                        plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
                        plan_enabled = bot_doc.get("plan_enabled", True) if bot_doc else True
                        upsell_btn = []
                        if plan_cfg and plan_enabled:
                            upsell_btn.append([InlineKeyboardButton("💳 Get VIP Plan — Watch Ad-Free!", callback_data="buy_plan")])
                        else:
                            upsell_btn.append([InlineKeyboardButton("💳 Get VIP Plan — Watch Ad-Free!", url=f"https://t.me/{me.username}?start=true")])
                        await client.send_message(
                            chat_id=message.from_user.id,
                            text=script.TMA_UPSELL_TEXT,
                            reply_markup=InlineKeyboardMarkup(upsell_btn) if upsell_btn else None,
                            parse_mode=enums.ParseMode.HTML
                        )
                    except Exception:
                        pass
                return
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            return await message.reply_text(f"<b>❌ Error processing batch: {e}</b>")

    try:
        decoded_string = base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("ascii")
        pre, decoded_id = decoded_string.split("_", 1)
        logger.info(f"Decoded data: pre={pre}, id={decoded_id}")
    except Exception as e:
        logger.info(f"Decoding failed (using raw data): {e}")
        # Fallback for old unencoded links
        try:
            pre, decoded_id = data.split('_', 1)
        except:
            decoded_id = data
            pre = ""
    
    # Try fetching the file_id from DB using the short ID
    logger.info(f"Searching DB for decoded_id: {decoded_id}")
    file_doc = await mongo_db.clone_files.find_one({"_id": decoded_id})
    if file_doc:
        file_id = file_doc["file_id"]
        logger.info(f"Found file in DB. file_id exists.")
    else:
        # Fallback to older links where raw file_id was encoded
        file_id = decoded_id
        logger.info("File not found in DB, using decoded_id as file_id")

    # Get owner's caption prefix from DB
    bot_owner = bot_doc
    owner_id = int(bot_owner['user_id']) if bot_owner else None
    caption_prefix = ""
    if owner_id:
        owner_data = await get_user(me.id, owner_id)
        caption_prefix = owner_data.get("caption_prefix", "").strip()
    
    logger.info(f"Final file_id to send: {file_id[:20]}...")

    # Plan and TMA Verification Check
    tma_mode = bot_owner.get("tma_mode", False) if bot_owner else False
    shortener_api = bot_owner.get("shortener_api") if bot_owner else None
    if not shortener_api:
        tma_mode = False
    user_is_vip = await is_vip(me.id, message.from_user.id)
    plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
    plan_enabled = bot_owner.get("plan_enabled", True) if bot_owner else True
    logger.info(f"TMA mode: {tma_mode}, User VIP: {user_is_vip}, Plan configured: {plan_cfg is not None}, Plan enabled: {plan_enabled}")
    
    if plan_cfg and plan_enabled and not user_is_vip:
        if tma_mode:
            ads_today = 0
            try:
                import pytz
                from datetime import datetime
                tz = pytz.timezone('Asia/Kolkata')
                today_str = datetime.now(tz).strftime('%Y-%m-%d')
                doc = await mongo_db.tma_stats.find_one({"bot_id": me.id, "user_id": message.from_user.id, "date": today_str})
                if doc:
                    ads_today = doc.get("ads_watched", 0)
            except Exception as e:
                logger.error(f"Error checking daily ads: {e}")

            if ads_today >= 3:
                btn = [[InlineKeyboardButton("💳 Buy Plan (Skip Ads)", callback_data="buy_plan")]]
                return await message.reply_text(
                    text="<b>⚠️ Maximum Ads Shown!</b>\n\nYou have already watched your maximum limit of 3 ads for today. Please wait until tomorrow or purchase a VIP Plan.",
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            bot_tma_timeout = bot_owner.get("token_timeout", 0) if bot_owner else 0
            is_verified = await check_tma_verification(message.from_user.id, timeout=bot_tma_timeout, bot_id=me.id)
            if not is_verified and not is_unlocked:
                tma_app_url = f"{URL.rstrip('/')}/tma"
                tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data, bot_username=me.username)
                btn = [
                    [InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))],
                    [InlineKeyboardButton("💳 Buy Plan (Skip Ads)", callback_data="buy_plan")]
                ]
                return await message.reply_text(
                    text=script.TMA_UNLOCK_TEXT.format(message.from_user.mention),
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
        else:
            btn = [[InlineKeyboardButton("💳 Buy VIP Plan to Unlock", callback_data="buy_plan")]]
            return await message.reply_text(
                text=f"<b>🔒 Hey {message.from_user.mention}, this file is locked!\n\nPlease purchase a VIP Plan to get instant access to files.</b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
    elif tma_mode and not user_is_vip:
        if not await check_tma_verification(message.from_user.id, bot_id=me.id):
            ads_today = 0
            try:
                import pytz
                from datetime import datetime
                tz = pytz.timezone('Asia/Kolkata')
                today_str = datetime.now(tz).strftime('%Y-%m-%d')
                doc = await mongo_db.tma_stats.find_one({"bot_id": me.id, "user_id": message.from_user.id, "date": today_str})
                if doc:
                    ads_today = doc.get("ads_watched", 0)
            except Exception as e:
                logger.error(f"Error checking daily ads: {e}")

            tma_app_url = f"{URL.rstrip('/')}/tma"
            tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data, bot_username=me.username)
            btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))]]
            
            if ads_today > 0:
                unlock_text = f"<b>⚠️ 3 File Limit is Over!</b>\n\nHey {message.from_user.mention}, your 3 free files limit is over. Please watch another ad to unlock 3 more files, or purchase a VIP plan."
            else:
                unlock_text = script.TMA_UNLOCK_TEXT.format(message.from_user.mention)

            return await message.reply_text(
                text=unlock_text,
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        else:
            is_verified = True
    if tma_mode and not user_is_vip:
        await consume_tma_link(message.from_user.id, bot_id=me.id)

    logger.info("Proceeding to send_cached_media...")
    try:
        is_nofwd = (bot_owner.get("no_forward", False) if bot_owner else False) and not user_is_vip
        is_stream = bot_owner.get("stream_mode", False) if bot_owner else False
        
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("Jᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/viralverse0909")
        ]])
        
        msg = None
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                reply_markup=reply_markup,
                protect_content=is_nofwd
            )
            logger.info(f"send_cached_media successful (protect_content={is_nofwd})")
        except Exception as e1:
            logger.warning(f"Clone bot send_cached_media failed: {e1}. Trying copy_message fallback...")
            if file_doc and "chat_id" in file_doc and "message_id" in file_doc:
                try:
                    msg = await client.copy_message(
                        chat_id=message.from_user.id,
                        from_chat_id=int(file_doc["chat_id"]),
                        message_id=int(file_doc["message_id"]),
                        reply_markup=reply_markup,
                        protect_content=is_nofwd
                    )
                    logger.info("Fallback copy_message via clone bot successful")
                except Exception as e2:
                    logger.warning(f"Clone bot copy_message failed: {e2}")
        
        if not msg or getattr(msg, "empty", False) or not getattr(msg, "media", None):
            return await message.reply_text("<b>❌ Error sending file! The file might have been deleted from Telegram (e.g. copyright strike) or is no longer available.</b>")
        
        # Send portal link immediately here to bypass downstream exceptions
        try:
            me = client.me or await client.get_me()
            base_url = URL.strip()
            if not base_url.startswith("https://") and not base_url.startswith("http://"):
                base_url = "https://" + base_url
            elif base_url.startswith("http://"):
                base_url = base_url.replace("http://", "https://")
            portal_url = f"{base_url.rstrip('/')}/portal?uid={message.from_user.id}&bot={me.username}"
            
            await client.send_message(
                chat_id=message.from_user.id,
                text="<b>🍿 naya taza maal dekhlo</b>",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💦 Tᴀᴢᴀ Mᴀᴀʟ 💦", web_app=WebAppInfo(url=portal_url))
                ]])
            )
        except Exception as final_msg_err:
            logger.error(f"Error sending final portal link message: {final_msg_err}")
    except Exception as e:
        logger.error(f"Clone bot send_cached_media error for file_id {file_id}: {e}")
        return await message.reply_text(f"<b>❌ Error sending file! The file ID might be invalid or generated by a different bot.\n\nError: <code>{e}</code></b>")
        
    try:
        filetype = msg.media
        file = getattr(msg, filetype.value)
        old_title = getattr(file, "file_name", "") or ""
        clean_name = old_title
        for c in ["[", "]", "(", ")"]:
            clean_name = clean_name.replace(c, "")
        clean_name = ' '.join(filter(lambda x: not x.startswith('@') and not x.startswith('http') and not x.startswith('www.'), clean_name.split()))
        title = (caption_prefix + ' ' + clean_name).strip() if caption_prefix else clean_name
        size_bytes = getattr(file, "file_size", 0)
        size = get_size(size_bytes)
        
        if file_doc and ("file_size" not in file_doc or "chat_id" not in file_doc or "message_id" not in file_doc):
            update_fields = {}
            if "file_size" not in file_doc:
                update_fields["file_size"] = size_bytes
            if "chat_id" not in file_doc:
                update_fields["chat_id"] = message.from_user.id
            if "message_id" not in file_doc:
                update_fields["message_id"] = msg.id
            
            try:
                await mongo_db.clone_files.update_one(
                    {"_id": decoded_id},
                    {"$set": update_fields}
                )
                logger.info(f"Updated metadata for clone file {decoded_id}: size={size_bytes}, chat_id={message.from_user.id}, message_id={msg.id}")
            except Exception as update_err:
                logger.error(f"Failed to update clone_files metadata: {update_err}")
                
        f_caption = f"<code>{title}</code>" if title else ""
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
            except:
                pass
        
        if is_stream:
            try:
                from urllib.parse import quote_plus
                from pyrogram.file_id import FileId
                
                log_msg_id = file_doc.get("log_msg_id") if file_doc else None
                parsed_file_id = FileId.decode(file_id)
                secure_hash = decoded_id[:6]
                setattr(parsed_file_id, "unique_id", secure_hash + "xxxxx")
                
                stream_id = str(log_msg_id) if log_msg_id else decoded_id
                me = client.me or await client.get_me()
                
                stream = f"{URL}watch/{stream_id}/{quote_plus(clean_name)}?hash={secure_hash}&bot={me.username}&user={message.from_user.id}"
                download = f"{URL}{stream_id}/{quote_plus(clean_name)}?hash={secure_hash}&bot={me.username}&user={message.from_user.id}"
                
                button = [[
                    InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
                    InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
                ],[
                    InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
                ],[
                    InlineKeyboardButton("Jᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/viralverse0909")
                ]]
                reply_markup = InlineKeyboardMarkup(button)
            except Exception as e:
                logger.error(f"Error generating stream links for clone: {e}")

        if f_caption:
            await msg.edit_caption(caption=f_caption, reply_markup=reply_markup)
        else:
            await msg.edit_reply_markup(reply_markup=reply_markup)
        
        # Dynamic Auto Delete
        is_autodel = bot_owner.get("auto_delete_enabled", True) if bot_owner else True
        if is_autodel:
            del_time = bot_owner.get("auto_delete_time", 5) if bot_owner else 5
            k = await msg.reply(f"<b><u>❗️❗️❗️IMPORTANT❗️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{del_time} mins</u> 🫥 <i>(Due to Copyright Issues)</i>.\n\nPlease forward this File/Video to your Saved Messages and Start Download there</b>",quote=True)
            
            async def auto_delete_task(m, warning_msg, delay):
                await asyncio.sleep(delay * 60)
                try:
                    await m.delete()
                    await warning_msg.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
                except: pass
            asyncio.create_task(auto_delete_task(msg, k, del_time))

        # ── VIP Upsell for TMA-verified non-VIP users ──
        tma_mode_check = bot_owner.get("tma_mode", False) if bot_owner else False
        shortener_api = bot_owner.get("shortener_api") if bot_owner else None
        if not shortener_api:
            tma_mode_check = False
        user_vip_check = await is_vip(me.id, message.from_user.id)
        if tma_mode_check and not user_vip_check:
            try:
                plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
                plan_enabled = bot_owner.get("plan_enabled", True) if bot_owner else True
                upsell_btn = []
                if plan_cfg and plan_enabled:
                    upsell_btn.append([InlineKeyboardButton("💳 Get VIP Plan — Watch Ad-Free!", callback_data="buy_plan")])
                else:
                    upsell_btn.append([InlineKeyboardButton("💳 Get VIP Plan — Watch Ad-Free!", url=f"https://t.me/{me.username}?start=true")])
                await client.send_message(
                    chat_id=message.from_user.id,
                    text=script.TMA_UPSELL_TEXT,
                    reply_markup=InlineKeyboardMarkup(upsell_btn) if upsell_btn else None,
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception:
                pass
        return
    except Exception as e:
        logger.error(f"Clone bot caption/auto-delete error: {e}")

@Client.on_message(filters.command("setting") & filters.private & filters.incoming)
async def settings_command(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    # Owner/Moderator/Admin check
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can access settings.</b>")

    # Force Subscribe Check
    chk_u = await is_subscribed_universal(client, message)
    if chk_u == "kicked" or type(chk_u) == list:
        return await start(client, message)

    user_id = message.from_user.id
    user = await get_user(me.id, user_id)
    prefix = user.get("caption_prefix", "") or "<i>Not set</i>"
    tma_mode = bot_doc.get("tma_mode", False) if bot_doc else False
    tma_status = "Enabled 🟢" if tma_mode else "Disabled 🔴"
    plan_enabled = bot_doc.get("plan_enabled", True) if bot_doc else True
    plan_status = "Enabled 🟢" if plan_enabled else "Disabled 🔴"
    stream_mode = bot_doc.get("stream_mode", False) if bot_doc else False
    stream_status = "Enabled 🟢" if stream_mode else "Disabled 🔴"
    paid_links = bot_doc.get("paid_links", False) if bot_doc else False
    paid_status = "Enabled 🟢" if paid_links else "Disabled 🔴"
    
    buttons = [[
        InlineKeyboardButton('📝 sᴇᴛ ᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx', callback_data='set_caption'),
        InlineKeyboardButton(f"TMA Ads: {'ON 🟢' if tma_mode else 'OFF 🔴'}", callback_data="toggle_tma")
    ],[
        InlineKeyboardButton('💳 Configure Plan', callback_data='setplan'),
        InlineKeyboardButton(f"VIP Plan: {'ON 🟢' if plan_enabled else 'OFF 🔴'}", callback_data="toggle_plan")
    ],[
        InlineKeyboardButton(f"Stream: {'ON 🟢' if stream_mode else 'OFF 🔴'}", callback_data="toggle_stream"),
        InlineKeyboardButton(f"Paid Links: {'ON 🟢' if paid_links else 'OFF 🔴'}", callback_data="toggle_paid")
    ],[
        InlineKeyboardButton('💬 ᴄʜᴀᴛʙox', url='https://t.me/+cFO-dJGWlCMzNGRl'),
        InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
    ],[
        InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
        InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
    ],[
        InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
    ]]
    
    from TechVJ.bot import StreamBot
    from clone_plugins.db_referral import is_participant
    main_bot_username = (await StreamBot.get_me()).username
    is_owner = bot_doc and (int(bot_doc.get('user_id', 0)) == message.from_user.id or message.from_user.id in ADMINS)
    
    if is_owner:
        buttons.insert(0, [InlineKeyboardButton('⚙️ Bot Settings', url=f"https://t.me/{main_bot_username}?start=manageclone_{me.id}")])
        buttons.insert(3, [InlineKeyboardButton('📢 Referral Campaign', callback_data='ref_campaign_menu')])
    elif await is_participant(me.id, message.from_user.id):
        buttons.insert(3, [InlineKeyboardButton('🔗 My Referral Link', callback_data='get_user_ref_link')])
        
    buttons.insert(0, [InlineKeyboardButton('⚙️ TMA Ads Setting', url=f"https://t.me/{main_bot_username}?start=verifyclone_{me.id}")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴛᴍᴀ ᴀᴅs: <code>{tma_status}</code>\nᴠɪᴘ ᴘʟᴀɴ: <code>{plan_status}</code>\nsᴛʀᴇᴀᴍ ᴍᴏᴅᴇ: <code>{stream_status}</code>\nᴘᴀɪᴅ ʟɪɴᴋs: <code>{paid_status}</code>\nᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx: {prefix}</b>",
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )



@Client.on_message(filters.command('setcaption') & filters.private)
async def set_caption_handler(client, m: Message):
    """Allow clone bot owner to set a custom prefix added to all file names.
    Usage: /setcaption @MyChannel
    To remove: /setcaption off
    """
    me = client.me or await client.get_me()
    bot_owner = await mongo_db.bots.find_one({'bot_id': me.id})
    
    if bot_owner and bot_owner.get("is_deactivated", False):
        return await m.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    owner_id = int(bot_owner.get("user_id", 0)) if bot_owner else 0
    mods = bot_owner.get("moderators", []) if bot_owner else []
    if m.from_user.id != owner_id and m.from_user.id not in mods and m.from_user.id not in ADMINS:
        return await m.reply("<b>❌ Only the bot owner can use this command.</b>")

    cmd = m.command
    if len(cmd) == 1:
        user = await get_user(me.id, m.from_user.id)
        current = user.get("caption_prefix", "") or "<i>Not set</i>"
        return await m.reply(
            f"<b>📝 Caption Prefix</b>\n\n"
            f"Current prefix: <code>{current}</code>\n\n"
            f"<b>Usage:</b> <code>/setcaption @YourName</code>\n"
            f"<b>To remove:</b> <code>/setcaption off</code>"
        )
    prefix = cmd[1].strip()
    if prefix.lower() == "off":
        await update_user_info(me.id, m.from_user.id, {"caption_prefix": ""})
        return await m.reply("<b>✅ Caption prefix removed. Files will be sent without a prefix.</b>")
    await update_user_info(me.id, m.from_user.id, {"caption_prefix": prefix})
    await m.reply(f"<b>✅ Caption prefix set to:</b> <code>{prefix}</code>\n\nAll files sent by your bot will now start with this name.")

@Client.on_message(filters.command('api') & filters.private)
async def shortener_api_handler(client, m: Message):
    me = client.me or await client.get_me()
    bot_owner = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_owner and bot_owner.get("is_deactivated", False):
        return await m.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    # Owner/Moderator/Admin check
    owner_id = int(bot_owner.get("user_id", 0)) if bot_owner else 0
    mods = bot_owner.get("moderators", []) if bot_owner else []
    if m.from_user.id != owner_id and m.from_user.id not in mods and m.from_user.id not in ADMINS:
        return await m.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")

    vplink_verified = bot_owner.get("vplink_verified", False) if bot_owner else False
    if not vplink_verified:
        from TechVJ.bot import StreamBot
        main_bot_username = (await StreamBot.get_me()).username
        return await m.reply(
            f"<b>⚠️ You need to register under our referral link first!</b>\n\n"
            f"1️⃣ Click this link to register: https://vplink.in/ref/Priyanshu7890\n"
            f"2️⃣ Create an account on VPLink.\n"
            f"3️⃣ Go to the Main Bot @{main_bot_username} and use Settings -> select this Bot to submit your verification request.\n\n"
            f"<i>Once verified by the admin, you will be able to set your shortener API key!</i>",
            disable_web_page_preview=True
        )

    cmd = m.command

    if len(cmd) == 1:
        current_api = bot_owner.get("shortener_api") or "Not set"
        s = f"<b><u>⚙️ Shortener Settings</u></b>\n\nDomain: <code>vplink.in</code>\nAPI Key: <code>{current_api}</code>\n\nTo set or update your API Key, use:\n<code>/api your_api_key</code>"
        return await m.reply(s)

    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await mongo_db.bots.update_one(
            {"bot_id": me.id},
            {"$set": {"shortener_site": "vplink.in", "shortener_api": api}}
        )
        await m.reply(f"<b>✅ Shortener API Key updated successfully!</b>")
    else:
        await m.reply("<b>❌ Invalid usage. Use: <code>/api your_api_key</code></b>")


# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    me = client.me or await client.get_me()
    bot_owner = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_owner and bot_owner.get("is_deactivated", False):
        return await m.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    # Owner/Moderator/Admin check
    owner_id = int(bot_owner.get("user_id", 0)) if bot_owner else 0
    mods = bot_owner.get("moderators", []) if bot_owner else []
    if m.from_user.id != owner_id and m.from_user.id not in mods and m.from_user.id not in ADMINS:
        return await m.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")

    vplink_verified = bot_owner.get("vplink_verified", False) if bot_owner else False
    if not vplink_verified:
        from TechVJ.bot import StreamBot
        main_bot_username = (await StreamBot.get_me()).username
        return await m.reply(
            f"<b>⚠️ You need to register under our referral link first!</b>\n\n"
            f"1️⃣ Click this link to register: https://vplink.in/ref/Priyanshu7890\n"
            f"2️⃣ Create an account on VPLink.\n"
            f"3️⃣ Go to the Main Bot @{main_bot_username} and use Settings -> select this Bot to submit your verification request.\n\n"
            f"<i>Once verified by the admin, you will be able to set your shortener base site!</i>",
            disable_web_page_preview=True
        )

    user_id = m.from_user.id
    user = await get_user(me.id, user_id)
    cmd = m.command
    text = f"/base_site (base_site)\n\nCurrent base site: None\n\n EX: /base_site shortnerdomain.com\n\nIf You Want To Remove Base Site Then Copy This And Send To Bot - `/base_site None`"
    
    if len(cmd) == 1:
        return await m.reply(text=text, disable_web_page_preview=True)
    elif len(cmd) == 2:
        base_site = cmd[1].strip()
        if not domain(base_site):
            return await m.reply(text=text, disable_web_page_preview=True)
        await update_user_info(me.id, user_id, {"base_site": base_site})
        await m.reply("Base Site updated successfully")
    else:
        await m.reply("You are not authorized to use this command.")

@Client.on_message(filters.command("stats") & filters.private & filters.incoming)
async def stats_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if not bot_doc: return
    
    # Owner/Moderator/Admin check
    owner_id = int(bot_doc.get("user_id", 0))
    mods = bot_doc.get("moderators", [])
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")

    m = await message.reply_text("<b>Calculating statistics...</b>")
    total_users = await clonedb.total_users_count(me.id)
    
    # Get additional info
    fsub_count = len(bot_doc.get("force_sub_channels", []))
    mode = bot_doc.get("bot_mode", "public").upper()
    nofwd = "Enabled ✅" if bot_doc.get("no_forward", False) else "Disabled ❌"
    token = "Enabled ✅" if bot_doc.get("token_verify", False) else "Disabled ❌"
    
    await m.edit_text(
        f"<b>📊 <u>{me.first_name} Statistics</u>\n\n"
        f"👤 Total Users: <code>{total_users}</code>\n"
        f"🔒 Force Sub: <code>{fsub_count} Channel(s)</code>\n"
        f"🌐 Bot Mode: <code>{mode}</code>\n"
        f"🚫 No Forward: <code>{nofwd}</code>\n"
        f"🔑 Access Token: <code>{token}</code></b>"
    )

@Client.on_message(filters.command("validity") & filters.private)
async def validity_command(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    # Owner/Moderator/Admin check
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can access this command.</b>")

    # Check if TMA ads are configured
    tma_mode = bot_doc.get("tma_mode", False) if bot_doc else False
    shortener_api = bot_doc.get("shortener_api") if bot_doc else None
    if not tma_mode or not shortener_api:
        return await message.reply_text("<b>❌ You didn't configure TMA ads first. Set them up first.</b>")

    from utils import TMA_VERIFIED, TMA_TIMEOUT
    import time
    
    text = "<b>📅 <u>Active Verifications</u></b>\n\n"
    
    # 1. TMA Verifications & Stats combined
    import pytz
    from datetime import datetime
    tz = pytz.timezone('Asia/Kolkata')
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    
    total_users_today = 0
    total_ads_today = 0
    user_records = {}
    
    # Query stats for today from database
    try:
        cursor = mongo_db.tma_stats.find({"bot_id": me.id, "date": today_str})
        async for doc in cursor:
            uid = int(doc.get("user_id"))
            ads_watched = doc.get("ads_watched", 0)
            total_ads_today += ads_watched
            user_records[uid] = {"ads": ads_watched, "links": 0}
    except Exception as e:
        logger.error(f"Error querying tma_stats for validity: {e}")
        
    # Merge active TMA verifications (remaining links)
    for key, val in list(TMA_VERIFIED.items()):
        key_str = str(key)
        if key_str.startswith(f"{me.id}_"):
            uid_str = key_str.split("_")[-1]
            try:
                uid = int(uid_str)
                if isinstance(val, dict):
                    # Ensure the verification session is from today
                    verified_at = val.get("verified_at", 0)
                    verified_date = datetime.fromtimestamp(verified_at, tz).strftime('%Y-%m-%d')
                    if verified_date != today_str:
                        TMA_VERIFIED.pop(key, None)
                        continue
                    links_left = int(val.get("links", 0))
                    if links_left <= 0:
                        TMA_VERIFIED.pop(key, None)
                        continue
                    if uid in user_records:
                        user_records[uid]["links"] = links_left
                    else:
                        user_records[uid] = {"ads": 0, "links": links_left}
                else:
                    TMA_VERIFIED.pop(key, None)
            except Exception as e:
                logger.error(f"Error parsing validity key {key}: {e}")
                TMA_VERIFIED.pop(key, None)

    # Sort records by ads watched descending, then by remaining links descending
    sorted_users = sorted(user_records.items(), key=lambda x: (x[1]["ads"], x[1]["links"]), reverse=True)
    total_users_today = len(sorted_users)
    
    detailed_stats_text = ""
    for uid, data in sorted_users:
        detailed_stats_text += f"• <code>{uid}</code> (Watched: {data['ads']} Ads today, Links Left: {data['links']})\n"
        
    if not detailed_stats_text:
        detailed_stats_text = "<i>No user activity today yet.</i>\n"
        
    text = (
        f"<b>📅 <u>Verification Stats (Today - {today_str})</u></b>\n"
        f"👥 <b>Total Users Today:</b> <code>{total_users_today}</code>\n"
        f"🎯 <b>Total Ads Watched Today:</b> <code>{total_ads_today}</code>\n\n"
        f"<b>📊 Today's User Activity & Validity:</b>\n"
        f"{detailed_stats_text}\n"
    )
    
    # 2. Standard Verifications (24 Hours / Custom Timeout)
    std_count = 0
    std_text = "\n<b>🔗 Standard Verifications:</b>\n"
    timeout = bot_doc.get("token_timeout", 86400) if bot_doc else 86400
    for key, verified_time in list(CLONE_VERIFIED.items()):
        if key.startswith(f"{me.id}_"):
            uid = key.split("_")[-1]
            elapsed = current_time - verified_time
            if elapsed < timeout:
                std_count += 1
                remaining = int(timeout - elapsed)
                hours = remaining // 3600
                mins = (remaining % 3600) // 60
                std_text += f"• <code>{uid}</code> (Remaining: {hours}h {mins}m)\n"
            else:
                CLONE_VERIFIED.pop(key, None)
        
    if std_count == 0:
        std_text += "<i>No active standard verifications.</i>\n"
        
    total_text = text + std_text
    await message.reply_text(total_text)

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

# ── Track Join Requests (Join Request Mode) ───────────────────
@Client.on_chat_join_request()
async def join_reqs_handler(client, join_request):
    """Record join requests without auto-approving them so owners can manually accept later."""
    try:
        me = client.me or await client.get_me()
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        if not bot_doc: return
        force_sub_mode = bot_doc.get('force_sub_mode', 'normal')
        if force_sub_mode == 'joinreq':
            await mongo_db.join_reqs.update_one(
                {"bot_id": me.id, "user_id": join_request.from_user.id, "channel_id": join_request.chat.id},
                {"$set": {"requested": True}},
                upsert=True
            )
    except: pass
# ──────────────────────────────────────────────────────────────────────

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    me = client.me or await client.get_me()
    
    if query.data.startswith("sub_pay_"):
        payload = query.data.split("sub_pay_", 1)[1]
        await mongo_db.user_states.update_one(
            {"bot_id": me.id, "user_id": query.from_user.id},
            {"$set": {"state": "waiting_paid_screenshot", "payload": payload}},
            upsert=True
        )
        await query.message.reply("<b>📤 Please send the payment screenshot photo now:</b>")
        await query.answer()
        return

    if query.data == "ref_campaign_menu":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        if query.from_user.id != owner_id:
            return await query.answer("❌ Only the bot owner can access referral campaign settings!", show_alert=True)
        
        from clone_plugins.db_referral import get_campaign
        camp = await get_campaign(me.id)
        enabled = camp.get("enabled", False) if camp else False
        duration = camp.get("duration_days", 7) if camp else 7
        channel = camp.get("channel", "Not set") if camp else "Not set"
        
        status_txt = "Active 🟢" if enabled else "Inactive 🔴"
        
        buttons = [
            [InlineKeyboardButton(f"Toggle Status: {'OFF 🔴' if enabled else 'ON 🟢'}", callback_data="toggle_ref_camp")],
            [InlineKeyboardButton("⏱ Set Duration", callback_data="set_ref_duration"), InlineKeyboardButton("📢 Set Channel", callback_data="set_ref_channel")],
            [InlineKeyboardButton("📊 Leaderboard", callback_data="ref_leaderboard"), InlineKeyboardButton("🔗 Join Link", callback_data="get_campaign_link")],
            [InlineKeyboardButton("🔙 Back", callback_data="settings")]
        ]
        
        await query.message.edit_text(
            text=(
                f"<b>📢 <u>Referral Campaign Manager</u></b>\n\n"
                f"• Status: <code>{status_txt}</code>\n"
                f"• Duration: <code>{duration} Days</code>\n"
                f"• Channel: <code>{channel}</code>\n\n"
                f"Configure your bot's referral program here. Users joining through the link will get their referral buttons in settings."
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        return
        
    elif query.data == "toggle_ref_camp":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        if query.from_user.id != owner_id:
            return await query.answer("❌ Unauthorized!", show_alert=True)
            
        from clone_plugins.db_referral import get_campaign, set_campaign
        camp = await get_campaign(me.id)
        current = camp.get("enabled", False) if camp else False
        await set_campaign(me.id, enabled=not current)
        await query.answer(f"Campaign {'enabled' if not current else 'disabled'} successfully!")
        query.data = "ref_campaign_menu"
        return await cb_handler(client, query)
        
    elif query.data == "set_ref_duration":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        if query.from_user.id != owner_id:
            return await query.answer("❌ Unauthorized!", show_alert=True)
            
        try:
            prompt = await _ask(client, query.message.chat.id, "<b>Please enter the campaign duration in days (e.g. 7 or 30):</b>")
            days = int(prompt.text.strip())
            from clone_plugins.db_referral import set_campaign
            await set_campaign(me.id, duration=days)
            await query.answer(f"✅ Campaign duration set to: {days} Days", show_alert=True)
            try:
                await client.delete_messages(query.message.chat.id, [prompt.prompt_message_id, prompt.id])
            except:
                pass
        except ValueError:
            await query.answer("❌ Invalid input. Please enter a number.", show_alert=True)
            try:
                await client.delete_messages(query.message.chat.id, [prompt.prompt_message_id, prompt.id])
            except:
                pass
        except Exception as e:
            logger.error(f"Error setting ref duration: {e}")
            
        query.data = "ref_campaign_menu"
        return await cb_handler(client, query)
        
    elif query.data == "set_ref_channel":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        if query.from_user.id != owner_id:
            return await query.answer("❌ Unauthorized!", show_alert=True)
            
        try:
            prompt = await _ask(client, query.message.chat.id, "<b>Please forward a message from the target channel, or send the channel ID (e.g. -100123456789):</b>")
            channel_id = None
            if prompt.forward_from_chat:
                channel_id = prompt.forward_from_chat.id
            else:
                channel_id = int(prompt.text.strip())
                
            try:
                chat = await client.get_chat(channel_id)
                from clone_plugins.db_referral import set_campaign
                await set_campaign(me.id, channel=channel_id)
                await query.answer(f"✅ Campaign channel set to: {chat.title} ({channel_id})", show_alert=True)
            except Exception as chat_err:
                await query.answer(f"❌ Error: Make sure the bot is admin in the target channel first!\n\nError: {chat_err}", show_alert=True)
                
            try:
                await client.delete_messages(query.message.chat.id, [prompt.prompt_message_id, prompt.id])
            except:
                pass
        except Exception as e:
            logger.error(f"Error setting ref channel: {e}")
            
        query.data = "ref_campaign_menu"
        return await cb_handler(client, query)
        
    elif query.data == "get_campaign_link":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        if query.from_user.id != owner_id:
            return await query.answer("❌ Unauthorized!", show_alert=True)
            
        link = f"https://t.me/{me.username}?start=joinref"
        await query.message.reply_text(
            text=f"<b>🔗 <u>Campaign Invite Link</u></b>\n\nShare this link to invite users to participate in the referral program:\n<code>{link}</code>",
            disable_web_page_preview=True
        )
        await query.answer()
        return
        
    elif query.data == "get_user_ref_link":
        from clone_plugins.db_referral import is_participant
        if not await is_participant(me.id, query.from_user.id):
            return await query.answer("❌ You are not registered in the Referral Program!", show_alert=True)
            
        link = f"https://t.me/{me.username}?start=ref_{query.from_user.id}"
        await query.message.reply_text(
            text=f"<b>🔗 <u>Your Personal Referral Link</u></b>\n\nShare this link. When new users join, you will earn points:\n<code>{link}</code>",
            disable_web_page_preview=True
        )
        await query.answer()
        return
        
    elif query.data == "ref_leaderboard":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        if query.from_user.id != owner_id:
            return await query.answer("❌ Unauthorized!", show_alert=True)
            
        from clone_plugins.db_referral import get_leaderboard
        board = await get_leaderboard(me.id)
        
        text = "<b>🏆 <u>Referral Campaign Leaderboard</u></b>\n\n"
        if not board:
            text += "<i>No stats available yet. Share the campaign link!</i>"
        else:
            for idx, user in enumerate(board[:15], 1):
                text += f"{idx}. User ID: <code>{user['user_id']}</code>\n   ➔ Referrals: <code>{user['referral_count']}</code> | Unique Link Clicks: <code>{user['clicks_count']}</code>\n\n"
                
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="ref_campaign_menu")]]
        await query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        return
        
    elif query.data == "confirm_join_ref":
        from clone_plugins.db_referral import add_participant
        await add_participant(me.id, query.from_user.id)
        await query.message.edit_text(
            text="<b>🎉 Congratulations! You have successfully joined the Referral Program.</b>\n\nGo to settings to get your personal referral link!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Open Settings", callback_data="settings")]])
        )
        return

    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "toggle_tma":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure TMA settings!", show_alert=True)
        
        vplink_verified = bot_doc.get("vplink_verified", False) if bot_doc else False
        if not vplink_verified:
            from TechVJ.bot import StreamBot
            main_bot_username = (await StreamBot.get_me()).username
            caption = (
                "<b>⚠️ You need to register under our referral link first!</b>\n\n"
                "1️⃣ Click this link to register: https://vplink.in/ref/Priyanshu7890\n"
                "2️⃣ Create an account on VPLink.\n"
                "3️⃣ Go to the Main Bot @{main_bot_username} and use Settings -> select this Bot to submit your verification request.\n\n"
                "<i>Once approved by the admin, you will be able to enable TMA Ads and configure your shortener settings!</i>"
            ).format(main_bot_username=main_bot_username)
            buttons = [
                [InlineKeyboardButton("🔗 Register on VPLink", url="https://vplink.in/ref/Priyanshu7890")],
                [InlineKeyboardButton("🤖 Go to Main Bot to Verify", url=f"https://t.me/{main_bot_username}?start=verifyclone_{me.id}")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ]
            try:
                await query.message.delete()
            except:
                pass
            try:
                await client.send_photo(
                    chat_id=query.message.chat.id,
                    photo="vplink_tutorial.png",
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except:
                await client.send_message(
                    chat_id=query.message.chat.id,
                    text=caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    disable_web_page_preview=True
                )

        tma_mode = bot_doc.get("tma_mode", False) if bot_doc else False
        new_mode = not tma_mode
        await mongo_db.bots.update_one({"bot_id": me.id}, {"$set": {"tma_mode": new_mode}})
        await query.answer(f"TMA Ads {'Enabled 🟢' if new_mode else 'Disabled 🔴'}", show_alert=True)
        query.data = "settings"
        return await cb_handler(client, query)
    elif query.data == "toggle_plan":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure Plan settings!", show_alert=True)
        
        plan_enabled = bot_doc.get("plan_enabled", True) if bot_doc else True
        new_mode = not plan_enabled
        await mongo_db.bots.update_one({"bot_id": me.id}, {"$set": {"plan_enabled": new_mode}})
        await query.answer(f"VIP Plan {'Enabled 🟢' if new_mode else 'Disabled 🔴'}", show_alert=True)
        query.data = "settings"
        return await cb_handler(client, query)
    elif query.data == "toggle_stream":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure Stream settings!", show_alert=True)
        
        stream_mode = bot_doc.get("stream_mode", False) if bot_doc else False
        new_mode = not stream_mode
        await mongo_db.bots.update_one({"bot_id": me.id}, {"$set": {"stream_mode": new_mode}})
        await query.answer(f"Stream Mode {'Enabled 🟢' if new_mode else 'Disabled 🔴'}", show_alert=True)
        query.data = "settings"
        return await cb_handler(client, query)
    elif query.data == "toggle_paid":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure Paid Links settings!", show_alert=True)
        
        paid_links = bot_doc.get("paid_links", False) if bot_doc else False
        new_mode = not paid_links
        await mongo_db.bots.update_one({"bot_id": me.id}, {"$set": {"paid_links": new_mode}})
        await query.answer(f"Paid Links {'Enabled 🟢' if new_mode else 'Disabled 🔴'}", show_alert=True)
        query.data = "settings"
        return await cb_handler(client, query)
    elif query.data == "toggle_tma_type":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure TMA Type!", show_alert=True)
        
        tma_type = bot_doc.get("tma_type", "links") if bot_doc else "links"
        new_type = "time" if tma_type == "links" else "links"
        await mongo_db.bots.update_one({"bot_id": me.id}, {"$set": {"tma_type": new_type}})
        await query.answer(f"TMA Type switched to {new_type.upper()}", show_alert=True)
        query.data = "settings"
        return await cb_handler(client, query)
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('⚙️ sᴇᴛᴛɪɴɢs', callback_data='settings'),
            InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ᴄʟᴏɴᴇ', url=f'https://t.me/{BOT_USERNAME}?start=clone')
        ],[
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        photo = bot_doc.get("start_photo") if bot_doc else None
        if photo and not photo.startswith("http"): photo = None
        if not photo: photo = random.choice(PICS)

        try:
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(photo)
            )
        except Exception:
            pass
        await query.message.edit_text(
            text=script.CLONE_START_TXT.format(query.from_user.mention, me.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        photo = bot_doc.get("start_photo") if bot_doc else None
        if photo and not photo.startswith("http"): photo = None
        if not photo: photo = random.choice(PICS)

        try:
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(photo)
            )
        except Exception:
            pass
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CHELP_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  

    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        photo = bot_doc.get("start_photo") if bot_doc else None
        if photo and not photo.startswith("http"): photo = None
        if not photo: photo = random.choice(PICS)

        try:
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(photo)
            )
        except Exception:
            pass
        owner_id_about = int(bot_doc['user_id']) if bot_doc else 0
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CABOUT_TXT.format(me.mention, owner_id_about),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

    elif query.data == "settings":
        user_id = query.from_user.id
        user = await get_user(me.id, user_id)
        prefix = user.get("caption_prefix", "") or "<i>Not set</i>"
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        tma_mode = bot_doc.get("tma_mode", False) if bot_doc else False
        tma_status = "Enabled 🟢" if tma_mode else "Disabled 🔴"
        plan_enabled = bot_doc.get("plan_enabled", True) if bot_doc else True
        plan_status = "Enabled 🟢" if plan_enabled else "Disabled 🔴"
        stream_mode = bot_doc.get("stream_mode", False) if bot_doc else False
        stream_status = "Enabled 🟢" if stream_mode else "Disabled 🔴"
        paid_links = bot_doc.get("paid_links", False) if bot_doc else False
        paid_status = "Enabled 🟢" if paid_links else "Disabled 🔴"
        tma_type = bot_doc.get("tma_type", "links") if bot_doc else "links"
        tma_type_status = "Links 🔗" if tma_type == "links" else "Time 🕒"
        
        buttons = [[
            InlineKeyboardButton('📝 sᴇᴛ ᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx', callback_data='set_caption'),
            InlineKeyboardButton(f"TMA Ads: {'ON 🟢' if tma_mode else 'OFF 🔴'}", callback_data="toggle_tma")
        ],[
            InlineKeyboardButton('💳 Configure Plan', callback_data='setplan'),
            InlineKeyboardButton(f"VIP Plan: {'ON 🟢' if plan_enabled else 'OFF 🔴'}", callback_data="toggle_plan")
        ],[
            InlineKeyboardButton(f"Stream: {'ON 🟢' if stream_mode else 'OFF 🔴'}", callback_data="toggle_stream"),
            InlineKeyboardButton(f"Paid Links: {'ON 🟢' if paid_links else 'OFF 🔴'}", callback_data="toggle_paid")
        ],[
            InlineKeyboardButton(f"TMA Type: {tma_type_status}", callback_data="toggle_tma_type")
        ],[
            InlineKeyboardButton('💬 ᴄʜᴀᴛʙox', url='https://t.me/+cFO-dJGWlCMzNGRl'),
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
        ],[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
        ]]
        
        photo = bot_doc.get("start_photo") if bot_doc else None
        if photo and not photo.startswith("http"): photo = None
        if not photo: photo = random.choice(PICS)

        try:
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(photo)
            )
        except Exception:
            pass
        from TechVJ.bot import StreamBot
        from clone_plugins.db_referral import is_participant
        main_bot_username = (await StreamBot.get_me()).username
        is_owner = bot_doc and (int(bot_doc.get('user_id', 0)) == query.from_user.id or query.from_user.id in ADMINS)
        
        if is_owner:
            buttons.insert(0, [InlineKeyboardButton('⚙️ Bot Settings', url=f"https://t.me/{main_bot_username}?start=manageclone_{me.id}")])
            buttons.insert(3, [InlineKeyboardButton('📢 Referral Campaign', callback_data='ref_campaign_menu')])
        elif await is_participant(me.id, query.from_user.id):
            buttons.insert(3, [InlineKeyboardButton('🔗 My Referral Link', callback_data='get_user_ref_link')])
            
        buttons.insert(0, [InlineKeyboardButton('⚙️ TMA Ads Setting', url=f"https://t.me/{main_bot_username}?start=verifyclone_{me.id}")])

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴛᴍᴀ ᴀᴅs: <code>{tma_status}</code>\nᴛᴍᴀ ᴛʏᴘᴇ: <code>{tma_type_status}</code>\nᴠɪᴘ ᴘʟᴀɴ: <code>{plan_status}</code>\nsᴛʀᴇᴀᴍ ᴍᴏᴅᴇ: <code>{stream_status}</code>\nᴘᴀɪᴅ ʟɪɴᴋs: <code>{paid_status}</code>\nᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx: {prefix}</b>",
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "set_api":
        await query.message.edit_text(
            text="<b>ᴛᴏ sᴇᴛ ʏᴏᴜʀ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ, ᴜsᴇ ᴛʜᴇ /api ᴄᴏᴍᴍᴀɴᴅ.\n\nᴇx: <code>/api your_api_key</code></b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='settings')]])
        )

    elif query.data == "set_site":
        await query.message.edit_text(
            text="<b>ᴛᴏ sᴇᴛ ʏᴏᴜʀ ʙᴀsᴇ sɪᴛᴇ, ᴜsᴇ ᴛʜᴇ /base_site ᴄᴏᴍᴍᴀɴᴅ.\n\nᴇx: <code>/base_site domain.com</code></b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='settings')]])
        )

    elif query.data == "set_caption":
        await query.message.edit_text(
            text="<b>📝 ᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx\n\nᴜsᴇ ᴛʜᴇ /setcaption ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ sᴇᴛ ʏᴏᴜʀ ᴄᴜsᴛᴏᴍ ɴᴀᴍᴇ ᴘʀᴇꜰɪx.\n\nᴇx: <code>/setcaption @YourChannel</code>\n\nᴛᴏ ʀᴇᴍᴏᴠᴇ: <code>/setcaption off</code></b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='settings')]])
        )

    elif query.data == "setplan":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure plans!", show_alert=True)
            
        plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id}) or {}
        upi_enabled = plan_cfg.get("upi_enabled", True)
        stars_enabled = plan_cfg.get("stars_enabled", True)
        paypal_enabled = plan_cfg.get("paypal_enabled", True)
            
        buttons = [
            [
                InlineKeyboardButton("💳 Set UPI", callback_data="setplan_upi"),
                InlineKeyboardButton(f"{'✅ Enabled' if upi_enabled else '❌ Disabled'}", callback_data="toggle_upi")
            ],
            [
                InlineKeyboardButton("⭐ Set Stars", callback_data="setplan_stars"),
                InlineKeyboardButton(f"{'✅ Enabled' if stars_enabled else '❌ Disabled'}", callback_data="toggle_stars")
            ],
            [
                InlineKeyboardButton("🅿️ Set PayPal", callback_data="setplan_paypal"),
                InlineKeyboardButton(f"{'✅ Enabled' if paypal_enabled else '❌ Disabled'}", callback_data="toggle_paypal")
            ],
            [InlineKeyboardButton("📸 Set Alt Server QR", callback_data="setplan_altqr")],
            [InlineKeyboardButton("« Back to Settings", callback_data="settings")]
        ]
        
        await query.message.edit_text(
            text="<b>⚙️ <u>Payment Plan Configuration</u>\n\nSelect the payment method you want to configure or toggle to disable/enable it:</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return await query.answer()

    elif query.data.startswith("toggle_"):
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure plans!", show_alert=True)
            
        method = query.data.split("_")[1]
        plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id}) or {}
        
        key = f"{method}_enabled"
        current_val = plan_cfg.get(key, True)
        
        await mongo_db.plans_config.update_one(
            {"_id": me.id},
            {"$set": {key: not current_val}},
            upsert=True
        )
        
        query.data = "setplan"
        return await cb_handler(client, query)

    elif query.data == "setplan_upi":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure plans!", show_alert=True)
            
        msg = await client.ask(
            chat_id=query.message.chat.id,
            text="<b>📸 Please send/upload your UPI QR code photo (or send /cancel to exit).</b>"
        )
        if msg.text and msg.text.strip() == "/cancel":
            return await msg.reply("<b>Cancelled UPI configuration.</b>")
            
        if not msg.photo:
            return await msg.reply("<b>❌ Please send a photo of the QR code. Try again from Settings.</b>")
            
        qr_file_id = msg.photo.file_id
        
        msg_text = await client.ask(
            chat_id=query.message.chat.id,
            text="<b>✍️ Now please send the UPI plans text with prices (or send /cancel to skip).\n\nExample:\n<code>1 Month - 199\n3 Months - 399\nLifetime - 799</code></b>"
        )
        if msg_text.text and msg_text.text.strip() == "/cancel":
            return await msg_text.reply("<b>Cancelled UPI configuration.</b>")
            
        plans_text = msg_text.text.html if msg_text.text else "Plans not configured"
        
        await mongo_db.plans_config.update_one(
            {"_id": me.id},
            {"$set": {
                "payment_qr": qr_file_id,
                "plans_text": plans_text
            }},
            upsert=True
        )
        await msg_text.reply("<b>✅ UPI Payment configured successfully!</b>")
        
    elif query.data == "setplan_stars":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure plans!", show_alert=True)
            
        msg_stars = await client.ask(
            chat_id=query.message.chat.id,
            text="<b>⭐ Please send the Telegram Stars plans text with prices (or send /cancel to exit).\n\nExample:\n<code>1 Month - 50 Stars\n3 Months - 120 Stars\nLifetime - 300 Stars</code></b>"
        )
        if msg_stars.text and msg_stars.text.strip() == "/cancel":
            return await msg_stars.reply("<b>Cancelled Stars configuration.</b>")
            
        stars_plans_text = msg_stars.text.html if msg_stars.text else "Stars Plans not configured"
        
        await mongo_db.plans_config.update_one(
            {"_id": me.id},
            {"$set": {
                "stars_plans_text": stars_plans_text
            }},
            upsert=True
        )
        await msg_stars.reply("<b>✅ Telegram Stars Payment configured successfully!</b>")
        
    elif query.data == "setplan_paypal":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure plans!", show_alert=True)
            
        msg_paypal_qr = await client.ask(
            chat_id=query.message.chat.id,
            text="<b>📸 Please send/upload your PayPal QR code photo (or send /cancel to exit).</b>"
        )
        if msg_paypal_qr.text and msg_paypal_qr.text.strip() == "/cancel":
            return await msg_paypal_qr.reply("<b>Cancelled PayPal configuration.</b>")
        
        if not msg_paypal_qr.photo:
            return await msg_paypal_qr.reply("<b>❌ Please send a photo of the QR code. Try again from Settings.</b>")
            
        paypal_qr_file_id = msg_paypal_qr.photo.file_id
        
        msg_paypal_text = await client.ask(
            chat_id=query.message.chat.id,
            text="<b>✍️ Now please send the PayPal plans text with prices (or send /cancel to skip).\n\nExample:\n<code>1 Month - 2$\n3 Months - 5$\nLifetime - 10$</code></b>"
        )
        if msg_paypal_text.text and msg_paypal_text.text.strip() == "/cancel":
            return await msg_paypal_text.reply("<b>Cancelled PayPal configuration.</b>")
            
        paypal_plans_text = msg_paypal_text.text.html if msg_paypal_text.text else "PayPal Plans not configured"
        
        await mongo_db.plans_config.update_one(
            {"_id": me.id},
            {"$set": {
                "paypal_qr": paypal_qr_file_id,
                "paypal_plans_text": paypal_plans_text
            }},
            upsert=True
        )
        await msg_paypal_text.reply("<b>✅ PayPal Payment configured successfully!</b>")
        
    elif query.data == "setplan_altqr":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure plans!", show_alert=True)
            
        msg_alt = await client.ask(
            chat_id=query.message.chat.id,
            text="<b>📸 Please send an alternative QR code photo for 'Server Down' (or send /cancel to exit).</b>"
        )
        if msg_alt.text and msg_alt.text.strip() == "/cancel":
            return await msg_alt.reply("<b>Cancelled Alt QR configuration.</b>")
            
        if not msg_alt.photo:
            return await msg_alt.reply("<b>❌ Please send a photo of the QR code. Try again from Settings.</b>")
            
        alt_qr_file_id = msg_alt.photo.file_id
        
        await mongo_db.plans_config.update_one(
            {"_id": me.id},
            {"$set": {
                "alt_payment_qr": alt_qr_file_id
            }},
            upsert=True
        )
        await msg_alt.reply("<b>✅ Alternative QR configured successfully!</b>")

    elif query.data == "buy_plan":
        plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
        if not plan_cfg:
            return await query.answer("Plans not configured!", show_alert=True)
            
        await mongo_db.user_states.delete_one({"bot_id": me.id, "user_id": query.from_user.id})
        
        btn = []
        if plan_cfg.get("upi_enabled", True):
            btn.append([InlineKeyboardButton("💳 UPI Payment", callback_data="buy_upi")])
        if plan_cfg.get("stars_enabled", True):
            btn.append([InlineKeyboardButton("⭐ Telegram Stars", callback_data="buy_stars")])
        if plan_cfg.get("paypal_enabled", True):
            btn.append([InlineKeyboardButton("🅿️ PayPal Payment", callback_data="buy_paypal")])
            
        btn.append([InlineKeyboardButton("« Back", callback_data="plan_status_back")])
        
        try:
            await query.message.delete()
        except Exception:
            pass
            
        await client.send_message(
            chat_id=query.message.chat.id,
            text="<b>🌟 <u>Choose Payment Method</u>\n\nSelect How You Would Like To Pay For Premium Access</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await query.answer()

    elif query.data == "buy_upi":
        plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
        if not plan_cfg:
            return await query.answer("Plans not configured!", show_alert=True)
            
        qr_file_id = plan_cfg["payment_qr"]
        plans_text = plan_cfg["plans_text"]
        
        caption = (
            f"<b>🛒 <u>VIP Plans & Pricing</u></b>\n\n"
            f"{plans_text}\n\n"
            f"<b><u>How to buy:</u></b>\n"
            f"1️⃣ Scan the QR code below to make payment.\n"
            f"2️⃣ Send the screenshot of the payment receipt here in the chat.\n\n"
            f"<i>Our admin will review and verify your screenshot to activate VIP access.</i>"
        )
        
        await mongo_db.user_states.update_one(
            {"bot_id": me.id, "user_id": query.from_user.id},
            {"$set": {"state": "waiting_screenshot"}},
            upsert=True
        )
        
        buttons = []
        if plan_cfg.get("alt_payment_qr"):
            buttons.append([InlineKeyboardButton("⚠️ Receiver bank not working?", callback_data="alt_buy_upi")])
        buttons.append([InlineKeyboardButton("« Back", callback_data="buy_plan")])
        
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=qr_file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await query.message.delete()
        await query.answer()

    elif query.data == "alt_buy_upi":
        plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
        if not plan_cfg or not plan_cfg.get("alt_payment_qr"):
            return await query.answer("Alternate QR not configured!", show_alert=True)
            
        alt_qr_file_id = plan_cfg["alt_payment_qr"]
        plans_text = plan_cfg["plans_text"]
        
        caption = (
            f"<b>🛒 <u>VIP Plans & Pricing</u></b>\n\n"
            f"{plans_text}\n\n"
            f"<b><u>How to buy:</u></b>\n"
            f"1️⃣ Scan the QR code below to make payment.\n"
            f"2️⃣ Send the screenshot of the payment receipt here in the chat.\n\n"
            f"<i>Our admin will review and verify your screenshot to activate VIP access.</i>"
        )
        
        buttons = [
            [InlineKeyboardButton("🔄 Show Primary QR", callback_data="buy_upi")],
            [InlineKeyboardButton("« Back", callback_data="buy_plan")]
        ]
        
        try:
            await query.edit_message_media(
                media=InputMediaPhoto(media=alt_qr_file_id, caption=caption),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await query.answer()
        except Exception as e:
            logging.error(f"Error editing QR media: {e}")
            await query.answer("Could not change QR image.", show_alert=True)

    elif query.data == "buy_paypal":
        plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
        if not plan_cfg or not plan_cfg.get("paypal_qr"):
            return await query.answer("PayPal is not configured by the admin!", show_alert=True)
            
        qr_file_id = plan_cfg["paypal_qr"]
        plans_text = plan_cfg.get("paypal_plans_text", "Plans not configured")
        
        caption = (
            f"<b>🛒 <u>VIP Plans & Pricing (PayPal)</u></b>\n\n"
            f"{plans_text}\n\n"
            f"<b><u>How to buy:</u></b>\n"
            f"1️⃣ Scan the QR code below to make payment.\n"
            f"2️⃣ Send the screenshot of the payment receipt here in the chat.\n\n"
            f"<i>Our admin will review and verify your screenshot to activate VIP access.</i>"
        )
        
        await mongo_db.user_states.update_one(
            {"bot_id": me.id, "user_id": query.from_user.id},
            {"$set": {"state": "waiting_screenshot"}},
            upsert=True
        )
        
        buttons = []
        buttons.append([InlineKeyboardButton("« Back", callback_data="buy_plan")])
        
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=qr_file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await query.message.delete()
        await query.answer()

    elif query.data == "buy_stars":
        await mongo_db.user_states.delete_one({"bot_id": me.id, "user_id": query.from_user.id})
        
        plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
        stars_plans_text = plan_cfg.get("stars_plans_text", "Plans not configured") if plan_cfg else "Plans not configured"
        prices = parse_stars_prices(stars_plans_text)
        
        text = (
            "<b>⭐ <u>Telegram Stars Payment</u>\n\n"
            "Select the VIP plan you want to purchase using Telegram Stars:</b>\n\n"
            f"{stars_plans_text}"
        )
        
        btn = []
        if prices.get("1d"):
            btn.append([InlineKeyboardButton(f"⭐ 1 Day ({prices['1d']} Stars)", callback_data="pay_stars_1")])
        if prices.get("1w"):
            btn.append([InlineKeyboardButton(f"⭐ 1 Week ({prices['1w']} Stars)", callback_data="pay_stars_7")])
        if prices.get("1m"):
            btn.append([InlineKeyboardButton(f"⭐ 1 Month ({prices['1m']} Stars)", callback_data="pay_stars_30")])
        if prices.get("3m"):
            btn.append([InlineKeyboardButton(f"⭐ 3 Months ({prices['3m']} Stars)", callback_data="pay_stars_90")])
        if prices.get("6m"):
            btn.append([InlineKeyboardButton(f"⭐ 6 Months ({prices['6m']} Stars)", callback_data="pay_stars_180")])
        if prices.get("lifetime"):
            btn.append([InlineKeyboardButton(f"⭐ Lifetime ({prices['lifetime']} Stars)", callback_data="pay_stars_0")])
            
        btn.append([InlineKeyboardButton("« Back", callback_data="buy_plan")])
        
        try:
            await query.message.delete()
        except Exception:
            pass
            
        await client.send_message(
            chat_id=query.message.chat.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        await query.answer()

    elif query.data.startswith("pay_stars_"):
        days = int(query.data.split("_")[-1])
        plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
        stars_plans_text = plan_cfg.get("stars_plans_text", "Plans not configured") if plan_cfg else "Plans not configured"
        prices = parse_stars_prices(stars_plans_text)
        
        if days == 1:
            title = "1 Day VIP Access"
            amount = prices.get("1d")
        elif days == 7:
            title = "1 Week VIP Access"
            amount = prices.get("1w")
        elif days == 30:
            title = "1 Month VIP Access"
            amount = prices.get("1m")
        elif days == 90:
            title = "3 Months VIP Access"
            amount = prices.get("3m")
        elif days == 180:
            title = "6 Months VIP Access"
            amount = prices.get("6m")
        else:
            title = "Lifetime VIP Access"
            amount = prices.get("lifetime")
            
        if not amount:
            return await query.answer("Price not configured for this plan!", show_alert=True)
            
        from pyrogram.types import LabeledPrice
        try:
            await query.message.delete()
        except Exception:
            pass
            
        try:
            await client.send_invoice(
                chat_id=query.message.chat.id,
                title=title,
                description=f"Get VIP access for {'Lifetime' if days == 0 else f'{days} days'} on this bot. Enjoy ad-free and instant file downloads!",
                payload=f"vip_stars_{days}",
                currency="XTR",
                prices=[LabeledPrice(label=title, amount=amount)],
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Plans", callback_data="buy_plan")]])
            )
        except Exception as e:
            logger.error(f"Error sending invoice: {e}")
            await client.send_message(
                chat_id=query.message.chat.id,
                text=f"<b>❌ Error sending invoice: {e}</b>\n\nPlease try again later or use UPI payment.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back to Plans", callback_data="buy_plan")]])
            )
        await query.answer()


    elif query.data == "plan_status_back":
        try:
            await query.message.delete()
        except:
            pass
            
        user_vip = await is_vip(me.id, query.from_user.id)
        if user_vip:
            from datetime import datetime
            vip_user = await mongo_db.vip_users.find_one({"bot_id": me.id, "user_id": query.from_user.id})
            expiry = vip_user.get("expiry")
            expiry_str = datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S') if expiry else "Lifetime"
            
            await client.send_message(
                chat_id=query.message.chat.id,
                text=f"<b>✨ <u>VIP Plan Status</u>\n\n"
                     f"➜ Status: Active VIP Member ✅\n"
                     f"➜ Expiry: <code>{expiry_str}</code>\n\n"
                     f"Thank you for supporting us! You bypass all shortlink/TMA verifications.</b>"
            )
        else:
            btn = [[InlineKeyboardButton("🛒 Buy Plan", callback_data="buy_plan")]]
            await client.send_message(
                chat_id=query.message.chat.id,
                text=f"<b>❌ <u>VIP Plan Status</u>\n\n"
                     f"➜ Status: No Active Plan ❌\n\n"
                     f"You will need to bypass verifications to download files. Get a VIP plan to unlock instant downloads!</b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
        await query.answer()

@Client.on_message(filters.command("plan") & filters.private)
async def plan_command_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    plan_enabled = bot_doc.get("plan_enabled", True) if bot_doc else True
    plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
    if not plan_cfg or not plan_enabled:
        return await message.reply_text("<b>⚠️ This bot does not have a plan configured yet. Please check back later!</b>")
        
    user_vip = await is_vip(me.id, message.from_user.id)
    if user_vip:
        from datetime import datetime
        vip_user = await mongo_db.vip_users.find_one({"bot_id": me.id, "user_id": message.from_user.id})
        expiry = vip_user.get("expiry")
        if expiry:
            expiry_str = datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
        else:
            expiry_str = "Lifetime"
            
        return await message.reply_text(
            f"<b>✨ <u>VIP Plan Status</u>\n\n"
            f"➜ Status: Active VIP Member ✅\n"
            f"➜ Expiry: <code>{expiry_str}</code>\n\n"
            f"Thank you for supporting us! You bypass all shortlink/TMA verifications.</b>"
        )
    else:
        btn = [[InlineKeyboardButton("🛒 Buy Plan", callback_data="buy_plan")]]
        return await message.reply_text(
            f"<b>❌ <u>VIP Plan Status</u>\n\n"
            f"➜ Status: No Active Plan ❌\n\n"
            f"You will need to bypass verifications to download files. Get a VIP plan to unlock instant downloads!</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )

import pyrogram

@Client.on_raw_update(group=1)
async def pre_checkout_handler(client, update, users, chats):
    if type(update).__name__ == "UpdateBotPrecheckoutQuery":
        await client.invoke(
            pyrogram.raw.functions.messages.SetBotPrecheckoutResults(
                query_id=update.query_id,
                success=True
            )
        )

@Client.on_message(filters.successful_payment)
async def successful_payment_handler(client, message):
    me = client.me or await client.get_me()
    payment = message.successful_payment
    payload = payment.invoice_payload
    
    if payload.startswith("vip_stars_"):
        try:
            days = int(payload.split("_")[-1])
        except ValueError:
            days = 30
            
        import time
        from datetime import datetime
        if days == 0:
            expiry = None
            days_label = "Lifetime"
            expiry_str = "Lifetime"
        else:
            expiry = time.time() + days * 86400
            days_label = f"{days} Days"
            expiry_str = datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
            
        user_id = message.from_user.id
        
        await message.reply_text(
            f"<b>✅ Payment Successful!</b>\n\n"
            f"Thank you for your payment of <b>{payment.total_amount} Telegram Stars</b>.\n\n"
            f"⏳ <b>Please wait, an admin is verifying your payment. Your VIP access will be activated shortly.</b>"
        )
        
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        
        recipients = [owner_id] + list(mods)
        for rcpt in recipients:
            if rcpt:
                try:
                    await client.send_message(
                        chat_id=rcpt,
                        text=f"<b>⭐ New VIP Purchase via Telegram Stars!</b>\n\n"
                             f"👤 <b>User:</b> {message.from_user.mention} (ID: <code>{user_id}</code>)\n"
                             f"💵 <b>Amount:</b> <code>{payment.total_amount} Stars</code>\n"
                             f"📅 <b>Plan:</b> {days_label}\n\n"
                             f"<b>To activate, click and send this command:</b>\n"
                             f"<code>/addvip {user_id} {days}</code>"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify recipient {rcpt} of successful payment: {e}")

@Client.on_message((filters.photo | filters.document) & filters.private & filters.incoming)
async def photo_message_handler(client, message):
    me = client.me or await client.get_me()
    state_doc = await mongo_db.user_states.find_one({"bot_id": me.id, "user_id": message.from_user.id})
    if state_doc and state_doc.get("state") == "waiting_screenshot":
        await mongo_db.user_states.delete_one({"bot_id": me.id, "user_id": message.from_user.id})
        
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        
        recipients = [owner_id] + list(mods)
        for rcpt in recipients:
            if rcpt:
                try:
                    await message.forward(rcpt)
                    await client.send_message(
                        chat_id=rcpt,
                        text=f"<b>📩 New VIP Payment Receipt Screenshot!</b>\n\n"
                             f"👤 <b>From User:</b> {message.from_user.mention} (ID: <code>{message.from_user.id}</code>)\n\n"
                             f"➜ To activate: `/addvip {message.from_user.id} [days]`\n"
                             f"➜ To decline: `/declinevip {message.from_user.id} [reason]`\n"
                             f"➜ To message: `/msg {message.from_user.id} [text]`"
                    )
                except Exception as e:
                    logger.error(f"Failed to forward screenshot to {rcpt}: {e}")
                
        await message.reply_text(
            "<b>Receipt sent successfully! Please wait for confirmation.</b>"
        )
    elif state_doc and state_doc.get("state") == "waiting_paid_screenshot":
        payload = state_doc.get("payload")
        await mongo_db.user_states.delete_one({"bot_id": me.id, "user_id": message.from_user.id})
        
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        
        paid_doc = await mongo_db.paid_links.find_one({"bot_id": me.id, "payload": payload})
        title = paid_doc.get("title", "Paid File") if paid_doc else "Paid File"
        
        recipients = [owner_id] + list(mods)
        for rcpt in recipients:
            if rcpt:
                try:
                    await message.forward(rcpt)
                    await client.send_message(
                        chat_id=rcpt,
                        text=f"<b>📩 New Paid Link Payment Screenshot!</b>\n\n"
                             f"👤 <b>From User:</b> {message.from_user.mention} (ID: <code>{message.from_user.id}</code>)\n"
                             f"💰 <b>File/Link Title:</b> {title}\n"
                             f"🔗 <b>Payload:</b> <code>{payload}</code>\n\n"
                             f"<b>To approve, click and send this command:</b>\n"
                             f"<code>/approvepaid {message.from_user.id} {payload}</code>"
                    )
                except Exception as e:
                    logger.error(f"Failed to forward paid link screenshot to {rcpt}: {e}")
                
        await message.reply_text(
            "<b>Payment screenshot sent successfully! Please wait for the admin to verify and approve.</b>"
        )

@Client.on_message(filters.command("addvip") & filters.private)
async def add_vip_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")
        
    if len(message.command) < 3:
        return await message.reply_text("<b>Usage:</b> `/addvip [user_id] [days]` (use 0 or 'lifetime' for permanent access)")
        
    try:
        user_id = int(message.command[1])
        days_str = message.command[2].lower()
        import time
        from datetime import datetime
        
        if days_str in ["0", "lifetime", "permanent"]:
            expiry = None
            days_label = "Lifetime"
        else:
            days = int(days_str)
            expiry = time.time() + days * 86400
            days_label = f"{days} Days"
            
        await mongo_db.vip_users.update_one(
            {"bot_id": me.id, "user_id": user_id},
            {"$set": {"expiry": expiry}},
            upsert=True
        )
        
        await message.reply_text(f"<b>✅ User <code>{user_id}</code> is now a VIP member ({days_label})!</b>")
        
        try:
            import pytz
            tz = pytz.timezone('Asia/Kolkata')
            expiry_str = datetime.fromtimestamp(expiry, tz).strftime('%Y-%m-%d %H:%M:%S') if expiry else "Lifetime"
            await client.send_message(
                chat_id=user_id,
                text=f"🎉 <b>Congratulations! You have been granted VIP access for {days_label}.</b>\n\n"
                     f"➜ Expires on: <code>{expiry_str}</code> (IST)\n"
                     f"You now bypass all shortlink/TMA verifications on this bot! Enjoy instant downloads."
            )
        except Exception as e:
            logger.error(f"Could not notify VIP user {user_id}: {e}")
            
    except ValueError:
        await message.reply_text("<b>❌ Invalid User ID or Days. Must be integers.</b>")
    except Exception as e:
        await message.reply_text(f"<b>❌ Error: {e}</b>")

@Client.on_message(filters.command("delvip") & filters.private)
async def del_vip_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")
        
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> `/delvip [user_id]`")
        
    try:
        user_id = int(message.command[1])
        res = await mongo_db.vip_users.delete_one({"bot_id": me.id, "user_id": user_id})
        if res.deleted_count > 0:
            await message.reply_text(f"<b>✅ VIP access removed for User <code>{user_id}</code>.</b>")
            try:
                await client.send_message(
                    chat_id=user_id,
                    text="<b>❌ Your VIP access has been removed.</b>"
                )
            except Exception as e:
                logger.error(f"Could not notify user {user_id}: {e}")
        else:
            await message.reply_text(f"<b>❌ User <code>{user_id}</code> is not a VIP member.</b>")
            
    except ValueError:
        await message.reply_text("<b>❌ Invalid User ID. Must be integer.</b>")
    except Exception as e:
        await message.reply_text(f"<b>❌ Error: {e}</b>")

@Client.on_message(filters.command("declinevip") & filters.private)
async def decline_vip_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")
        
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> `/declinevip [user_id] [optional reason]`")
        
    try:
        user_id = int(message.command[1])
        reason = "Invalid/Fake screenshot"
        if len(message.command) >= 3:
            reason = message.text.split(None, 2)[2]
            
        await client.send_message(
            chat_id=user_id,
            text=f"❌ <b>Your VIP payment verification has been declined.</b>\n\n"
                 f"➜ <b>Reason:</b> {reason}\n\n"
                 f"If you believe this is a mistake, please contact support."
        )
        await message.reply_text(f"<b>❌ VIP verification declined and user <code>{user_id}</code> notified.</b>")
    except ValueError:
        await message.reply_text("<b>❌ Invalid User ID. Must be an integer.</b>")
    except Exception as e:
        await message.reply_text(f"<b>❌ Error: {e}</b>")

@Client.on_message(filters.command("msg") & filters.private)
async def msg_user_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")
        
    if len(message.command) < 3:
        return await message.reply_text("<b>Usage:</b> `/msg [user_id] [message]`")
        
    try:
        user_id = int(message.command[1])
        msg_text = message.text.split(None, 2)[2]
        
        await client.send_message(
            chat_id=user_id,
            text=msg_text
        )
        await message.reply_text(f"<b>✅ Message sent to User <code>{user_id}</code> successfully!</b>")
    except ValueError:
        await message.reply_text("<b>❌ Invalid User ID. Must be an integer.</b>")
    except Exception as e:
        await message.reply_text(f"<b>❌ Error: {e}</b>")

@Client.on_message(filters.command("listvip") & filters.private)
async def list_vip_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")
        
    try:
        # Clean up expired VIP users first
        import time
        await mongo_db.vip_users.delete_many({
            "bot_id": me.id,
            "expiry": {"$ne": None, "$lt": int(time.time())}
        })
        
        vip_list = []
        async for user in mongo_db.vip_users.find({"bot_id": me.id}):
            vip_list.append(user)
            
        if not vip_list:
            return await message.reply_text("<b>📭 No active VIP users found.</b>")
            
        # Sort VIP users by expiry date ascending (soonest first, Lifetime last)
        vip_list.sort(key=lambda x: x.get("expiry") if x.get("expiry") is not None else float('inf'))

        from datetime import datetime
        import pytz
        tz = pytz.timezone('Asia/Kolkata')
        text = f"<b>✨ <u>Active VIP Users ({len(vip_list)}):</u></b>\n\n"
        for i, user in enumerate(vip_list, 1):
            expiry = user.get("expiry")
            if expiry:
                expiry_str = datetime.fromtimestamp(expiry, tz).strftime('%Y-%m-%d %H:%M:%S')
            else:
                expiry_str = "Lifetime"
            text += f"{i}. User ID: <code>{user['user_id']}</code>\n" \
                    f"   Expiry: <code>{expiry_str} (IST)</code>\n\n"
                    
        # Send in chunks if too long
        if len(text) > 4000:
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                await message.reply_text(chunk)
        else:
            await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"<b>❌ Error: {e}</b>")

@Client.on_message(filters.command("makepaid") & filters.private)
async def makepaid_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")

    paid_links_enabled = bot_doc.get("paid_links", False) if bot_doc else False
    if not paid_links_enabled:
        return await message.reply("<b>❌ Paid Links feature is currently turned OFF. Please toggle it ON in /setting first.</b>")

    if len(message.command) < 2:
        return await message.reply("<b>Usage:</b> `/makepaid [payload_or_link]`\nExample: `/makepaid BATCH-1234` or `/makepaid https://t.me/BotName?start=BATCH-1234`")

    raw_payload = message.command[1].strip()
    payload = raw_payload
    if "start=" in raw_payload:
        payload = raw_payload.split("start=")[-1]
    payload = from_small_caps(payload)

    try:
        title_msg = await _ask(client, message.chat.id, "<b>📝 Please send the TITLE of this paid file:</b>", timeout=120)
        title = title_msg.text.strip() if title_msg.text else "Paid File"
    except asyncio.TimeoutError:
        return await message.reply("<b>❌ Timeout: Setup cancelled.</b>")

    try:
        price_msg = await _ask(client, message.chat.id, "<b>💵 Please send the PRICE of this file (e.g. 5$, 500 INR):</b>", timeout=120)
        price = price_msg.text.strip() if price_msg.text else "N/A"
    except asyncio.TimeoutError:
        return await message.reply("<b>❌ Timeout: Setup cancelled.</b>")

    try:
        qr_msg = await _ask(client, message.chat.id, "<b>🖼️ Please send the QR Code image for payment:</b>", timeout=120)
        if not qr_msg.photo:
            return await message.reply("<b>❌ Error: You must send an image/photo of the QR code. Setup cancelled.</b>")
        qr_file_id = qr_msg.photo.file_id
    except asyncio.TimeoutError:
        return await message.reply("<b>❌ Timeout: Setup cancelled.</b>")

    await mongo_db.paid_links.update_one(
        {"bot_id": me.id, "payload": payload},
        {"$set": {
            "title": title,
            "price": price,
            "qr_file_id": qr_file_id,
            "updated_at": time.time()
        }},
        upsert=True
    )

    await message.reply(f"<b>✅ Paid link successfully created!</b>\n\n<b>Payload:</b> <code>{payload}</code>\n<b>Title:</b> {title}\n<b>Price:</b> {price}")

@Client.on_message(filters.command("approvepaid") & filters.private)
async def approvepaid_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")

    if len(message.command) < 3:
        return await message.reply_text("<b>Usage:</b> `/approvepaid [user_id] [payload]`")

    try:
        user_id = int(message.command[1])
        raw_payload = message.command[2].strip()
        payload = from_small_caps(raw_payload)

        paid_doc = await mongo_db.paid_links.find_one({
            "bot_id": me.id, 
            "payload": re.compile(f"^{re.escape(payload)}$", re.IGNORECASE)
        })
        title = paid_doc.get("title", "Paid File") if paid_doc else "Paid File"

        await mongo_db.paid_unlocks.update_one(
            {"bot_id": me.id, "user_id": user_id, "payload": payload},
            {"$set": {"unlocked_at": time.time()}},
            upsert=True
        )

        await message.reply_text(f"<b>✅ Payment approved! User <code>{user_id}</code> has been granted access to payload: <code>{payload}</code></b>")

        try:
            bot_username = me.username
            deeplink = f"https://t.me/{bot_username}?start={payload}"
            await client.send_message(
                chat_id=user_id,
                text=f"<b>🎉 Payment Approved!</b>\n\nYour payment for file \"<b>{title}</b>\" has been verified.\n\n👉 <b>Click the link below to get your file:</b>\n{deeplink}"
            )
        except Exception as e:
            logger.error(f"Could not notify paid link user {user_id}: {e}")

    except ValueError:
        await message.reply_text("<b>❌ Invalid User ID. Must be integer.</b>")
    except Exception as e:
        await message.reply_text(f"<b>❌ Error: {e}</b>")

@Client.on_message(filters.command("post") & filters.private)
async def post_channel_handler(client, message: Message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner, moderators, and admins can use this command.</b>")

    if len(message.command) < 2:
        return await message.reply(
            "<b>📢 <u>Post to Channel Usage:</u></b>\n\n"
            "1️⃣ <b>Text Message:</b>\n"
            "<code>/post (channel_id_or_username) (your text message)</code>\n"
            "<i>Example:</i> <code>/post -1003842749347 Join our new bot @tazzamaal909_bot!</code>\n\n"
            "2️⃣ <b>Media / Photo / Video (by Replying):</b>\n"
            "Reply to any photo, video, or document message with:\n"
            "<code>/post (channel_id_or_username) (optional caption)</code>"
        )

    target_chat = message.command[1].strip()
    # Parse target chat ID if integer
    try:
        if target_chat.startswith("-100") or target_chat.isdigit() or (target_chat.startswith("-") and target_chat[1:].isdigit()):
            target_chat = int(target_chat)
    except ValueError:
        pass

    try:
        if message.reply_to_message:
            caption = message.text.split(None, 2)[2] if len(message.command) >= 3 else None
            sent = await message.reply_to_message.copy(chat_id=target_chat, caption=caption)
        else:
            if len(message.command) < 3:
                return await message.reply("<b>❌ Please provide message text or reply to a media message to post.</b>")
            msg_text = message.text.split(None, 2)[2]
            sent = await client.send_message(chat_id=target_chat, text=msg_text)

        await message.reply_text(
            f"<b>✅ Message posted successfully to <code>{target_chat}</code>!</b>\n"
            f"<b>Message ID:</b> <code>{sent.id}</code>"
        )
    except Exception as e:
        await message.reply_text(f"<b>❌ Failed to post to channel:</b>\n<code>{e}</code>")


@Client.on_message(filters.command(["editpost", "edit"]) & filters.private)
async def edit_post_handler(client, message: Message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner, moderators, and admins can use this command.</b>")

    if len(message.command) < 3:
        return await message.reply(
            "<b>✏️ <u>Edit Channel Post Usage:</u></b>\n\n"
            "<code>/editpost (channel_id_or_username) (message_id) (new_text)</code>\n"
            "<i>Example:</i> <code>/editpost -1003842749347 45 New updated message content!</code>"
        )

    target_chat = message.command[1].strip()
    try:
        if target_chat.startswith("-100") or target_chat.isdigit() or (target_chat.startswith("-") and target_chat[1:].isdigit()):
            target_chat = int(target_chat)
    except ValueError:
        pass

    try:
        msg_id = int(message.command[2])
    except ValueError:
        return await message.reply("<b>❌ Invalid Message ID. Must be an integer.</b>")

    if len(message.command) < 4:
        return await message.reply("<b>❌ Please provide the new text to update the post.</b>")

    new_text = message.text.split(None, 3)[3]

    try:
        try:
            edited = await client.edit_message_text(chat_id=target_chat, message_id=msg_id, text=new_text)
        except Exception:
            edited = await client.edit_message_caption(chat_id=target_chat, message_id=msg_id, caption=new_text)

        await message.reply_text(f"<b>✅ Message <code>{msg_id}</code> in <code>{target_chat}</code> successfully edited!</b>")
    except Exception as e:
        await message.reply_text(f"<b>❌ Failed to edit channel post:</b>\n<code>{e}</code>")


@Client.on_message(filters.command(["delpost", "del"]) & filters.private)
async def delete_post_handler(client, message: Message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner, moderators, and admins can use this command.</b>")

    if len(message.command) < 3:
        return await message.reply(
            "<b>🗑️ <u>Delete Channel Post Usage:</u></b>\n\n"
            "<code>/delpost (channel_id_or_username) (message_id)</code>\n"
            "<i>Example:</i> <code>/delpost -1003842749347 45</code>"
        )

    target_chat = message.command[1].strip()
    try:
        if target_chat.startswith("-100") or target_chat.isdigit() or (target_chat.startswith("-") and target_chat[1:].isdigit()):
            target_chat = int(target_chat)
    except ValueError:
        pass

    try:
        msg_id = int(message.command[2])
    except ValueError:
        return await message.reply("<b>❌ Invalid Message ID. Must be an integer.</b>")

    try:
        await client.delete_messages(chat_id=target_chat, message_ids=msg_id)
        await message.reply_text(f"<b>✅ Message <code>{msg_id}</code> deleted successfully from <code>{target_chat}</code>!</b>")
    except Exception as e:
        await message.reply_text(f"<b>❌ Failed to delete channel post:</b>\n<code>{e}</code>")


# ── Google Drive Automation & Migration Commands for Cloned Bots ──

async def upload_image_via_main_bot(thumb_path) -> tuple:
    """Uploads thumbnail photo to LOG_CHANNEL using StreamBot (main bot) and returns stream URL."""
    from config import LOG_CHANNEL, URL
    from TechVJ.utils.file_properties import get_name, get_hash
    from TechVJ.bot import StreamBot
    from urllib.parse import quote_plus
    
    try:
        if not LOG_CHANNEL:
            return None, "LOG_CHANNEL not configured"
            
        log_msg = await StreamBot.send_photo(chat_id=LOG_CHANNEL, photo=thumb_path)
        
        base_url = URL.strip()
        if not base_url.startswith("https://") and not base_url.startswith("http://"):
            base_url = "https://" + base_url
        elif base_url.startswith("http://"):
            base_url = base_url.replace("http://", "https://")
            
        file_name = get_name(log_msg) or "image.jpg"
        stream_url = f"{base_url.rstrip('/')}/{str(log_msg.id)}/{quote_plus(file_name)}?hash={get_hash(log_msg)}"
        
        return stream_url, log_msg
    except Exception as e:
        logger.error(f"Error uploading image via StreamBot: {e}")
        return None, f"Error: {e}"


@Client.on_message(filters.command("upload_gdrive") & filters.private)
async def clone_upload_gdrive_cmd_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")

    replied = message.reply_to_message
    if not replied:
        return await message.reply_text("<b>❌ Please reply to a video file to upload to Google Drive.</b>")
        
    media = replied.video or replied.document
    if not media:
        return await message.reply_text("<b>❌ Replied message does not contain a video or document file.</b>")
        
    if replied.document and not (media.mime_type and media.mime_type.startswith("video/")):
        return await message.reply_text("<b>❌ The replied document is not a valid video file.</b>")
        
    caption = replied.caption or ""
    lines = [l.strip() for l in caption.split('\n') if l.strip()]
    
    title = lines[0] if lines else getattr(media, "file_name", f"Video_{int(time.time())}")
    title = re.sub(r'<[^>]+>', '', title)
    title = re.sub(r'[*_`~]', '', title).strip()
    
    category = "General"
    if len(message.command) > 1:
        category = message.text.split(" ", 1)[1].strip()
    else:
        for line in lines:
            if line.lower().startswith("category:") or line.lower().startswith("genre:"):
                parsed_cat = line.split(":", 1)[1].strip()
                parsed_cat = re.sub(r'<[^>]+>', '', parsed_cat).strip()
                if parsed_cat:
                    category = parsed_cat
                    break

    sts = await message.reply_text("<b>⏳ Downloading thumbnail and generating image link...</b>")
    
    image_url = None
    if media.thumbs:
        try:
            thumb_file = await client.download_media(media.thumbs[0].file_id)
            if thumb_file:
                image_url, thumb_msg = await upload_image_via_main_bot(thumb_file)
                try:
                    os.remove(thumb_file)
                except:
                    pass
        except Exception as e:
            logger.error(f"Thumbnail generation error: {e}")
            
    if not image_url or image_url.startswith("Error"):
        image_url = "https://graph.org/file/6a869326b7756a622bd48-6213fc97b75f7bfb30.jpg"
        
    await sts.edit_text("<b>⏳ Starting video download from Telegram...</b>")
    
    temp_dir = "scratch/temp_upload"
    os.makedirs(temp_dir, exist_ok=True)
    
    class ProgressState:
        def __init__(self):
            self.last_update = 0

    state = ProgressState()
    
    async def progress_callback(current, total):
        now = time.time()
        if now - state.last_update < 4:
            return
        state.last_update = now
        pct = (current / total) * 100
        try:
            await sts.edit_text(f"<b>⏳ Downloading video from Telegram...</b>\n<code>[{'●' * int(pct // 10)}{'○' * (10 - int(pct // 10))}] {pct:.1f}%</code>")
        except:
            pass

    local_filename = getattr(media, "file_name", f"video_{int(time.time())}.mp4")
    local_path = os.path.join(temp_dir, local_filename)
    
    try:
        downloaded_path = await client.download_media(
            message=media.file_id,
            file_name=local_path,
            progress=progress_callback
        )
    except Exception as e:
        return await sts.edit_text(f"<b>❌ Telegram Download Failed:</b>\n<code>{e}</code>")
        
    if not downloaded_path or not os.path.exists(downloaded_path):
        return await sts.edit_text("<b>❌ Failed to download file from Telegram.</b>")
        
    await sts.edit_text("<b>⏳ Uploading video to Google Drive with anti-ban masking...</b>")
    
    from gdrive_helper import upload_file_to_gdrive
    gdrive_file_id, masked_name = upload_file_to_gdrive(downloaded_path, local_filename)
    
    try:
        os.remove(downloaded_path)
    except Exception as e:
        logger.error(f"Failed to remove temp file: {e}")
        
    if not gdrive_file_id:
        return await sts.edit_text(f"<b>❌ GDrive Upload Failed:</b>\n<code>{masked_name}</code>")
        
    import uuid
    post_id = str(uuid.uuid4())[:8]
    
    await mongo_db.posts.insert_one({
        "_id": post_id,
        "title": title,
        "image_url": image_url,
        "category": category,
        "gdrive_file_id": gdrive_file_id,
        "is_gdrive": True,
        "bot_username": me.username,
        "created_at": time.time(),
        "views": 0,
        "reactions": {"❤️": 0, "👍": 0, "🔥": 0, "💦": 0}
    })
    
    await sts.edit_text(
        f"<b>✅ Video uploaded and synced successfully!</b>\n\n"
        f"📋 <b>Post ID:</b> <code>{post_id}</code>\n"
        f"🎬 <b>Title:</b> {title}\n"
        f"📂 <b>Category:</b> {category}\n"
        f"🔑 <b>GDrive File ID:</b> <code>{gdrive_file_id}</code>\n"
        f"🎭 <b>Masked Name:</b> <code>{masked_name}</code>"
    )


# Global migration lock to prevent multiple tasks
CLONE_MIGRATION_RUNNING = False

async def clone_migration_background_worker(client, status_msg, admin_chat_id, bot_username):
    global CLONE_MIGRATION_RUNNING
    CLONE_MIGRATION_RUNNING = True
    
    from gdrive_helper import upload_file_to_gdrive
    from config import LOG_CHANNEL
    import uuid
    import os
    import base64
    import json

    try:
        query = {"bot_username": bot_username, "is_gdrive": {"$ne": True}}
        total_posts = await mongo_db.posts.count_documents(query)
        
        await status_msg.edit_text(f"<b>🚀 Starting GDrive Migration!</b>\n🔍 Found <b>{total_posts}</b> posts to process for @{bot_username}.\n<i>I will update you every 10 posts.</i>")
        
        temp_dir = "scratch/temp_migration"
        os.makedirs(temp_dir, exist_ok=True)
        
        success_count = 0
        fail_count = 0
        
        posts_cursor = mongo_db.posts.find(query).sort("created_at", -1)
        
        async for post in posts_cursor:
            post_id = post["_id"]
            title = post.get("title", "Untitled")
            deeplink = post.get("file_deeplink", "")
            
            gdrive_ids = []
            is_batch = False
            
            if not deeplink:
                continue
                
            if deeplink.startswith("BATCH-"):
                is_batch = True
                try:
                    batch_file_id = deeplink.split("-", 1)[1]
                    decoded_msg_id = int(base64.urlsafe_b64decode(batch_file_id + "=" * (-len(batch_file_id) % 4)).decode("ascii"))
                    
                    # Log channel JSON fetching
                    from TechVJ.bot import StreamBot
                    msg = await StreamBot.get_messages(LOG_CHANNEL, decoded_msg_id)
                    if msg and msg.document:
                        batch_json_path = await StreamBot.download_media(msg.document.file_id, file_name=os.path.join(temp_dir, f"batch_{post_id}.json"))
                        if batch_json_path and os.path.exists(batch_json_path):
                            with open(batch_json_path, "r", encoding="utf-8") as f:
                                batch_data = json.load(f)
                            try:
                                os.remove(batch_json_path)
                            except:
                                pass
                                
                            for b_idx, item in enumerate(batch_data):
                                channel_id = item["channel_id"]
                                msg_id = item["msg_id"]
                                
                                video_msg = await client.get_messages(channel_id, msg_id)
                                if video_msg and (video_msg.video or video_msg.document):
                                    media = video_msg.video or video_msg.document
                                    local_filename = getattr(media, "file_name", f"video_{post_id}_{b_idx}.mp4")
                                    local_path = os.path.join(temp_dir, local_filename)
                                    
                                    video_path = await client.download_media(media.file_id, file_name=local_path)
                                    if video_path and os.path.exists(video_path):
                                        gdrive_id, masked_name = upload_file_to_gdrive(video_path, local_filename)
                                        try:
                                            os.remove(video_path)
                                        except:
                                            pass
                                        if gdrive_id:
                                            gdrive_ids.append(gdrive_id)
                except Exception as e:
                    logger.error(f"Error migrating batch {post_id}: {e}")
            else:
                try:
                    decoded = base64.urlsafe_b64decode(deeplink + "=" * (-len(deeplink) % 4)).decode("ascii")
                    if "_" in decoded:
                        _, decode_file_id = decoded.split("_", 1)
                    else:
                        decode_file_id = decoded

                    file_id = None
                    if decode_file_id.isdigit():
                        from TechVJ.bot import StreamBot
                        msg = await StreamBot.get_messages(LOG_CHANNEL, int(decode_file_id))
                        if msg and msg.media:
                            media = getattr(msg, msg.media.value)
                            file_id = media.file_id
                            local_filename = getattr(media, "file_name", f"video_{post_id}.mp4")
                    else:
                        file_doc = await mongo_db.clone_files.find_one({"_id": decode_file_id})
                        if file_doc:
                            file_id = file_doc.get("file_id")
                            local_filename = f"video_{post_id}.mp4"
                            
                    if file_id:
                        local_path = os.path.join(temp_dir, local_filename)
                        video_path = await client.download_media(file_id, file_name=local_path)
                        if video_path and os.path.exists(video_path):
                            gdrive_id, masked_name = upload_file_to_gdrive(video_path, local_filename)
                            try:
                                os.remove(video_path)
                            except:
                                pass
                            if gdrive_id:
                                gdrive_ids.append(gdrive_id)
                except Exception as e:
                    logger.error(f"Error migrating single file {post_id}: {e}")

            if gdrive_ids:
                await mongo_db.posts.update_one(
                    {"_id": post_id},
                    {
                        "$set": {
                            "is_gdrive": True,
                            "is_batch": is_batch,
                            "gdrive_file_id": gdrive_ids[0],
                            "gdrive_file_ids": gdrive_ids
                        }
                    }
                )
                success_count += 1
            else:
                fail_count += 1
                
            processed = success_count + fail_count
            if processed % 10 == 0 or processed == total_posts:
                try:
                    await client.send_message(
                        chat_id=admin_chat_id,
                        text=f"<b>📊 GDrive Migration Progress:</b>\n"
                             f"Processed: <code>{processed}/{total_posts}</code>\n"
                             f"✅ Success: <code>{success_count}</code>\n"
                             f"❌ Failed: <code>{fail_count}</code>"
                    )
                except Exception as ex:
                    logger.error(f"Failed to send migration progress message: {ex}")
                    
        await client.send_message(
            chat_id=admin_chat_id,
            text=f"<b>🎉 GDrive Migration Task Finished!</b>\n\n"
                 f"Total Processed: <code>{success_count + fail_count}</code>\n"
                 f"✅ Successfully Migrated: <code>{success_count}</code>\n"
                 f"❌ Failed: <code>{fail_count}</code>\n\n"
                 f"All GDrive videos are now playable in your React Native app."
        )
    except Exception as e:
        logger.error(f"Migration background worker error: {e}")
        try:
            await client.send_message(chat_id=admin_chat_id, text=f"<b>❌ GDrive Migration crashed with error:</b>\n<code>{e}</code>")
        except:
            pass
    finally:
        CLONE_MIGRATION_RUNNING = False


@Client.on_message(filters.command("migrate_gdrive") & filters.private)
async def clone_migrate_gdrive_cmd_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods and message.from_user.id not in ADMINS:
        return await message.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")

    global CLONE_MIGRATION_RUNNING
    if CLONE_MIGRATION_RUNNING:
        return await message.reply_text("<b>⚠️ GDrive Migration task is already running in the background! Please wait.</b>")
        
    sts = await message.reply_text("<b>⏳ Spawning background task to migrate all old videos...</b>")
    
    # Run task in background
    asyncio.create_task(clone_migration_background_worker(client, sts, message.chat.id, me.username))


