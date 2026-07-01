# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import os
import logging
import random
import asyncio
import time
from validators import domain
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery, Message, WebAppInfo
from utils import verify_user, check_token, check_verification, get_token, is_subscribed, is_subscribed_universal, get_tma_link, verify_tma_user, check_tma_verification, is_vip, TMA_TIMEOUT, is_token_consumed, consume_token, validate_tma_token
from config import *
from config import TMA_MODE, MONETAG_ZONE_ID, URL
import config
import re
import json
import base64
from urllib.parse import quote_plus
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.bot import StreamBot
from plugins.clone import async_mongo_db as clone_mongo_db
from clone_plugins.dbusers import clonedb
logger = logging.getLogger(__name__)

def is_valid_url(url):
    """Check if a URL is a valid http/https URL for use in Telegram buttons."""
    if not url:
        return False
    return url.startswith("http://") or url.startswith("https://")

BATCH_FILES = {}

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

def formate_file_name(file_name):
    if file_name is None:
        file_name = ""
    chars = ["[", "]", "(", ")"]
    for c in chars:
        file_name = file_name.replace(c, "")
    file_name = ' '.join(filter(lambda x: not x.startswith('http') and not x.startswith('@') and not x.startswith('www.'), file_name.split()))
    return file_name

def parse_stars_prices(plans_text):
    stars_1m = None
    stars_3m = None
    stars_lifetime = None
    
    if not plans_text:
        return stars_1m, stars_3m, stars_lifetime
        
    # Remove HTML tags to process clean text
    text = re.sub(r'<[^>]+>', '', plans_text).lower()
    
    # Split by lines
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # Find all integers
        numbers = re.findall(r'\b\d+\b', line)
        if not numbers:
            continue
            
        # Check matching keywords
        if any(kw in line for kw in ["1 month", "1month", "30 days", "30days", "monthly"]):
            price_candidates = [int(n) for n in numbers if n not in ["1", "30"]]
            if price_candidates:
                stars_1m = price_candidates[0]
            elif len(numbers) == 1:
                stars_1m = int(numbers[0])
        elif any(kw in line for kw in ["3 month", "3month", "90 days", "90days"]):
            price_candidates = [int(n) for n in numbers if n not in ["3", "90"]]
            if price_candidates:
                stars_3m = price_candidates[0]
            elif len(numbers) == 1:
                stars_3m = int(numbers[0])
        elif any(kw in line for kw in ["lifetime", "life time", "life-time", "forever"]):
            price_candidates = [int(n) for n in numbers]
            if price_candidates:
                stars_lifetime = price_candidates[0]
                
    return stars_1m, stars_3m, stars_lifetime

async def get_invalid_link_btn(client, user_id, data):
    me = client.me or await client.get_me()
    if config.TMA_MODE:
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
        tma_link = await get_tma_link(client, user_id, tma_app_url, file_data=file_data)
        return InlineKeyboardMarkup([[InlineKeyboardButton("Click Here to Get Verification", web_app=WebAppInfo(url=tma_link))]])
    else:
        if VERIFY_MODE:
            verify_url = await get_token(client, user_id, f"https://telegram.me/{me.username}?start=")
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("Click Here to Get Verification", url=verify_url)],
                [InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)]
            ])
        else:
            return InlineKeyboardMarkup([[InlineKeyboardButton("Click Here to Get Verification", url=f"https://t.me/{me.username}?start=true")]])

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ0


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        me = client.me or await client.get_me()
        if not await db.is_user_exist(message.from_user.id):
            try:
                await db.add_user(message.from_user.id, message.from_user.first_name)
                await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))
            except: pass
        
        # Universal Force Sub Check
        try:
            chk_u = await is_subscribed_universal(client, message)
            if chk_u == "kicked":
                return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
            if type(chk_u) == list:
                buttons = []
                for channel_id in chk_u:
                    try:
                        chat = await client.get_chat(channel_id)
                        link = chat.invite_link
                        if not link:
                            try:
                                inv = await client.create_chat_invite_link(channel_id)
                                link = inv.invite_link
                            except:
                                link = f"https://t.me/{chat.username}" if chat.username else None
                        if link:
                            buttons.append([InlineKeyboardButton("ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=link)])
                    except: continue
                buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=true")])
                return await message.reply_text(
                    text="<b>ʜᴇʏ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜɴɪᴠᴇʀsᴀʟ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!</b>",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
        except Exception as e:
            logger.error(f"Universal Sub Error: {e}")

        # Main Force Sub Check
        try:
            chk = await is_subscribed(client, message)
            if chk == "kicked":
                return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
            if type(chk) == list:
                buttons = []
                for i, channel_id in enumerate(chk, start=1):
                    try:
                        chat = await client.get_chat(channel_id)
                        link = chat.invite_link
                        if not link:
                            try:
                                inv = await client.create_chat_invite_link(channel_id)
                                link = inv.invite_link
                            except:
                                link = f"https://t.me/{chat.username}" if chat.username else None
                        if link:
                            buttons.append([InlineKeyboardButton(f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {i}", url=link)])
                        else:
                            buttons.append([InlineKeyboardButton(f"⚠️ Bot Not Admin in Channel {i}", url=f"https://t.me/{me.username}")])
                    except: 
                        buttons.append([InlineKeyboardButton(f"⚠️ Bot Not Admin in Channel {i}", url=f"https://t.me/{me.username}")])
                try_again_url = f"https://t.me/{me.username}?start={message.command[1]}" if len(message.command) == 2 else f"https://t.me/{me.username}?start=true"
                buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=try_again_url)])
                return await message.reply_text(
                    text=script.FORCE_SUB_TEXT.format(message.from_user.mention),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
        except Exception as e:
            logger.error(f"Main Sub Error: {e}")

        if len(message.command) != 2 or message.command[1] == "true":
            portal_url = f"{URL.rstrip('/')}/portal?uid={message.from_user.id}&bot={me.username}"
            buttons = [[
                InlineKeyboardButton('Viral Videos 💦', web_app=WebAppInfo(url=portal_url))
            ],[
                InlineKeyboardButton('⚙️ sᴇᴛᴛɪɴɢs', callback_data='settings'),
                InlineKeyboardButton('🤖 ᴄʟᴏɴᴇ', callback_data='clone_manage')
            ],[
                InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            try:
                await message.reply_photo(
                    photo=random.choice(PICS),
                    caption=script.START_TXT.format(message.from_user.mention, me.mention),
                    reply_markup=reply_markup
                )
            except:
                await message.reply_text(
                    text=script.START_TXT.format(message.from_user.mention, me.mention),
                    reply_markup=reply_markup
                )
            return

        # Handle File ID
        data = message.command[1]

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
                                plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
                                upsell_btn = []
                                if plan_cfg:
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
                        # Mark verified for 3 hours in database/memory
                        await verify_tma_user(message.from_user.id, token)
                        # Notify user of successful verification
                        await message.reply_text(
                            text=script.TMA_VERIFIED_TEXT.format(message.from_user.mention, hours=TMA_TIMEOUT // 3600),
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

        
        # Handle clone redirect from button
        if data == "clone":
            from plugins.clone import clone
            return await clone(client, message)
            
        if data.startswith("verifyclone_"):
            bot_id = int(data.split("_")[-1])
            bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
            if not bot or int(bot.get("user_id", 0)) != message.from_user.id:
                return await message.reply("<b>❌ You don't own this bot!</b>")
            
            vplink_verified = bot.get("vplink_verified", False)
            if not vplink_verified:
                req = await clone_mongo_db.vplink_requests.find_one({"bot_id": bot_id, "status": "pending"})
                if req:
                    text = "<b>waiting msg please wait for confirmation</b>"
                    buttons = [[InlineKeyboardButton("🔙 Back", callback_data=f"cust_{bot_id}")]]
                    return await message.reply_text(
                        text=text,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    caption = (
                        "<b>⚠️ You need to register under our referral link first!</b>\n\n"
                        "1️⃣ Click this link to register: https://vplink.in/ref/Priyanshu7890\n"
                        "2️⃣ Create an account on VPLink.\n"
                        "3️⃣ Go to Tools -> Developers API (as shown in the image below) to get your API token.\n"
                        "4️⃣ Once done, click <b>📤 Submit Request</b> below.\n\n"
                        "<i>Our admin will manually verify and approve your request. Once verified, you can set your API key.</i>"
                    )
                    buttons = [
                        [InlineKeyboardButton("🔗 Register on VPLink", url="https://vplink.in/ref/Priyanshu7890")],
                        [InlineKeyboardButton("📤 Submit Request", callback_data=f"req_vplink_{bot_id}")],
                        [InlineKeyboardButton("🔙 Back", callback_data=f"cust_{bot_id}")]
                    ]
                    try:
                        return await message.reply_photo(
                            photo="vplink_tutorial.png",
                            caption=caption,
                            reply_markup=InlineKeyboardMarkup(buttons)
                        )
                    except Exception as e:
                        return await message.reply_text(
                            text=caption,
                            reply_markup=InlineKeyboardMarkup(buttons),
                            disable_web_page_preview=True
                        )
            else:
                tma_mode = bot.get("tma_mode", False)
                status_txt = "ON 🟢" if tma_mode else "OFF 🔴"
                tma_btn = "Disable ❌ TMA Ads" if tma_mode else "Enable ✅ TMA Ads"
                api_key = bot.get("shortener_api") or "Not set"
                validity = bot.get("token_timeout", 10800) // 3600
                tutorial = bot.get("token_tutorial", "None")
                api_display = f"<code>{api_key}</code>" if api_key != "Not set" else "<i>⚠️ Not set — tap Set API Key!</i>"
                buttons = [
                    [InlineKeyboardButton("🔑 Set API Key", callback_data=f"tok_api_{bot_id}")],
                    [InlineKeyboardButton("⏱ Validity", callback_data=f"tok_val_{bot_id}"), InlineKeyboardButton("📖 Tutorial", callback_data=f"tok_tut_{bot_id}")],
                    [InlineKeyboardButton(f"{tma_btn}", callback_data=f"tok_tma_{bot_id}"), InlineKeyboardButton("🧹 Clear Settings", callback_data=f"tok_clr_{bot_id}")],
                    [InlineKeyboardButton("🔙 Back", callback_data=f"cust_{bot_id}")]
                ]
                text = (
                    f"<b><u>⚙️ TMA Ads Setting</u></b>\n\n"
                    f"  - Status: {status_txt}\n"
                    f"  - Domain: <code>vplink.in</code>\n"
                    f"  - API Key: {api_display}\n"
                    f"  - Tutorial: {tutorial}\n"
                    f"  - Validity: <code>{validity} hours</code>"
                )
                return await message.reply_text(
                    text=text,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=enums.ParseMode.HTML,
                    disable_web_page_preview=True
                )

        if data.startswith("manageclone_"):
            bot_id = int(data.split("_")[-1])
            bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
            if not bot or int(bot.get("user_id", 0)) != message.from_user.id:
                return await message.reply("<b>❌ You don't own this bot!</b>")
                
            buttons = [
                [InlineKeyboardButton("START MSG", callback_data=f"startmsg_{bot_id}"), InlineKeyboardButton("FORCE SUB", callback_data=f"forcesub_{bot_id}")],
                [InlineKeyboardButton("MODERATORS", callback_data=f"mods_{bot_id}"), InlineKeyboardButton("AUTO DELETE", callback_data=f"autodel_{bot_id}")],
                [InlineKeyboardButton("NO FORWARD", callback_data=f"nofwd_{bot_id}"), InlineKeyboardButton("ACCESS TOKEN & TMA", callback_data=f"tokencfg_{bot_id}")],
                [InlineKeyboardButton("MODE", callback_data=f"mode_{bot_id}"), InlineKeyboardButton("DEACTIVATE", callback_data=f"deactivate_{bot_id}")],
                [InlineKeyboardButton("STATS", callback_data=f"stats_{bot_id}"), InlineKeyboardButton("RESTART", callback_data=f"restart_{bot_id}")],
                [InlineKeyboardButton("DELETE", callback_data=f"delete_{bot_id}")],
                [InlineKeyboardButton("BACK", callback_data="clone_manage")]
            ]
            
            return await message.reply_text(
                text=f"<b>🪄 <u>Customize Clone</u>\n\n➜ Name: <i>{bot['name']}</i>\n\nConfigure Your Clone Settings Using Given Buttons</b>",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        
        # ... rest of the logic ...
        try:
            pre, file_id = data.split('_', 1)
        except:
            file_id = data
            pre = ""
        if data.split("-", 1)[0] == "verify":
            userid = data.split("-", 2)[1]
            token = data.split("-", 3)[2]
            if str(message.from_user.id) != str(userid):
                reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
                return await message.reply_text(
                    text="<b>This link is not valid, either it is used or broken.</b>",
                    reply_markup=reply_markup,
                    protect_content=True
                )
            is_valid = await check_token(client, userid, token)
            if is_valid == True:
                await message.reply_text(
                    text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all files till today midnight.</b>",
                    protect_content=True
                )
                await verify_user(client, userid, token)
            else:
                reply_markup = await get_invalid_link_btn(client, message.from_user.id, data)
                return await message.reply_text(
                    text="<b>This link is not valid, either it is used or broken.</b>",
                    reply_markup=reply_markup,
                    protect_content=True
                )
        # TMA verification callback: /start tma-{uid}-{token}
        elif data.split("-", 1)[0] == "tma":
            parts = data.split("-")
            if len(parts) >= 3:
                tma_uid = int(parts[1])
                tma_token = "-".join(parts[2:])  # token may contain a dash
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
                        plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
                        upsell_btn = []
                        if plan_cfg:
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

                ok = await verify_tma_user(tma_uid, tma_token)
                if ok:
                    await consume_token(tma_token)
                    await message.reply_text(
                        text=script.TMA_VERIFIED_TEXT.format(message.from_user.mention, hours=TMA_TIMEOUT // 3600),
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
        elif data.split("-", 1)[0] == "BATCH":
            try:
                user_is_vip = await is_vip(me.id, message.from_user.id)
                if not user_is_vip:
                    # TMA Mode: use Monetag Mini App for verification
                    if config.TMA_MODE and not is_unlocked and not await check_tma_verification(message.from_user.id):
                        tma_app_url = f"{URL.rstrip('/')}/tma"
                        # Pass the raw /start data so the Mini App knows which file to deliver
                        tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data)
                        btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))]]
                        plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
                        if plan_cfg:
                            btn.append([InlineKeyboardButton("💳 Buy Plan (Skip Ads)", callback_data="buy_plan")])
                        await message.reply_text(
                            text=script.TMA_UNLOCK_TEXT.format(message.from_user.mention, hours=TMA_TIMEOUT // 3600),
                            protect_content=True,
                            reply_markup=InlineKeyboardMarkup(btn)
                        )
                        return
                    elif not config.TMA_MODE and not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
                        btn = [[
                            InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{BOT_USERNAME}?start="))
                        ],[
                            InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
                        ]]
                        await message.reply_text(
                            text="<b>You are not verified !\nKindly verify to continue !</b>",
                            protect_content=True,
                            reply_markup=InlineKeyboardMarkup(btn)
                        )
                        return
            except Exception as e:
                return await message.reply_text(f"**Error - {e}**")
            sts = await message.reply("**🔺 ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ**")
            file_id = data.split("-", 1)[1]
            msgs = BATCH_FILES.get(file_id)
            if not msgs:
                decode_file_id = base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4)).decode("ascii")
                msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
                media = getattr(msg, msg.media.value)
                file_id = media.file_id
                file = await client.download_media(file_id)
                try: 
                    with open(file) as file_data:
                        msgs=json.loads(file_data.read())
                except:
                    await sts.edit("FAILED")
                    return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
                os.remove(file)
                BATCH_FILES[file_id] = msgs
                
            filesarr = []
            for msg in msgs:
                channel_id = int(msg.get("channel_id"))
                msgid = msg.get("msg_id")
                info = await client.get_messages(channel_id, int(msgid))
                if info.media:
                    file_type = info.media
                    file = getattr(info, file_type.value)
                    f_caption = getattr(info, 'caption', '')
                    if f_caption:
                        f_caption = f"@viralverse0909 {f_caption.html}"
                    old_title = getattr(file, "file_name", "")
                    title = formate_file_name(old_title)
                    size=get_size(int(file.file_size))
                    if BATCH_FILE_CAPTION:
                        try:
                            f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                        except:
                            f_caption=f_caption
                    if f_caption is None:
                        f_caption = f"@viralverse0909 {title}"
                    reply_markup = None
                    if config.STREAM_MODE == True:
                            if info.video or info.document:
                                try:
                                    # Forward file to LOG_CHANNEL so the stream server can access it by msg ID
                                    log_msg = await StreamBot.copy_message(
                                        chat_id=LOG_CHANNEL,
                                        from_chat_id=info.chat.id,
                                        message_id=info.id
                                    )
                                except Exception as _fwd_err:
                                    logger.warning(f"Batch stream: could not forward to LOG_CHANNEL: {_fwd_err}")
                                    log_msg = info  # fallback (stream link may not work)
                                fileName = {quote_plus(get_name(log_msg))}
                                stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                                download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                                # Telegram only accepts https:// URLs in inline buttons
                                if is_valid_url(stream) and is_valid_url(download) and stream.startswith("https://") and download.startswith("https://"):
                                    button = [[
                                        InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
                                        InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
                                    ],[
                                        InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
                                    ],[
                                        InlineKeyboardButton("Jᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/viralverse0909")
                                    ]]
                                    reply_markup=InlineKeyboardMarkup(button)
                    try:
                        msg = await info.copy(chat_id=message.from_user.id, caption=f_caption, protect_content=False, reply_markup=reply_markup)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        msg = await info.copy(chat_id=message.from_user.id, caption=f_caption, protect_content=False, reply_markup=reply_markup)
                    except:
                        continue
                else:
                    try:
                        msg = await info.copy(chat_id=message.from_user.id, protect_content=False)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                        msg = await info.copy(chat_id=message.from_user.id, protect_content=False)
                    except:
                        continue
                filesarr.append(msg)
                await asyncio.sleep(1) 
            await sts.delete()
            # ── VIP Upsell for TMA-verified non-VIP users ──
            if config.TMA_MODE and not user_is_vip:
                try:
                    me = client.me or await client.get_me()
                    plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
                    upsell_btn = []
                    if plan_cfg:
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
            if AUTO_DELETE_MODE == True:
                k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} mins</u> 🫥 <i>(Due to Copyright Issues)</i>.\n\nPlease forward this File/Video to your Saved Messages and Start Download there</b>")
                await asyncio.sleep(AUTO_DELETE_TIME)
                for x in filesarr:
                    try:
                        await x.delete()
                    except:
                        pass
                try:
                    await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
                except:
                    pass
            return

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

        pre, decode_file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        user_is_vip = await is_vip(me.id, message.from_user.id)
        if not user_is_vip:
            # TMA Mode: use Monetag Mini App for verification
            if config.TMA_MODE and not is_unlocked and not await check_tma_verification(message.from_user.id):
                tma_app_url = f"{URL.rstrip('/')}/tma"
                # Pass the raw /start data so the Mini App knows which file to deliver
                tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data)
                btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))]]
                plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
                if plan_cfg:
                    btn.append([InlineKeyboardButton("💳 Buy Plan (Skip Ads)", callback_data="buy_plan")])
                await message.reply_text(
                    text=script.TMA_UNLOCK_TEXT.format(message.from_user.mention, hours=TMA_TIMEOUT // 3600),
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            elif not config.TMA_MODE and not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
                btn = [[
                    InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{BOT_USERNAME}?start="))
                ],[
                    InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
                ]]
                await message.reply_text(
                    text="<b>You are not verified !\nKindly verify to continue !</b>",
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
        try:
            msg = await client.get_messages(LOG_CHANNEL, int(decode_file_id))
            if msg.media:
                media = getattr(msg, msg.media.value)
                title = formate_file_name(media.file_name)
                size=get_size(media.file_size)
                f_caption = f"@viralverse0909 <code>{title}</code>"
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                    except:
                        f_caption = f"@viralverse0909 <code>{title}</code>"
                reply_markup = None
                if config.STREAM_MODE == True:
                    if msg.video or msg.document:
                        log_msg = msg
                        fileName = {quote_plus(get_name(log_msg))}
                        stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                        download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                        # Telegram only accepts https:// URLs in inline buttons
                        if is_valid_url(stream) and is_valid_url(download) and stream.startswith("https://") and download.startswith("https://"):
                            button = [[
                                InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download),
                                InlineKeyboardButton('• ᴡᴀᴛᴄʜ •', url=stream)
                            ],[
                                InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
                            ],[
                                InlineKeyboardButton("Jᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/viralverse0909")
                            ]]
                            reply_markup=InlineKeyboardMarkup(button)
                del_msg = await msg.copy(chat_id=message.from_user.id, caption=f_caption, reply_markup=reply_markup, protect_content=False)
            else:
                del_msg = await msg.copy(chat_id=message.from_user.id, protect_content=False)
            # ── VIP Upsell for TMA-verified non-VIP users ──
            if config.TMA_MODE and not user_is_vip:
                try:
                    plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
                    upsell_btn = []
                    if plan_cfg:
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
            if AUTO_DELETE_MODE == True:
                k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} mins</u> 🫥 <i>(Due to Copyright Issues)</i>.\n\nPlease forward this File/Video to your Saved Messages and Start Download there</b>")
                await asyncio.sleep(AUTO_DELETE_TIME)
                try:
                    await del_msg.delete()
                except:
                    pass
                try:
                    await k.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
                except:
                    pass
            return
        except Exception as e:
            logger.exception(f"File Send Error: {e}")
            try:
                await message.reply_text(f"<b>⚠️ Error sending file.\n\nError:</b> <code>{e}</code>")
            except:
                pass
        
    except Exception as e:
        try: await message.reply_text(f"<b>⚠️ Error occurred while processing /start command.\n\nError:</b> <code>{e}</code>")
        except: pass

@Client.on_message(filters.command("stats") & filters.user(ADMINS) & filters.private)
async def stats_handler(client, message):
    m = await message.reply_text("<b>Calculating statistics...</b>")
    
    # 1. Main Bot Users
    main_users = await db.total_users_count()
    
    # 2. Cloned Bots Statistics
    total_clones = 0
    total_clone_users = 0
    clone_details = []
    buttons = []
    
    try:
        bots = [b async for b in clone_mongo_db.bots.find({})]
        total_clones = len(bots)
        bots_data = []
        for bot in bots:
            bot_id_str = str(bot.get("bot_id"))
            bot_name = bot.get("name", "Unknown")
            bot_username = bot.get("username", "Unknown")
            bot_id = bot.get("bot_id")
            try:
                count = await clonedb.db[bot_id_str].count_documents({})
            except Exception:
                count = 0
            total_clone_users += count
            bots_data.append({
                "bot_id": bot_id,
                "name": bot_name,
                "username": bot_username,
                "count": count
            })
        
        # Sort bots by user count in descending order
        bots_data.sort(key=lambda x: x["count"], reverse=True)
        
        for item in bots_data:
            clone_details.append(f"• <b>{item['name']}</b> (@{item['username']}): <code>{item['count']}</code> users")
            buttons.append([InlineKeyboardButton(f"🗑 Delete @{item['username']}", callback_data=f"delbot_{item['bot_id']}")])
    except Exception as e:
        logger.error(f"Error fetching clone stats: {e}")
        
    clones_list_text = "\n".join(clone_details) if clone_details else "<i>No clones active.</i>"
    
    await m.edit_text(
        f"<b>📊 <u>Bot Statistics</u>\n\n"
        f"👤 Main Bot Users: <code>{main_users}</code>\n"
        f"🤖 Total Clones Made: <code>{total_clones}</code>\n"
        f"👥 Total Users Across Clones: <code>{total_clone_users}</code>\n\n"
        f"📋 <u>Cloned Bots List:</u>\n"
        f"{clones_list_text}</b>",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
    )

@Client.on_message(filters.command("validity") & filters.user(ADMINS) & filters.private)
async def tma_validity_command(client, message):
    from utils import TMA_VERIFIED, VERIFIED, TMA_TIMEOUT
    import time
    
    text = "<b>📅 <u>Active Verifications</u></b>\n\n"
    
    # 1. TMA Verifications (dynamic validity from TMA_TIMEOUT)
    tma_count = 0
    tma_hours = TMA_TIMEOUT // 3600
    tma_text = f"<b>⚡ TMA Verifications ({tma_hours}-Hour Validity):</b>\n"
    current_time = time.time()
    for uid, verified_time in list(TMA_VERIFIED.items()):
        elapsed = current_time - verified_time
        if elapsed < TMA_TIMEOUT:
            tma_count += 1
            remaining = int(TMA_TIMEOUT - elapsed)
            hours = remaining // 3600
            mins = (remaining % 3600) // 60
            tma_text += f"• <code>{uid}</code> (Remaining: {hours}h {mins}m)\n"
        else:
            TMA_VERIFIED.pop(uid, None)
            
    if tma_count == 0:
        tma_text += "<i>No active TMA verifications.</i>\n"
        
    # 2. Standard Verifications (24 Hours / Today)
    std_count = 0
    std_text = "\n<b>🔗 Standard Verifications (Daily):</b>\n"
    for uid, expiry in list(VERIFIED.items()):
        std_count += 1
        std_text += f"• <code>{uid}</code> (Valid for: {expiry})\n"
        
    if std_count == 0:
        std_text += "<i>No active standard verifications.</i>\n"
        
    total_text = text + tma_text + std_text
    await message.reply_text(total_text)

@Client.on_message(filters.command("remove_validity") & filters.user(ADMINS) & filters.private)
async def remove_validity_command(client, message):
    from utils import TMA_VERIFIED, VERIFIED
    
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b> `/remove_validity (user_id)`")
        
    try:
        target_uid = int(message.command[1].strip())
    except ValueError:
        return await message.reply_text("<b>Error:</b> Invalid User ID format. Please provide a numeric User ID.")
        
    removed_tma = TMA_VERIFIED.pop(target_uid, None) is not None
    removed_std = VERIFIED.pop(target_uid, None) is not None
    
    if removed_tma or removed_std:
        await message.reply_text(f"<b>✅ Successfully removed validity for User ID:</b> <code>{target_uid}</code>")
    else:
        await message.reply_text(f"<b>❌ User ID <code>{target_uid}</code> does not have any active validity.</b>")

@Client.on_message(filters.command("setting") & filters.private & filters.incoming & filters.user(ADMINS))
async def settings_command(client, message):
    # Force Subscribe Check
    chk_u = await is_subscribed_universal(client, message)
    if chk_u == "kicked" or isinstance(chk_u, list):
        return await start(client, message)
    
    chk = await is_subscribed(client, message)
    if chk == "kicked" or isinstance(chk, list):
        return await start(client, message)

    user_id = message.from_user.id
    user = await get_user(user_id)
    tma_status = "Enabled 🟢" if config.TMA_MODE else "Disabled 🔴"
    stream_status = "Enabled 🟢" if config.STREAM_MODE else "Disabled 🔴"
    buttons = [[
        InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ', callback_data='set_api'),
        InlineKeyboardButton('sᴇᴛ ʙᴀsᴇ sɪᴛᴇ', callback_data='set_site')
    ],[
        InlineKeyboardButton(f"TMA Ads: {'ON 🟢' if config.TMA_MODE else 'OFF 🔴'}", callback_data="toggle_tma"),
        InlineKeyboardButton(f"Stream: {'ON 🟢' if config.STREAM_MODE else 'OFF 🔴'}", callback_data="toggle_stream")
    ],[
        InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴄᴜʀʀᴇɴᴛ ʙᴀsᴇ sɪᴛᴇ: {user['base_site']}\nᴄᴜʀʀᴇɴᴛ ᴀᴘɪ: <code>{user['shortener_api']}</code>\nᴛᴍᴀ ᴀᴅs: <code>{tma_status}</code>\nsᴛʀᴇᴀᴍ ᴍᴏᴅᴇ: <code>{stream_status}</code></b>",
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command('api') & filters.private & filters.user(ADMINS))
async def shortener_api_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = script.SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"])
        return await m.reply(s)

    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(user_id, {"shortener_api": api})
        await m.reply("<b>Shortener API updated successfully to</b> " + api)

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command("base_site") & filters.private & filters.user(ADMINS))
async def base_site_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    text = f"`/base_site (base_site)`\n\n<b>Current base site: None\n\n EX:</b> `/base_site shortnerdomain.com`\n\nIf You Want To Remove Base Site Then Copy This And Send To Bot - `/base_site None`"
    if len(cmd) == 1:
        return await m.reply(text=text, disable_web_page_preview=True)
    elif len(cmd) == 2:
        base_site = cmd[1].strip()
        if base_site == None:
            await update_user_info(user_id, {"base_site": base_site})
            return await m.reply("<b>Base Site updated successfully</b>")
            
        if not domain(base_site):
            return await m.reply(text=text, disable_web_page_preview=True)
        await update_user_info(user_id, {"base_site": base_site})
        await m.reply("<b>Base Site updated successfully</b>")

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command("setforcesub") & filters.private)
async def set_force_sub_handler(client, message):
    """Main bot command for clone bot owners to set force subscribe channels (up to 6).
    Owner adds clone bot as admin to channels, then forwards a message from each channel here.
    """
    user_id = message.from_user.id
    bot_doc = await clone_mongo_db.bots.find_one({"user_id": user_id})
    if not bot_doc:
        return await message.reply_text(
            "<b>❌ You don't have a clone bot yet.\nCreate one first by clicking 🤖 ᴄʟᴏɴᴇ in the main bot.</b>"
        )
    bot_username = bot_doc.get("username", "your bot")
    current = bot_doc.get("force_sub_channels", [])
    await message.reply_text(
        f"<b>📢 Force Subscribe Manager\n\n"
        f"Clone Bot: @{bot_username}\n"
        f"Current channels: {len(current)}/6\n\n"
        f"<u>How to add a channel:</u>\n"
        f"1️⃣ Add @{bot_username} as <b>Admin</b> in your channel\n"
        f"2️⃣ Forward any message from that channel to me here\n\n"
        f"Send up to <b>6 forwarded messages</b> now, one at a time.\n"
        f"Send /done when finished · /clearforcesub to remove all</b>"
    )
    channels = list(current)
    while len(channels) < 6:
        try:
            msg = await client.ask(
                message.chat.id,
                f"<b>Forward a message from channel {len(channels)+1}/6\n"
                f"(or /done to save · /clearforcesub to clear all)</b>",
                timeout=60
            )
        except Exception:
            await message.reply_text("<b>⏰ Timed out. Use /setforcesub to try again.</b>")
            break
        if msg.text and msg.text.strip() == "/done":
            break
        if msg.text and msg.text.strip() == "/clearforcesub":
            channels = []
            break
        if msg.forward_from_chat:
            chat = msg.forward_from_chat
            channel_id = chat.id
            if channel_id in channels:
                await message.reply_text("<b>⚠️ This channel is already added! Forward from a different channel.</b>")
                continue
            # Verify clone bot is admin in this channel
            try:
                member = await client.get_chat_member(channel_id, bot_doc["bot_id"])
                if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    await message.reply_text(
                        f"<b>❌ @{bot_username} is not an admin in <code>{chat.title}</code>.\n"
                        f"Please make it admin first, then forward again.</b>"
                    )
                    continue
            except Exception:
                await message.reply_text(
                    f"<b>⚠️ Could not verify @{bot_username} admin status in <code>{chat.title}</code>.\n"
                    f"Make sure the bot is added as admin, then forward again.</b>"
                )
                continue
            channels.append(channel_id)
            await message.reply_text(
                f"<b>✅ Added [{len(channels)}/6]: {chat.title}\n<code>{channel_id}</code>\n\n"
                f"Forward next channel or send /done</b>"
            )
        else:
            await message.reply_text(
                "<b>⚠️ Please <u>forward a message</u> from a Telegram channel, not type text.\n"
                "If your channel is private, just forward any post from it.</b>"
            )
    # Save channels to DB
    await clone_mongo_db.bots.update_one(
        {"user_id": user_id},
        {"$set": {"force_sub_channels": channels}}
    )
    if channels:
        # Ask user to choose force sub mode
        await message.reply_text(
            f"<b>✅ {len(channels)} channel(s) saved for @{bot_username}!\n\n"
            f"📢 Now choose the <u>Force Subscribe Mode</u>:</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔵 Normal Mode", callback_data=f"fsub_nm_{user_id}")],
                [InlineKeyboardButton("🟢 Join Request Mode", callback_data=f"fsub_jr_{user_id}")]
            ])
        )
    else:
        await message.reply_text("<b>✅ All force subscribe channels cleared for your clone bot.</b>")

@Client.on_message(filters.command("listforcesub") & filters.private)
async def list_force_sub_handler(client, message):
    user_id = message.from_user.id
    bot_doc = await clone_mongo_db.bots.find_one({"user_id": user_id})
    if not bot_doc:
        return await message.reply_text("<b>❌ You don't have a clone bot yet.</b>")
    channels = bot_doc.get("force_sub_channels", [])
    if not channels:
        return await message.reply_text(
            f"<b>📢 No force subscribe channels set for @{bot_doc.get('username','your bot')}.\n"
            f"Use /setforcesub to add channels.</b>"
        )
    text = f"<b>📢 Force Subscribe Channels for @{bot_doc.get('username','your bot')}:\n\n</b>"
    for i, ch_id in enumerate(channels, 1):
        try:
            chat = await client.get_chat(ch_id)
            text += f"{i}. {chat.title} (<code>{ch_id}</code>)\n"
        except:
            text += f"{i}. <code>{ch_id}</code>\n"
    text += f"\n<b>Use /clearforcesub to remove all · /setforcesub to update</b>"
    await message.reply_text(text)

@Client.on_message(filters.command("clearforcesub") & filters.private)
async def clear_force_sub_handler(client, message):
    user_id = message.from_user.id
    bot_doc = await clone_mongo_db.bots.find_one({"user_id": user_id})
    if not bot_doc:
        return await message.reply_text("<b>❌ You don't have a clone bot yet.</b>")
    await clone_mongo_db.bots.update_one({"user_id": user_id}, {"$set": {"force_sub_channels": []}})
    await message.reply_text(f"<b>✅ All force subscribe channels cleared for @{bot_doc.get('username','your bot')}.</b>")

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    from config import ADMINS
    if query.data.startswith("delbot_"):
        if query.from_user.id not in ADMINS:
            return await query.answer("❌ Only the bot owner can delete cloned bots.", show_alert=True)
        try:
            bot_id = int(query.data.split("_")[1])
            cloned_bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
            if cloned_bot:
                from plugins.clone import stop_clone
                bot_username = cloned_bot.get('username')
                await stop_clone(bot_id)
                await clone_mongo_db.bots.delete_one({"bot_id": bot_id})
                try:
                    await clone_mongo_db[str(bot_id)].drop()
                except:
                    pass
                await query.answer(f"✅ @{bot_username} stopped and deleted successfully!", show_alert=True)
                try:
                    await query.message.delete()
                except:
                    pass
            else:
                await query.answer("⚠️ Bot not found.", show_alert=True)
        except Exception as e:
            await query.answer(f"❌ Error: {e}", show_alert=True)
        return

    # Force Sub Mode selection (from /setforcesub)
    if query.data.startswith("fsub_nm_") or query.data.startswith("fsub_jr_"):
        parts = query.data.split("_")
        mode = parts[1]          # "nm" or "jr"
        owner_id = int(parts[2])
        if query.from_user.id != owner_id:
            return await query.answer("❌ This button is not for you!", show_alert=True)
        mode_value = "normal" if mode == "nm" else "joinreq"
        mode_label = "🔵 Normal Mode" if mode == "nm" else "🟢 Join Request Mode"
        await clone_mongo_db.bots.update_one(
            {"user_id": owner_id},
            {"$set": {"force_sub_mode": mode_value}}
        )
        bot_doc = await clone_mongo_db.bots.find_one({"user_id": owner_id})
        bot_username = bot_doc.get("username", "your bot") if bot_doc else "your bot"
        desc = (
            "Users click <b>Join</b> and instantly join the channel."
            if mode_value == "normal" else
            "Users send a <b>join request</b> which the bot <b>auto-approves</b> instantly.\n"
            "Perfect for keeping subscriber counts high."
        )
        await query.message.edit_text(
            f"<b>✅ Force Sub Mode set to: {mode_label}\n\n"
            f"🤖 Clone Bot: @{bot_username}\n\n"
            f"{desc}\n\n"
            f"Use /listforcesub to review channels · /setforcesub to update</b>"
        )
        return await query.answer()
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        me = client.me or await client.get_me()
        me2 = me.mention
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(me2),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
    
    elif query.data == "start":
        me = client.me or await client.get_me()
        portal_url = f"{URL.rstrip('/')}/portal?uid={query.from_user.id}&bot={me.username}"
        buttons = [[
            InlineKeyboardButton('Viral Videos 💦', web_app=WebAppInfo(url=portal_url))
        ],[
            InlineKeyboardButton('⚙️ sᴇᴛᴛɪɴɢs', callback_data='settings'),
            InlineKeyboardButton('🤖 ᴄʟᴏɴᴇ', callback_data='clone_manage')
        ],[
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        me = client.me or await client.get_me()
        me2 = me.mention
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, me2),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
    
    elif query.data == "clone_manage":
        if query.from_user.id not in ADMINS:
            return await query.answer("❌ Only the bot owner can manage/create clone bots.", show_alert=True)
        user_id = query.from_user.id
        bots = [b async for b in clone_mongo_db.bots.find({"user_id": user_id})]
        buttons = []
        for bot in bots:
            buttons.append([InlineKeyboardButton(f"{bot['name']}", callback_data=f"cust_{bot['bot_id']}")])
        
        buttons.append([InlineKeyboardButton("➕ Add Clone", callback_data="add_clone")])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="start")])
        
        manage_text = "<b>✨ <u>Manage Clone's</u>\n\nYou can now manage and create your very own identical clone bot, mirroring all my awesome features, using the given buttons.</b>"
        reply_markup = InlineKeyboardMarkup(buttons)
        
        if query.message.photo:
            try:
                await client.edit_message_media(
                    query.message.chat.id, 
                    query.message.id, 
                    InputMediaPhoto(random.choice(PICS))
                )
                await query.message.edit_text(
                    text=manage_text,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception:
                try:
                    await query.message.delete()
                except: pass
                me = client.me or await client.get_me()
                await client.send_message(
                    chat_id=query.message.chat.id,
                    text=manage_text,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
        else:
            try:
                await query.message.edit_text(
                    text=manage_text,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception:
                try:
                    await query.message.delete()
                except: pass
                await client.send_message(
                    chat_id=query.message.chat.id,
                    text=manage_text,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )

    elif query.data.startswith("cust_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        if not bot:
            return await query.answer("Bot not found!", show_alert=True)
            
        buttons = [
            [InlineKeyboardButton("START MSG", callback_data=f"startmsg_{bot_id}"), InlineKeyboardButton("FORCE SUB", callback_data=f"forcesub_{bot_id}")],
            [InlineKeyboardButton("MODERATORS", callback_data=f"mods_{bot_id}"), InlineKeyboardButton("AUTO DELETE", callback_data=f"autodel_{bot_id}")],
            [InlineKeyboardButton("NO FORWARD", callback_data=f"nofwd_{bot_id}"), InlineKeyboardButton("ACCESS TOKEN", callback_data=f"tokencfg_{bot_id}")],
            [InlineKeyboardButton("MODE", callback_data=f"mode_{bot_id}"), InlineKeyboardButton("DEACTIVATE", callback_data=f"deactivate_{bot_id}")],
            [InlineKeyboardButton("STATS", callback_data=f"stats_{bot_id}"), InlineKeyboardButton("RESTART", callback_data=f"restart_{bot_id}")],
            [InlineKeyboardButton("DELETE", callback_data=f"delete_{bot_id}")],
            [InlineKeyboardButton("BACK", callback_data="clone_manage")]
        ]
        
        text = f"<b>🪄 <u>Customize Clone</u>\n\n➜ Name: <i>{bot['name']}</i>\n\nConfigure Your Clone Settings Using Given Buttons</b>"
        
        if query.message.photo:
            try:
                await query.message.delete()
            except:
                pass
            await client.send_message(
                chat_id=query.message.chat.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )

    elif query.data.startswith("startmsg_"):
        bot_id = int(query.data.split("_")[-1])
        buttons = [
            [InlineKeyboardButton("START TEXT", callback_data=f"stxt_{bot_id}"), InlineKeyboardButton("START PHOTO", callback_data=f"spho_{bot_id}")],
            [InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]
        ]
        await query.message.edit_text(
            text="<b><u>Start Message</u>\n\ncustomize your clone start message using the following buttons</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data.startswith("autodel_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        is_enabled = bot.get("auto_delete_enabled", True)
        status = "Enabled ✅" if is_enabled else "Disabled ❌"
        label = "Disable ❌" if is_enabled else "Enable ✅"
        time = bot.get("auto_delete_time", 5)
        
        buttons = [
            [InlineKeyboardButton("Change time", callback_data=f"cdeltime_{bot_id}"), InlineKeyboardButton("Message", callback_data=f"cdelmsg_{bot_id}"), InlineKeyboardButton(label, callback_data=f"ddel_{bot_id}")],
            [InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]
        ]
        await query.message.edit_text(
            text=f"<b><u>Auto Delete</u>\n\nAutomatically delete all messages sent to clone users after {time} minutes\n\n- Status: {status}</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data.startswith("deactivate_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        is_deact = bot.get("is_deactivated", False)
        label = "Activate" if is_deact else "Deactivate"
        status_text = "<b>Status: Deactivated ❌</b>" if is_deact else "<b>Status: Active ✅</b>"
        
        buttons = [
            [InlineKeyboardButton(label, callback_data=f"do_deact_{bot_id}")],
            [InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]
        ]
        await query.message.edit_text(
            text=f"<b><u>Deactivate Bot</u></b>\n\n{status_text}\n\nDeactivate Your clone bot without deleting your clone bot and saved data's. if you were deactivated your clone bot will no longer work until activating.\n\nNote: if not your clone is used by anyone for longer 8 days then your bot will automatically deactivate",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data.startswith("ddel_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        new_status = not bot.get("auto_delete_enabled", True)
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"auto_delete_enabled": new_status}})
        await query.answer(f"Auto Delete {'Enabled' if new_status else 'Disabled'}")
        # Refresh the menu
        query.data = f"autodel_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("do_deact_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        new_status = not bot.get("is_deactivated", False)
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"is_deactivated": new_status}})
        await query.answer(f"Bot {'Deactivated' if new_status else 'Activated'}")
        # Refresh the menu
        query.data = f"deactivate_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("delete_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        if not bot: return await query.answer("Bot not found!")
        
        # Confirmation
        msg = await client.ask(query.message.chat.id, f"<b>⚠️ Are you sure you want to delete @{bot['username']}?\n\nType <code>YES</code> to confirm or /cancel</b>")
        if msg.text == "YES":
            # Stop the running client first
            from plugins.clone import stop_clone
            await stop_clone(bot_id)
            # Then remove from DB
            await clone_mongo_db.bots.delete_one({"bot_id": bot_id})
            await query.message.edit_text(f"<b>✅ @{bot['username']} has been stopped and deleted.</b>")
            await msg.reply("<b>Bot stopped and deleted successfully. ✅</b>")
        else:
            await msg.reply("<b>Deletion cancelled.</b>")

    elif query.data.startswith("stxt_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Please send the new START TEXT for your clone bot.\n\nUse {mention} for user mention and {mention2} for bot mention.\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"start_text": msg.text.html}})
        await msg.reply("<b>✅ Start Text updated successfully!</b>")
        query.data = f"startmsg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("spho_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Please send the new START PHOTO for your clone bot.\n\n📎 Upload a photo OR send a direct image URL (http/https).\n\n/cancel to skip.</b>")
        if msg.text and msg.text.strip() == "/cancel": return await msg.reply("Cancelled.")
        
        if msg.photo:
            try:
                import aiohttp
                # Download photo bytes from Telegram
                photo_data = await client.download_media(msg.photo.file_id, in_memory=True)
                
                # Retrieve raw bytes from whatever Pyrogram version returns (BytesIO or file path)
                if isinstance(photo_data, str):
                    with open(photo_data, "rb") as f:
                        file_bytes = f.read()
                    try:
                        os.remove(photo_data)
                    except Exception:
                        pass
                elif hasattr(photo_data, "getvalue"):
                    file_bytes = photo_data.getvalue()
                elif hasattr(photo_data, "read"):
                    photo_data.seek(0)
                    file_bytes = photo_data.read()
                else:
                    file_bytes = bytes(photo_data)
                
                # Upload to catbox.moe (highly reliable image hosting)
                import io
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                async with aiohttp.ClientSession(headers=headers) as session:
                    try:
                        form = aiohttp.FormData()
                        form.add_field("reqtype", "fileupload")
                        form.add_field("fileToUpload", io.BytesIO(file_bytes), filename="start.jpg")
                        async with session.post("https://catbox.moe/user/api.php", data=form) as resp:
                            res_text = await resp.text()
                            if res_text and res_text.strip().startswith("http"):
                                photo_url = res_text.strip()
                            else:
                                raise Exception(f"Catbox invalid response: {res_text}")
                    except Exception as catbox_err:
                        logger.error(f"Catbox upload failed: {catbox_err}. Trying fallback...")
                        # Fallback to telegra.ph
                        form_fallback = aiohttp.FormData()
                        form_fallback.add_field("file", io.BytesIO(file_bytes), filename="start.jpg")
                        try:
                            async with session.post("https://telegra.ph/upload", data=form_fallback) as resp:
                                result = await resp.json()
                                if isinstance(result, list) and result[0].get("src"):
                                    photo_url = "https://telegra.ph" + result[0]["src"]
                                else:
                                    raise Exception("Telegra.ph upload failed")
                        except Exception as tg_err:
                            logger.error(f"Telegra.ph upload failed: {tg_err}. Trying graph.org...")
                            # Fallback to graph.org
                            try:
                                async with session.post("https://graph.org/upload", data=form_fallback) as resp2:
                                    result2 = await resp2.json()
                                    if isinstance(result2, list) and result2[0].get("src"):
                                        photo_url = "https://graph.org" + result2[0]["src"]
                                    else:
                                        raise Exception("Graph.org upload failed")
                            except Exception as graph_err:
                                logger.error(f"Graph.org upload failed: {graph_err}. Trying tmpfiles.org...")
                                # Fallback to tmpfiles.org
                                try:
                                    form_tmp = aiohttp.FormData()
                                    form_tmp.add_field("file", io.BytesIO(file_bytes), filename="start.jpg")
                                    async with session.post("https://tmpfiles.org/api/v1/upload", data=form_tmp) as resp3:
                                        res3 = await resp3.json()
                                        if res3.get("status") == "success" and "data" in res3 and "url" in res3["data"]:
                                            raw_url = res3["data"]["url"]
                                            photo_url = raw_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
                                        else:
                                            raise Exception(f"tmpfiles.org invalid response: {res3}")
                                except Exception as tmp_err:
                                    raise Exception(f"All providers failed. Catbox: {catbox_err} | Telegraph: {tg_err} | Graph: {graph_err} | Tmpfiles: {tmp_err}")
                
                await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"start_photo": photo_url}})
                await msg.reply(f"<b>✅ Start Photo updated successfully!\n\nURL: <code>{photo_url}</code></b>")
            except Exception as e:
                logger.error(f"Media upload error: {e}")
                await msg.reply(f"<b>❌ Upload failed: {e}\n\nPlease send a direct image URL instead.</b>")
        elif msg.text and msg.text.strip().startswith("http"):
            await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"start_photo": msg.text.strip()}})
            await msg.reply("<b>✅ Start Photo URL updated successfully!</b>")
        else:
            return await msg.reply("<b>❌ Invalid input. Please upload a photo or send an http/https URL.</b>")
            
        query.data = f"startmsg_{bot_id}"
        try:
            return await cb_handler(client, query)
        except Exception:
            pass

    elif query.data.startswith("cdeltime_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Please send the new Auto-Delete time in minutes (integer).\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        try:
            time = int(msg.text.strip())
            await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"auto_delete_time": time}})
            await msg.reply(f"<b>✅ Auto-Delete time set to {time} minutes!</b>")
        except:
            await msg.reply("<b>❌ Invalid input. Please send a number.</b>")
        query.data = f"autodel_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("forcesub_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        channels = bot.get("force_sub_channels", [])
        mode = bot.get("force_sub_mode", "normal")
        channel_names = bot.get("channel_names") or {}
        
        text = (
            "<b><u>Force Sub</u></b>\n\n"
            "<i>Users can only use your clone bot after joining all force sub channels. "
            "Clone bots now also support join request mode.</i>\n\n"
            "You can add up to 6 channels.\n\n"
            f"<b>Current Mode:</b> <code>{mode.upper()}</code>"
        )
        
        buttons = []
        # Add each channel as a row with a deletion button
        for c in channels:
            title = channel_names.get(str(c), str(c))
            buttons.append([
                InlineKeyboardButton(f"• {title}", callback_data=f"info_fsub_{bot_id}_{c}"),
                InlineKeyboardButton("❌", callback_data=f"rem_fsub_{bot_id}_{c}")
            ])
            
        buttons.append([
            InlineKeyboardButton("➕ Add Channel", callback_data=f"add_fsub_{bot_id}"),
            InlineKeyboardButton("🧹 Clear All", callback_data=f"clear_fsub_{bot_id}")
        ])
        buttons.append([
            InlineKeyboardButton(f"Switch to {'JOIN REQ' if mode=='normal' else 'NORMAL'} Mode", callback_data=f"mode_fsub_{bot_id}")
        ])
        buttons.append([
            InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")
        ])
        
        await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

    elif query.data.startswith("rem_fsub_"):
        parts = query.data.split("_")
        bot_id = int(parts[2])
        channel_id = int(parts[3])
        
        await clone_mongo_db.bots.update_one(
            {"bot_id": bot_id},
            {
                "$pull": {"force_sub_channels": channel_id},
                "$unset": {f"channel_names.{channel_id}": ""}
            }
        )
        await query.answer("✅ Channel removed successfully!", show_alert=True)
        query.data = f"forcesub_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("info_fsub_"):
        parts = query.data.split("_")
        channel_id = parts[3]
        await query.answer(f"Channel ID: {channel_id}", show_alert=True)
        return

    elif query.data.startswith("add_fsub_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        if len(bot.get("force_sub_channels", [])) >= 6:
            return await query.answer("Max 6 channels allowed!", show_alert=True)
            
        sent_msg = await client.send_message(
            query.message.chat.id, 
            "<b>Please forward a message from the channel you want to add as Force Sub.\n\nMake sure your clone bot is ADMIN in that channel!</b>"
        )
        msg = await client.listen(query.message.chat.id)
        
        if msg.forward_from_chat:
            f_chat_id = msg.forward_from_chat.id
            f_chat_title = msg.forward_from_chat.title
            
            if not f_chat_title:
                try:
                    chat = await client.get_chat(f_chat_id)
                    f_chat_title = chat.title
                except:
                    pass
            
            f_chat_title = f_chat_title or str(f_chat_id)
            
            await clone_mongo_db.bots.update_one(
                {"bot_id": bot_id}, 
                {
                    "$push": {"force_sub_channels": f_chat_id},
                    "$set": {f"channel_names.{f_chat_id}": f_chat_title}
                }
            )
            await query.answer(f"✅ Channel '{f_chat_title}' added successfully!", show_alert=True)
        else:
            await query.answer("❌ Please forward a message from a channel.", show_alert=True)
            
        try:
            await client.delete_messages(query.message.chat.id, [sent_msg.id, msg.id])
        except Exception as e:
            logger.error(f"Error deleting force sub messages: {e}")
            
        query.data = f"forcesub_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("clear_fsub_"):
        bot_id = int(query.data.split("_")[-1])
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"force_sub_channels": []}})
        await query.answer("All channels cleared!")
        query.data = f"forcesub_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("mode_fsub_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        new_mode = "joinreq" if bot.get("force_sub_mode", "normal") == "normal" else "normal"
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"force_sub_mode": new_mode}})
        await query.answer(f"Mode switched to {new_mode.upper()}")
        query.data = f"forcesub_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("mods_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        mods = bot.get("moderators", [])
        mods_text = "\n".join([f"• <code>{m}</code>" for m in mods]) if mods else "<i>No moderators added.</i>"
        buttons = [
            [InlineKeyboardButton("➕ Add Moderator", callback_data=f"add_mod_{bot_id}"),
             InlineKeyboardButton("🧹 Clear All", callback_data=f"clear_mod_{bot_id}")],
            [InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]
        ]
        await query.message.edit_text(
            text=f"<b><u>Moderators</u></b>\n\nModerators can use admin commands in your clone bot.\n\n<b>Current Moderators:</b>\n{mods_text}",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data.startswith("add_mod_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Send the User ID of the moderator to add.\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        try:
            mod_id = int(msg.text.strip())
            await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$addToSet": {"moderators": mod_id}})
            await msg.reply(f"<b>✅ User <code>{mod_id}</code> added as moderator!</b>")
        except:
            await msg.reply("<b>❌ Invalid User ID. Please send a number.</b>")
        query.data = f"mods_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("clear_mod_"):
        bot_id = int(query.data.split("_")[-1])
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"moderators": []}})
        await query.answer("All moderators cleared!")
        query.data = f"mods_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("nofwd_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        is_nofwd = bot.get("no_forward", False)
        new_status = not is_nofwd
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"no_forward": new_status}})
        status_txt = "✅ Enabled" if new_status else "❌ Disabled"
        await query.answer(f"No Forward {status_txt}", show_alert=True)
        buttons = [
            [InlineKeyboardButton(f"{'Disable ❌' if new_status else 'Enable ✅'} No Forward", callback_data=f"nofwd_{bot_id}")],
            [InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]
        ]
        await query.message.edit_text(
            text=f"<b><u>No Forward</u></b>\n\nWhen enabled, files sent by the bot cannot be forwarded by users.\n\n<b>Status: {status_txt}</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data.startswith("tokencfg_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        
        vplink_verified = bot.get("vplink_verified", False)
        if not vplink_verified:
            req = await clone_mongo_db.vplink_requests.find_one({"bot_id": bot_id, "status": "pending"})
            if req:
                text = "<b>waiting msg please wait for confirmation</b>"
                buttons = [[InlineKeyboardButton("🔙 Back", callback_data=f"cust_{bot_id}")]]
                if query.message.photo:
                    try:
                        await query.message.delete()
                    except:
                        pass
                    await client.send_message(
                        chat_id=query.message.chat.id,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    await query.message.edit_text(
                        text=text,
                        reply_markup=InlineKeyboardMarkup(buttons),
                        parse_mode=enums.ParseMode.HTML
                    )
                return
            else:
                caption = (
                    "<b>⚠️ You need to register under our referral link first!</b>\n\n"
                    "1️⃣ Click this link to register: https://vplink.in/ref/Priyanshu7890\n"
                    "2️⃣ Create an account on VPLink.\n"
                    "3️⃣ Go to Tools -> Developers API (as shown in the image below) to get your API token.\n"
                    "4️⃣ Once done, click <b>📤 Submit Request</b> below.\n\n"
                    "<i>Our admin will manually verify and approve your request. Once verified, you can set your API key.</i>"
                )
                buttons = [
                    [InlineKeyboardButton("🔗 Register on VPLink", url="https://vplink.in/ref/Priyanshu7890")],
                    [InlineKeyboardButton("📤 Submit Request", callback_data=f"req_vplink_{bot_id}")],
                    [InlineKeyboardButton("🔙 Back", callback_data=f"cust_{bot_id}")]
                ]
                try:
                    await query.message.delete()
                except:
                    pass
                await client.send_photo(
                    chat_id=query.message.chat.id,
                    photo="vplink_tutorial.png",
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
                
        tma_mode = bot.get("tma_mode", False)
        status_txt = "ON 🟢" if tma_mode else "OFF 🔴"
        tma_btn = "Disable ❌ TMA Ads" if tma_mode else "Enable ✅ TMA Ads"
        
        api_key = bot.get("shortener_api") or "Not set"
        validity = bot.get("token_timeout", 10800) // 3600
        tutorial = bot.get("token_tutorial", "None")
        api_display = f"<code>{api_key}</code>" if api_key != "Not set" else "<i>⚠️ Not set — tap Set API Key!</i>"
        
        buttons = [
            [InlineKeyboardButton("🔑 Set API Key", callback_data=f"tok_api_{bot_id}")],
            [InlineKeyboardButton("⏱ Validity", callback_data=f"tok_val_{bot_id}"), InlineKeyboardButton("📖 Tutorial", callback_data=f"tok_tut_{bot_id}")],
            [InlineKeyboardButton(tma_btn, callback_data=f"tok_tma_{bot_id}"), InlineKeyboardButton("🧹 Clear All Settings", callback_data=f"tok_clr_{bot_id}")],
            [InlineKeyboardButton("🔙 Back", callback_data=f"cust_{bot_id}")]
        ]
        
        text = (
            f"<b><u>⚙️ TMA Ads Setting</u></b>\n\n"
            f"  - Status: {status_txt}\n"
            f"  - Domain: <code>vplink.in</code>\n"
            f"  - API Key: {api_display}\n"
            f"  - Tutorial: {tutorial}\n"
            f"  - Validity: <code>{validity} hours</code>"
        )
        
        if query.message.photo:
            try:
                await query.message.delete()
            except:
                pass
            await client.send_message(
                chat_id=query.message.chat.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
        else:
            await query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )

    elif query.data.startswith("tok_val_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Send the token validity time in HOURS (e.g. 24).\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        try:
            val = int(msg.text.strip())
            await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"token_timeout": val * 3600}})
            await msg.reply(f"<b>✅ Token Validity set to {val} hours!</b>")
        except:
            await msg.reply("<b>❌ Invalid time. Must be a number.</b>")
        query.data = f"tokencfg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("tok_api_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        current_api = bot.get("shortener_api") or "Not set"
        msg = await client.ask(
            query.message.chat.id,
            f"<b>🔑 Set VPLink API Key</b>\n\n"
            f"Current API Key: <code>{current_api}</code>\n\n"
            f"Please send your <b>VPLink API Key</b> from:\n"
            f"<code>vplink.in → Tools → Developer API</code>\n\n"
            f"Send /cancel to skip."
        )
        if msg.text and msg.text.strip() == "/cancel": return await msg.reply("Cancelled.")
        try:
            api_key = msg.text.strip()
            await clone_mongo_db.bots.update_one(
                {"bot_id": bot_id},
                {"$set": {"shortener_site": "vplink.in", "shortener_api": api_key}}
            )
            await msg.reply(f"<b>✅ API Key set successfully!\n\nYour TMA Ads verification is now ready to use.</b>")
        except Exception as e:
            await msg.reply(f"<b>❌ Error: {e}</b>")
        query.data = f"tokencfg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("tok_tut_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Send the Tutorial Link URL for how to bypass your shortener.\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"token_tutorial": msg.text.strip()}})
        await msg.reply(f"<b>✅ Tutorial link updated!</b>")
        query.data = f"tokencfg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("tok_tma_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        tma_mode = bot.get("tma_mode", False)
        new_tma = not tma_mode
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"tma_mode": new_tma}})
        await query.answer(f"TMA Ads {'Enabled 🟢' if new_tma else 'Disabled 🔴'}", show_alert=True)
        query.data = f"tokencfg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("tok_clr_"):
        bot_id = int(query.data.split("_")[-1])
        await clone_mongo_db.bots.update_one(
            {"bot_id": bot_id},
            {"$set": {
                "shortener_site": "None",
                "shortener_api": "None",
                "token_tutorial": "None",
                "token_timeout": 86400,
                "token_verify": False,
                "tma_mode": False
            }}
        )
        await query.answer("All Token + TMA settings cleared and disabled!", show_alert=True)
        query.data = f"tokencfg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("mode_") and not query.data.startswith("mode_fsub_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        current_mode = bot.get("bot_mode", "public")
        buttons = [
            [InlineKeyboardButton("🌐 Public Mode", callback_data=f"setmode_public_{bot_id}"),
             InlineKeyboardButton("🔒 Private Mode", callback_data=f"setmode_private_{bot_id}")],
            [InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]
        ]
        await query.message.edit_text(
            text=f"<b><u>Bot Mode</u></b>\n\n🌐 <b>Public</b>: Anyone can use the bot.\n🔒 <b>Private</b>: Only moderators and owner can generate links.\n\n<b>Current Mode: {current_mode.upper()}</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data.startswith("setmode_"):
        parts = query.data.split("_")
        mode = parts[1]
        bot_id = int(parts[2])
        await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"bot_mode": mode}})
        await query.answer(f"Mode set to {mode.upper()}!", show_alert=True)
        query.data = f"mode_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("stats_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        from clone_plugins.dbusers import clonedb
        total_users = await clonedb.total_users_count(bot_id) if bot else 0
        status = "🔴 Deactivated" if bot.get("is_deactivated") else "🟢 Active"
        name = bot.get("name", "Unknown")
        username = bot.get("username", "Unknown")
        buttons = [[InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]]
        await query.message.edit_text(
            text=f"<b><u>Bot Statistics</u></b>\n\n🤖 <b>Name:</b> {name}\n👤 <b>Username:</b> @{username}\n👥 <b>Total Users:</b> <code>{total_users}</code>\n📊 <b>Status:</b> {status}",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data.startswith("restart_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        if not bot:
            return await query.answer("Bot not found!", show_alert=True)
        await query.answer("⏳ Restarting bot...", show_alert=True)
        try:
            from plugins.clone import stop_clone, running_clones, set_clone_commands
            from pyrogram import Client as PyroClient
            
            # ✅ Stop the existing instance first to avoid duplicate handlers
            await stop_clone(bot_id)
            
            # Start a fresh instance
            bot_token = bot["token"]
            vj = PyroClient(
                f"clone_{bot_token[:10]}",
                API_ID, API_HASH,
                bot_token=bot_token,
                plugins={"root": "clone_plugins"},
                in_memory=True
            )
            await vj.start()
            # Set bot commands so they appear in Telegram menu
            await set_clone_commands(vj)
            
            # ✅ Register the new client so future restarts/stops work correctly
            running_clones[bot_id] = vj
            
            success_text = f"✅ @{bot['username']} restarted successfully!"
        except Exception as e:
            success_text = f"❌ Restart failed: {str(e)[:100]}"
        
        buttons = [[InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]]
        await query.message.edit_text(
            text=f"<b>{success_text}\n\nThe bot has been fully stopped and started fresh. All handlers are now running clean.</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "add_clone":
        # Simply trigger the /clone command logic
        from plugins.clone import clone
        # We need a fake message object or just call the logic
        await query.message.delete()
        # Create a mock message to satisfy clone function
        class MockMessage:
            def __init__(self, from_user, chat):
                self.from_user = from_user
                self.chat = chat
            async def reply_text(self, *args, **kwargs):
                return await client.send_message(self.chat.id, *args, **kwargs)
            async def reply(self, *args, **kwargs):
                return await client.send_message(self.chat.id, *args, **kwargs)
        
        await clone(client, MockMessage(query.from_user, query.message.chat))

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
    
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('🔒 Cʟᴏsᴇ', callback_data='close_data')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )  
        
# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

    elif query.data == "toggle_tma":
        from config import ADMINS
        if query.from_user.id not in ADMINS:
            return await query.answer("❌ Only the bot owner can configure TMA settings!", show_alert=True)
        config.TMA_MODE = not config.TMA_MODE
        await clone_mongo_db.settings.update_one(
            {"_id": "main_settings"},
            {"$set": {"tma_mode": config.TMA_MODE}},
            upsert=True
        )
        await query.answer(f"TMA Ads {'Enabled 🟢' if config.TMA_MODE else 'Disabled 🔴'}", show_alert=True)
        query.data = "settings"
        return await cb_handler(client, query)

    elif query.data == "toggle_stream":
        from config import ADMINS
        if query.from_user.id not in ADMINS:
            return await query.answer("❌ Only the bot owner can configure Stream settings!", show_alert=True)
        config.STREAM_MODE = not config.STREAM_MODE
        await clone_mongo_db.settings.update_one(
            {"_id": "main_settings"},
            {"$set": {"stream_mode": config.STREAM_MODE}},
            upsert=True
        )
        await query.answer(f"Stream Mode {'Enabled 🟢' if config.STREAM_MODE else 'Disabled 🔴'}", show_alert=True)
        query.data = "settings"
        return await cb_handler(client, query)

    elif query.data == "settings":
        from config import ADMINS
        user_id = query.from_user.id
        user = await get_user(user_id)
        tma_status = "Enabled 🟢" if config.TMA_MODE else "Disabled 🔴"
        stream_status = "Enabled 🟢" if config.STREAM_MODE else "Disabled 🔴"
        
        # Base settings buttons for every user
        buttons = [[
            InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ', callback_data='set_api'),
            InlineKeyboardButton('sᴇᴛ ʙᴀsᴇ sɪᴛᴇ', callback_data='set_site')
        ],[
            InlineKeyboardButton('💬 ᴄʜᴀᴛʙᴏx', url='https://t.me/+cFO-dJGWlCMzNGRl'),
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
        ]]
        
        # Only render and allow the global TMA/Stream toggle buttons for bot owners/admins
        if user_id in ADMINS:
            buttons.append([
                InlineKeyboardButton(f"TMA Ads: {'ON 🟢' if config.TMA_MODE else 'OFF 🔴'}", callback_data="toggle_tma"),
                InlineKeyboardButton(f"Stream: {'ON 🟢' if config.STREAM_MODE else 'OFF 🔴'}", callback_data="toggle_stream")
            ])
            buttons.append([
                InlineKeyboardButton("💳 Configure Plan", callback_data="setplan")
            ])
            
        buttons.extend([[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
        ]])
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴄᴜʀʀᴇɴᴛ ʙᴀsᴇ sɪᴛᴇ: {user['base_site']}\nᴄᴜʀʀᴇɴᴛ ᴀᴘɪ: <code>{user['shortener_api']}</code>\nᴛᴍᴀ ᴀᴅs: <code>{tma_status}</code>\nsᴛʀᴇᴀᴍ ᴍᴏᴅᴇ: <code>{stream_status}</code></b>",
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

    elif query.data.startswith("req_vplink_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        if not bot:
            return await query.answer("Bot not found!", show_alert=True)
            
        user_id = query.from_user.id
        import time
        from datetime import datetime
        
        await clone_mongo_db.vplink_requests.update_one(
            {"bot_id": bot_id},
            {"$set": {
                "user_id": user_id,
                "username": bot.get("username", ""),
                "bot_name": bot.get("name", ""),
                "user_mention": query.from_user.mention,
                "status": "pending",
                "requested_at": time.time()
            }},
            upsert=True
        )
        
        text = "<b>waiting msg please wait for confirmation</b>"
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data=f"cust_{bot_id}")]]
        if query.message.photo:
            try:
                await query.message.delete()
            except:
                pass
            await client.send_message(
                chat_id=query.message.chat.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
            
        from config import ADMINS
        for admin in ADMINS:
            try:
                notify_buttons = [
                    [
                        InlineKeyboardButton("✅ Approve", callback_data=f"adm_appr_{bot_id}"),
                        InlineKeyboardButton("❌ Decline", callback_data=f"adm_decl_{bot_id}")
                    ]
                ]
                await client.send_message(
                    chat_id=admin,
                    text=f"<b>🔔 New TMA Verification Request!</b>\n\n"
                         f"👤 <b>User:</b> {query.from_user.mention} (ID: <code>{user_id}</code>)\n"
                         f"🤖 <b>Clone Bot:</b> @{bot.get('username')} (ID: <code>{bot_id}</code>)\n"
                         f"📅 <b>Requested At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    reply_markup=InlineKeyboardMarkup(notify_buttons)
                )
            except Exception as e:
                logger.error(f"Failed to send admin notification to {admin}: {e}")
                
        await query.answer("Verification request submitted successfully!", show_alert=True)

    elif query.data.startswith("adm_appr_") or query.data.startswith("adm_decl_"):
        from config import ADMINS
        if query.from_user.id not in ADMINS:
            return await query.answer("❌ You are not an admin!", show_alert=True)
            
        action = "approved" if "appr" in query.data else "declined"
        bot_id = int(query.data.split("_")[-1])
        import time
        
        req = await clone_mongo_db.vplink_requests.find_one({"bot_id": bot_id, "status": "pending"})
        if not req:
            return await query.answer("Request not found or already processed!", show_alert=True)
            
        await clone_mongo_db.vplink_requests.update_one(
            {"bot_id": bot_id},
            {"$set": {"status": action, "processed_at": time.time()}}
        )
        
        # Use clone bot client to send notification so user sees it in their clone bot chat
        from plugins.clone import running_clones
        clone_client = running_clones.get(bot_id, client)
        
        if action == "approved":
            await clone_mongo_db.bots.update_one(
                {"bot_id": bot_id},
                {"$set": {"vplink_verified": True}}
            )
            try:
                await clone_client.send_message(
                    chat_id=req["user_id"],
                    text="<b>✅ You're verified! You can now enable TMA Ads and set your API key.\n\nUse /setting in your clone bot to configure it.</b>"
                )
            except Exception as e:
                logger.error(f"Failed to send approval message via clone bot: {e}")
                try:
                    await client.send_message(
                        chat_id=req["user_id"],
                        text=f"<b>✅ Your clone bot @{req.get('username', '')} has been verified!\nYou can now enable TMA Ads and set your API key in the clone bot settings.</b>"
                    )
                except Exception as e2:
                    logger.error(f"Failed to send approval message via main bot too: {e2}")
            await query.answer("Request Approved! User notified.", show_alert=True)
        else:
            try:
                await clone_client.send_message(
                    chat_id=req["user_id"],
                    text="<b>❌ Your VPLink verification request was declined. Please ensure you registered using our referral link: https://vplink.in/ref/Priyanshu7890</b>"
                )
            except Exception as e:
                logger.error(f"Failed to send declination message via clone bot: {e}")
                try:
                    await client.send_message(
                        chat_id=req["user_id"],
                        text="<b>❌ Your VPLink verification request was declined. Please ensure you registered using our referral link.</b>"
                    )
                except Exception as e2:
                    logger.error(f"Failed to send declination message via main bot too: {e2}")
            await query.answer("Request Declined! User notified.", show_alert=True)
            
        try:
            await query.message.edit_text(
                text=query.message.text.html + f"\n\n<b>Status: {action.upper()} by {query.from_user.mention}</b>",
                reply_markup=None
            )
        except Exception as e:
            logger.error(f"Failed to edit admin notification: {e}")

    elif query.data.startswith("page_appr_") or query.data.startswith("page_decl_"):
        from config import ADMINS
        if query.from_user.id not in ADMINS:
            return await query.answer("❌ You are not an admin!", show_alert=True)
            
        parts = query.data.split("_")
        action = "approved" if parts[1] == "appr" else "declined"
        bot_id = int(parts[2])
        page = int(parts[3])
        import time
        
        req = await clone_mongo_db.vplink_requests.find_one({"bot_id": bot_id, "status": "pending"})
        if not req:
            await query.answer("Request not found or already processed!", show_alert=True)
            await send_requests_page(client, query.message.chat.id, page, query.message.id)
            return
            
        await clone_mongo_db.vplink_requests.update_one(
            {"bot_id": bot_id},
            {"$set": {"status": action, "processed_at": time.time()}}
        )
        
        # Use clone bot client to send notification so user sees it in their clone bot chat
        from plugins.clone import running_clones
        clone_client = running_clones.get(bot_id, client)
        
        if action == "approved":
            await clone_mongo_db.bots.update_one(
                {"bot_id": bot_id},
                {"$set": {"vplink_verified": True}}
            )
            try:
                await clone_client.send_message(
                    chat_id=req["user_id"],
                    text="<b>✅ You're verified! You can now enable TMA Ads and set your API key.\n\nUse /setting in your clone bot to configure it.</b>"
                )
            except Exception as e:
                logger.error(f"Failed to send approval message via clone bot: {e}")
                try:
                    await client.send_message(
                        chat_id=req["user_id"],
                        text=f"<b>✅ Your clone bot @{req.get('username', '')} has been verified!\nYou can now enable TMA Ads and set your API key in the clone bot settings.</b>"
                    )
                except Exception as e2:
                    logger.error(f"Failed to send approval message via main bot too: {e2}")
            await query.answer("Request Approved! User notified.", show_alert=True)
        else:
            try:
                await clone_client.send_message(
                    chat_id=req["user_id"],
                    text="<b>❌ Your VPLink verification request was declined. Please ensure you registered using our referral link: https://vplink.in/ref/Priyanshu7890</b>"
                )
            except Exception as e:
                logger.error(f"Failed to send declination message via clone bot: {e}")
                try:
                    await client.send_message(
                        chat_id=req["user_id"],
                        text="<b>❌ Your VPLink verification request was declined. Please ensure you registered using our referral link.</b>"
                    )
                except Exception as e2:
                    logger.error(f"Failed to send declination message via main bot too: {e2}")
            await query.answer("Request Declined! User notified.", show_alert=True)
            
        await send_requests_page(client, query.message.chat.id, page, query.message.id)

    elif query.data.startswith("reqpage_"):
        page = int(query.data.split("_")[-1])
        await send_requests_page(client, query.message.chat.id, page, query.message.id)
        await query.answer()

    elif query.data == "setplan":
        from config import ADMINS
        if query.from_user.id not in ADMINS:
            return await query.answer("❌ Only admins can configure plans!", show_alert=True)
            
        msg = await client.ask(
            chat_id=query.message.chat.id,
            text="<b>📸 Please send/upload your payment QR code photo (or send /cancel to exit).</b>"
        )
        if msg.text and msg.text.strip() == "/cancel":
            return await msg.reply("<b>Cancelled plan configuration.</b>")
            
        if not msg.photo:
            return await msg.reply("<b>❌ Please send a photo of the QR code. Try again from Settings.</b>")
            
        qr_file_id = msg.photo.file_id
        
        msg_text = await client.ask(
            chat_id=query.message.chat.id,
            text="<b>✍️ Now please send the UPI plans text with prices (or send /cancel to skip).\n\nExample:\n<code>1 Month - 199\n3 Months - 399\nLifetime - 799</code></b>"
        )
        if msg_text.text and msg_text.text.strip() == "/cancel":
            return await msg_text.reply("<b>Cancelled plan configuration.</b>")
            
        plans_text = msg_text.text.html if msg_text.text else "Plans not configured"
        
        # Parse prices to verify format and display confirmation
        stars_1m, stars_3m, stars_lifetime = parse_stars_prices(plans_text)
        s_1m = stars_1m if stars_1m is not None else 50
        s_3m = stars_3m if stars_3m is not None else 120
        s_lifetime = stars_lifetime if stars_lifetime is not None else 300
        
        me = client.me or await client.get_me()
        await clone_mongo_db.plans_config.update_one(
            {"_id": me.id},
            {"$set": {
                "payment_qr": qr_file_id,
                "plans_text": plans_text,
                "stars_1m": s_1m,
                "stars_3m": s_3m,
                "stars_lifetime": s_lifetime
            }},
            upsert=True
        )
        
        await msg_text.reply(
            f"<b>✅ Payment Plan configured successfully!\n\n"
            f"⭐ Telegram Stars Prices (auto-extracted from plan text):\n"
            f"• 1 Month — {s_1m} Stars\n"
            f"• 3 Months — {s_3m} Stars\n"
            f"• Lifetime — {s_lifetime} Stars</b>"
        )
        query.data = "settings"
        return await cb_handler(client, query)

    elif query.data == "buy_plan":
        me = client.me or await client.get_me()
        plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
        if not plan_cfg:
            return await query.answer("Plans not configured!", show_alert=True)
            
        await clone_mongo_db.user_states.delete_one({"bot_id": me.id, "user_id": query.from_user.id})
        
        btn = [
            [InlineKeyboardButton("💳 UPI Payment", callback_data="buy_upi")],
            [InlineKeyboardButton("⭐ Telegram Stars", callback_data="buy_stars")],
            [InlineKeyboardButton("« Back", callback_data="plan_status_back")]
        ]
        
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
        me = client.me or await client.get_me()
        plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
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
        
        await clone_mongo_db.user_states.update_one(
            {"bot_id": me.id, "user_id": query.from_user.id},
            {"$set": {"state": "waiting_screenshot"}},
            upsert=True
        )
        
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=qr_file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="buy_plan")]])
        )
        await query.message.delete()
        await query.answer()

    elif query.data == "buy_stars":
        me = client.me or await client.get_me()
        await clone_mongo_db.user_states.delete_one({"bot_id": me.id, "user_id": query.from_user.id})
        
        plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
        parsed_1m, parsed_3m, parsed_lifetime = parse_stars_prices(plan_cfg.get("plans_text", "") if plan_cfg else "")
        
        stars_1m = parsed_1m if parsed_1m is not None else (plan_cfg.get("stars_1m", 50) if plan_cfg else 50)
        stars_3m = parsed_3m if parsed_3m is not None else (plan_cfg.get("stars_3m", 120) if plan_cfg else 120)
        stars_lifetime = parsed_lifetime if parsed_lifetime is not None else (plan_cfg.get("stars_lifetime", 300) if plan_cfg else 300)
        
        text = (
            "<b>⭐ <u>Telegram Stars Payment</u>\n\n"
            "Select the VIP plan you want to purchase using Telegram Stars:</b>\n\n"
            f"• <b>1 Month</b> — <code>{stars_1m} Stars</code>\n"
            f"• <b>3 Months</b> — <code>{stars_3m} Stars</code>\n"
            f"• <b>Lifetime</b> — <code>{stars_lifetime} Stars</code>"
        )
        btn = [
            [InlineKeyboardButton(f"⭐ 1 Month ({stars_1m} Stars)", callback_data="pay_stars_30")],
            [InlineKeyboardButton(f"⭐ 3 Months ({stars_3m} Stars)", callback_data="pay_stars_90")],
            [InlineKeyboardButton(f"⭐ Lifetime ({stars_lifetime} Stars)", callback_data="pay_stars_0")],
            [InlineKeyboardButton("« Back", callback_data="buy_plan")]
        ]
        
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
        me = client.me or await client.get_me()
        days = int(query.data.split("_")[-1])
        plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
        parsed_1m, parsed_3m, parsed_lifetime = parse_stars_prices(plan_cfg.get("plans_text", "") if plan_cfg else "")
        
        stars_1m = parsed_1m if parsed_1m is not None else (plan_cfg.get("stars_1m", 50) if plan_cfg else 50)
        stars_3m = parsed_3m if parsed_3m is not None else (plan_cfg.get("stars_3m", 120) if plan_cfg else 120)
        stars_lifetime = parsed_lifetime if parsed_lifetime is not None else (plan_cfg.get("stars_lifetime", 300) if plan_cfg else 300)
        
        if days == 30:
            title = "1 Month VIP Access"
            amount = stars_1m
        elif days == 90:
            title = "3 Months VIP Access"
            amount = stars_3m
        else:
            title = "Lifetime VIP Access"
            amount = stars_lifetime
            
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
            
        me = client.me or await client.get_me()
        user_vip = await is_vip(me.id, query.from_user.id)
        if user_vip:
            from datetime import datetime
            vip_user = await clone_mongo_db.vip_users.find_one({"bot_id": me.id, "user_id": query.from_user.id})
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

async def send_requests_page(client, chat_id, page, message_id=None):
    limit = 5
    skip = (page - 1) * limit
    
    total = await clone_mongo_db.vplink_requests.count_documents({"status": "pending"})
    requests_list = []
    async for r in clone_mongo_db.vplink_requests.find({"status": "pending"}).sort("requested_at", 1).skip(skip).limit(limit):
        requests_list.append(r)
        
    if not requests_list:
        text = "<b>📭 No pending VPLink verification requests found.</b>"
        if message_id:
            await client.edit_message_text(chat_id, message_id, text)
        else:
            await client.send_message(chat_id, text)
        return

    text = f"<b>📋 Pending VPLink Requests (Page {page}/{(total + limit - 1) // limit}):</b>\n\n"
    buttons = []
    
    for idx, r in enumerate(requests_list, 1):
        text += f"{idx}. 👤 {r['user_mention']} (ID: <code>{r['user_id']}</code>)\n" \
                f"   🤖 Bot: @{r['username']} (ID: <code>{r['bot_id']}</code>)\n\n"
                
        buttons.append([
            InlineKeyboardButton(f"✅ Approve {idx}", callback_data=f"page_appr_{r['bot_id']}_{page}"),
            InlineKeyboardButton(f"❌ Decline {idx}", callback_data=f"page_decl_{r['bot_id']}_{page}")
        ])
        
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⏮ Previous", callback_data=f"reqpage_{page - 1}"))
    if skip + limit < total:
        nav_row.append(InlineKeyboardButton("Next ⏭", callback_data=f"reqpage_{page + 1}"))
        
    if nav_row:
        buttons.append(nav_row)
        
    if message_id:
        await client.edit_message_text(chat_id, message_id, text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await client.send_message(chat_id, text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command(["requests", "tma_requests"]) & filters.private & filters.user(ADMINS))
async def list_requests_handler(client, message):
    page = 1
    if len(message.command) > 1:
        try:
            page = int(message.command[1])
        except ValueError:
            pass
            
    await send_requests_page(client, message.chat.id, page)

@Client.on_message(filters.command("plan") & filters.private)
async def plan_command_handler(client, message):
    me = client.me or await client.get_me()
    plan_cfg = await clone_mongo_db.plans_config.find_one({"_id": me.id})
    if not plan_cfg:
        return await message.reply_text("<b>⚠️ This bot does not have a plan configured yet. Please check back later!</b>")
        
    user_vip = await is_vip(me.id, message.from_user.id)
    if user_vip:
        from datetime import datetime
        vip_user = await clone_mongo_db.vip_users.find_one({"bot_id": me.id, "user_id": message.from_user.id})
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

@Client.on_pre_checkout_query()
async def pre_checkout_handler(client, pre_checkout_query):
    await pre_checkout_query.answer(ok=True)

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
        
        await clone_mongo_db.vip_users.update_one(
            {"bot_id": me.id, "user_id": user_id},
            {"$set": {"expiry": expiry}},
            upsert=True
        )
        
        await message.reply_text(
            f"🎉 <b>VIP Activation Successful!</b>\n\n"
            f"Thank you for your payment of <b>{payment.total_amount} Telegram Stars</b>.\n\n"
            f"➜ Plan: <b>{days_label} VIP Access</b>\n"
            f"➜ Expiry: <code>{expiry_str}</code>\n\n"
            f"You bypass all shortlinks and TMA verifications! Enjoy instant downloads."
        )
        
        from config import ADMINS
        for admin in ADMINS:
            try:
                await client.send_message(
                    chat_id=admin,
                    text=f"<b>⭐ New VIP Purchase via Telegram Stars!</b>\n\n"
                         f"👤 <b>User:</b> {message.from_user.mention} (ID: <code>{user_id}</code>)\n"
                         f"🤖 <b>Bot ID:</b> <code>{me.id}</code>\n"
                         f"💵 <b>Amount:</b> <code>{payment.total_amount} Stars</code>\n"
                         f"📅 <b>Plan:</b> {days_label}"
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin} of successful payment: {e}")

@Client.on_message(filters.photo & filters.private & filters.incoming)
async def photo_message_handler(client, message):
    me = client.me or await client.get_me()
    state_doc = await clone_mongo_db.user_states.find_one({"bot_id": me.id, "user_id": message.from_user.id})
    if state_doc and state_doc.get("state") == "waiting_screenshot":
        await clone_mongo_db.user_states.delete_one({"bot_id": me.id, "user_id": message.from_user.id})
        
        from config import ADMINS
        for admin in ADMINS:
            try:
                await message.forward(admin)
                await client.send_message(
                    chat_id=admin,
                    text=f"<b>📩 New VIP Payment Receipt Screenshot!</b>\n\n"
                         f"👤 <b>From User:</b> {message.from_user.mention} (ID: <code>{message.from_user.id}</code>)\n"
                         f"🤖 <b>Bot ID:</b> <code>{me.id}</code>\n\n"
                         f"➜ To activate: `/addvip {message.from_user.id} [days]`\n"
                         f"➜ To decline: `/declinevip {message.from_user.id} [reason]`\n"
                         f"➜ To message: `/msg {message.from_user.id} [text]`"
                )
            except Exception as e:
                logger.error(f"Failed to forward screenshot to admin {admin}: {e}")
                
        await message.reply_text(
            "<b>Receipt sent successfully! Please wait for confirmation.</b>"
        )

@Client.on_message(filters.command("addvip") & filters.private & filters.user(ADMINS))
async def add_vip_handler(client, message):
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
            
        me = client.me or await client.get_me()
        await clone_mongo_db.vip_users.update_one(
            {"bot_id": me.id, "user_id": user_id},
            {"$set": {"expiry": expiry}},
            upsert=True
        )
        
        await message.reply_text(f"<b>✅ User <code>{user_id}</code> is now a VIP member ({days_label})!</b>")
        
        try:
            expiry_str = datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S') if expiry else "Lifetime"
            await client.send_message(
                chat_id=user_id,
                text=f"🎉 <b>Congratulations! You have been granted VIP access for {days_label}.</b>\n\n"
                     f"➜ Expires on: <code>{expiry_str}</code>\n"
                     f"You now bypass all shortlink/TMA verifications on this bot! Enjoy instant downloads."
            )
        except Exception as e:
            logger.error(f"Could not notify VIP user {user_id}: {e}")
            
    except ValueError:
        await message.reply_text("<b>❌ Invalid User ID or Days. Must be integers.</b>")
    except Exception as e:
        await message.reply_text(f"<b>❌ Error: {e}</b>")

@Client.on_message(filters.command("delvip") & filters.private & filters.user(ADMINS))
async def del_vip_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> `/delvip [user_id]`")
        
    try:
        user_id = int(message.command[1])
        me = client.me or await client.get_me()
        
        res = await clone_mongo_db.vip_users.delete_one({"bot_id": me.id, "user_id": user_id})
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

@Client.on_message(filters.command("declinevip") & filters.private & filters.user(ADMINS))
async def decline_vip_handler(client, message):
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

@Client.on_message(filters.command("msg") & filters.private & filters.user(ADMINS))
async def msg_user_handler(client, message):
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

@Client.on_message(filters.command("listvip") & filters.private & filters.user(ADMINS))
async def list_vip_handler(client, message):
    try:
        me = client.me or await client.get_me()
        vip_list = []
        async for user in clone_mongo_db.vip_users.find({"bot_id": me.id}):
            vip_list.append(user)
            
        if not vip_list:
            return await message.reply_text("<b>📭 No active VIP users found.</b>")
            
        from datetime import datetime
        text = f"<b>✨ <u>Active VIP Users ({len(vip_list)}):</u></b>\n\n"
        for i, user in enumerate(vip_list, 1):
            expiry = user.get("expiry")
            if expiry:
                expiry_str = datetime.fromtimestamp(expiry).strftime('%Y-%m-%d %H:%M:%S')
            else:
                expiry_str = "Lifetime"
            text += f"{i}. User ID: <code>{user['user_id']}</code>\n" \
                    f"   Expiry: <code>{expiry_str}</code>\n\n"
                    
        # Send in chunks if too long
        if len(text) > 4000:
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                await message.reply_text(chunk)
        else:
            await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"<b>❌ Error: {e}</b>")

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command("revoke_vplink") & filters.private & filters.user(ADMINS))
async def revoke_vplink_handler(client, message):
    """Revoke VPLink referral verification for a clone bot.
    Usage: /revoke_vplink [bot_id]
    """
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>📋 Usage:</b> <code>/revoke_vplink [bot_id]</code>\n\n"
            "Removes the VPLink referral verification from a clone bot.\n"
            "Use <code>/list_vplink</code> to see all verified bots and their IDs."
        )

    try:
        bot_id = int(message.command[1].strip())
    except ValueError:
        return await message.reply_text("<b>❌ Invalid Bot ID. Must be a number.</b>")

    bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
    if not bot:
        return await message.reply_text(f"<b>❌ No clone bot found with ID <code>{bot_id}</code>.</b>")

    vplink_verified = bot.get("vplink_verified", False)
    bot_username = bot.get("username", "unknown")
    owner_id = bot.get("user_id")

    if not vplink_verified:
        return await message.reply_text(
            f"<b>⚠️ @{bot_username} (<code>{bot_id}</code>) is not VPLink verified. Nothing to revoke.</b>"
        )

    # Revoke the verification
    await clone_mongo_db.bots.update_one(
        {"bot_id": bot_id},
        {"$set": {"vplink_verified": False}}
    )

    # Also clear any approved vplink_requests so owner can re-submit fresh
    await clone_mongo_db.vplink_requests.delete_many({"bot_id": bot_id})

    await message.reply_text(
        f"<b>✅ VPLink verification revoked!\n\n"
        f"🤖 Bot: @{bot_username} (<code>{bot_id}</code>)\n\n"
        f"The bot owner must re-register under the referral link and submit a new verification request to use TMA Ads or set a shortener API.</b>"
    )

    # Notify the clone bot owner
    if owner_id:
        try:
            from plugins.clone import running_clones
            clone_client = running_clones.get(bot_id, client)
            await clone_client.send_message(
                chat_id=owner_id,
                text="<b>⚠️ Your VPLink referral verification has been revoked by the admin.\n\n"
                     "TMA Ads and shortener API settings have been disabled for your bot.\n"
                     "To re-enable, register using the referral link and submit a new verification request from your bot's settings.</b>"
            )
        except Exception as e:
            logger.error(f"Could not notify clone bot owner {owner_id}: {e}")


@Client.on_message(filters.command("list_vplink") & filters.private & filters.user(ADMINS))
async def list_vplink_handler(client, message):
    """List clone bots and their VPLink verification status.
    Usage:
      /list_vplink           - shows all verified bots
      /list_vplink all       - shows all bots (verified + unverified)
      /list_vplink pending   - shows pending verification requests
    """
    mode = message.command[1].lower() if len(message.command) > 1 else "verified"

    if mode == "pending":
        pending = []
        async for req in clone_mongo_db.vplink_requests.find({"status": "pending"}).sort("requested_at", 1):
            pending.append(req)

        if not pending:
            return await message.reply_text("<b>📭 No pending VPLink verification requests.</b>")

        from datetime import datetime
        text = f"<b>⏳ Pending VPLink Requests ({len(pending)}):</b>\n\n"
        for i, req in enumerate(pending, 1):
            req_time = datetime.fromtimestamp(req.get("requested_at", 0)).strftime('%d/%m %H:%M') if req.get("requested_at") else "N/A"
            text += (
                f"{i}. 👤 {req.get('user_mention', 'Unknown')} (<code>{req.get('user_id')}</code>)\n"
                f"   🤖 @{req.get('username', 'N/A')} (ID: <code>{req.get('bot_id')}</code>)\n"
                f"   📅 {req_time}\n"
                f"   ▸ Approve: <code>/approve_vplink {req.get('bot_id')}</code>\n\n"
            )
        return await message.reply_text(text, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)

    query_filter = {} if mode == "all" else {"vplink_verified": True}
    verified_bots = []
    async for bot in clone_mongo_db.bots.find(query_filter).sort("bot_id", 1):
        verified_bots.append(bot)

    if not verified_bots:
        label = "verified" if mode == "verified" else "registered"
        return await message.reply_text(f"<b>📭 No {label} clone bots found.</b>")

    label = "Verified" if mode == "verified" else "All"
    text = f"<b>{'✅' if mode == 'verified' else '📋'} {label} VPLink Bots ({len(verified_bots)}):</b>\n\n"

    for i, bot in enumerate(verified_bots, 1):
        is_verified = "✅" if bot.get("vplink_verified") else "❌"
        text += (
            f"{i}. {is_verified} @{bot.get('username', 'N/A')}\n"
            f"   🆔 Bot ID: <code>{bot.get('bot_id')}</code>\n"
            f"   👤 Owner: <code>{bot.get('user_id')}</code>\n"
            f"   ▸ Revoke: <code>/revoke_vplink {bot.get('bot_id')}</code>\n\n"
        )

    # Send in chunks if too long
    if len(text) > 4000:
        chunks = []
        current = ""
        for line in text.split("\n"):
            if len(current) + len(line) + 1 > 4000:
                chunks.append(current)
                current = line + "\n"
            else:
                current += line + "\n"
        if current:
            chunks.append(current)
        for chunk in chunks:
            await message.reply_text(chunk, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command("approve_vplink") & filters.private & filters.user(ADMINS))
async def approve_vplink_cmd_handler(client, message):
    """Directly approve a VPLink verification request by bot_id from command.
    Usage: /approve_vplink [bot_id]
    """
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>📋 Usage:</b> <code>/approve_vplink [bot_id]</code>\n\n"
            "Use <code>/list_vplink pending</code> to see pending requests."
        )

    try:
        bot_id = int(message.command[1].strip())
    except ValueError:
        return await message.reply_text("<b>❌ Invalid Bot ID. Must be a number.</b>")

    import time
    bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
    if not bot:
        return await message.reply_text(f"<b>❌ No clone bot found with ID <code>{bot_id}</code>.</b>")

    if bot.get("vplink_verified"):
        return await message.reply_text(f"<b>⚠️ @{bot.get('username', bot_id)} is already verified!</b>")

    req = await clone_mongo_db.vplink_requests.find_one({"bot_id": bot_id})

    await clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"vplink_verified": True}})
    if req:
        await clone_mongo_db.vplink_requests.update_one(
            {"bot_id": bot_id},
            {"$set": {"status": "approved", "processed_at": time.time()}}
        )

    await message.reply_text(
        f"<b>✅ @{bot.get('username', bot_id)} (<code>{bot_id}</code>) has been VPLink verified!</b>"
    )

    owner_id = req.get("user_id") if req else bot.get("user_id")
    if owner_id:
        try:
            from plugins.clone import running_clones
            clone_client = running_clones.get(bot_id, client)
            await clone_client.send_message(
                chat_id=owner_id,
                text="<b>✅ You're verified! You can now enable TMA Ads and set your API key.\n\nUse /setting in your clone bot to configure it.</b>"
            )
        except Exception as e:
            logger.error(f"Could not notify owner {owner_id}: {e}")

async def upload_image(client, photo) -> tuple:
    """Download photo to memory and upload to ImgBB (primary) with fallbacks. Returns (url, debug_info)."""
    import io
    import aiohttp
    
    errors = []
    try:
        photo_bytes = await client.download_media(photo, in_memory=True)
        if not photo_bytes:
            return None, "Failed to download photo from Telegram"
            
        file_bytes = bytes(photo_bytes)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            # 1. ImgBB
            try:
                import base64
                b64_image = base64.b64encode(file_bytes).decode("utf-8")
                form = aiohttp.FormData()
                form.add_field("image", b64_image)
                imgbb_url = f"https://api.imgbb.com/1/upload?key=1e7383edb75ca41b8e32b515e9603a76"
                async with session.post(imgbb_url, data=form, timeout=15) as resp:
                    if resp.status == 200:
                        res_json = await resp.json()
                        if res_json.get("success") and "data" in res_json and "url" in res_json["data"]:
                            return res_json["data"]["url"], "ImgBB Success"
                        else:
                            errors.append(f"ImgBB success=False: {res_json}")
                    else:
                        res_txt = await resp.text()
                        errors.append(f"ImgBB status={resp.status} response={res_txt[:100]}")
            except Exception as e:
                errors.append(f"ImgBB Exception: {e}")

            # 2. Catbox.moe
            try:
                form = aiohttp.FormData()
                form.add_field("reqtype", "fileupload")
                form.add_field("fileToUpload", io.BytesIO(file_bytes), filename="image.jpg")
                async with session.post("https://catbox.moe/user/api.php", data=form, timeout=10) as resp:
                    res_text = await resp.text()
                    if res_text and res_text.strip().startswith("http"):
                        return res_text.strip(), f"Catbox Success (Failures: {'; '.join(errors)})"
                    else:
                        errors.append(f"Catbox: {res_text}")
            except Exception as e:
                errors.append(f"Catbox Exception: {e}")
                
            # 3. Telegra.ph
            try:
                form_fallback = aiohttp.FormData()
                form_fallback.add_field("file", io.BytesIO(file_bytes), filename="image.jpg")
                async with session.post("https://telegra.ph/upload", data=form_fallback, timeout=10) as resp:
                    result = await resp.json()
                    if isinstance(result, list) and result[0].get("src"):
                        return "https://telegra.ph" + result[0]["src"], f"Telegra.ph Success (Failures: {'; '.join(errors)})"
                    else:
                        errors.append(f"Telegra.ph: {result}")
            except Exception as e:
                errors.append(f"Telegra.ph Exception: {e}")
                
            # 4. Graph.org
            try:
                form_fallback = aiohttp.FormData()
                form_fallback.add_field("file", io.BytesIO(file_bytes), filename="image.jpg")
                async with session.post("https://graph.org/upload", data=form_fallback, timeout=10) as resp:
                    result = await resp.json()
                    if isinstance(result, list) and result[0].get("src"):
                        return "https://graph.org" + result[0]["src"], f"Graph.org Success (Failures: {'; '.join(errors)})"
                    else:
                        errors.append(f"Graph.org: {result}")
            except Exception as e:
                errors.append(f"Graph.org Exception: {e}")
                
            # 5. Tmpfiles.org
            try:
                form_tmp = aiohttp.FormData()
                form_tmp.add_field("file", io.BytesIO(file_bytes), filename="image.jpg")
                async with session.post("https://tmpfiles.org/api/v1/upload", data=form_tmp, timeout=10) as resp:
                    res3 = await resp.json()
                    if res3.get("status") == "success" and "data" in res3 and "url" in res3["data"]:
                        raw_url = res3["data"]["url"]
                        return raw_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/"), f"Tmpfiles Success (Failures: {'; '.join(errors)})"
                    else:
                        errors.append(f"Tmpfiles: {res3}")
            except Exception as e:
                errors.append(f"Tmpfiles Exception: {e}")
                
    except Exception as e:
        errors.append(f"Global download/bytes error: {e}")
        
    return None, " | ".join(errors)

@Client.on_message(filters.command("addpost") & filters.private & filters.user(ADMINS))
async def add_post_cmd_handler(client, message):
    replied = message.reply_to_message
    if replied:
        if not replied.photo or not replied.caption:
            return await message.reply_text("<b>❌ The replied message must have a photo and a caption.</b>")
            
        import re
        bot_username = None
        # Try to find full link e.g. https://t.me/my_clone_bot?start=payload
        bot_match = re.search(r"https?://t\.me/([A-Za-z0-9_]+)\?start=([A-Za-z0-9_-]+)", replied.caption)
        if bot_match:
            bot_username = bot_match.group(1)
            deeplink = bot_match.group(2)
        else:
            links = re.findall(r"start=([A-Za-z0-9_-]+)", replied.caption)
            if not links:
                links = re.findall(r"https?://t\.me/[A-Za-z0-9_]+\?start=([A-Za-z0-9_-]+)", replied.caption)
            if not links:
                return await message.reply_text("<b>❌ Could not find a bot start link (payload) in the caption.</b>")
            deeplink = links[0]
        
        lines = [l.strip() for l in replied.caption.split('\n') if l.strip()]
        title = lines[0] if lines else "Untitled"
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
                        
        sts = await message.reply_text("<b>⏳ Uploading poster (ImgBB) and adding post...</b>")
        
        image_url, debug_info = await upload_image(client, replied.photo)
        if not image_url:
            return await sts.edit_text(f"<b>❌ Failed to upload photo to any host.</b>\n\nDebug: <code>{debug_info}</code>")
            
        import uuid
        import time
        post_id = str(uuid.uuid4())[:8]
        await clone_mongo_db.posts.insert_one({
            "_id": post_id,
            "title": title,
            "image_url": image_url,
            "category": category,
            "file_deeplink": deeplink,
            "bot_username": bot_username,
            "created_at": time.time()
        })
        
        return await sts.edit_text(f"<b>✅ Post added successfully by reply!\n\nID: <code>{post_id}</code>\nTitle: {title}\nCategory: {category}\nBot Username: {bot_username or 'Default'}\nUploader: {debug_info}</b>")

    # Traditional manual add fallback
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>📋 Usage (Manual):</b> <code>/addpost Title | Image URL | Category | Start Payload</code>\n"
            "<b>Usage (Reply):</b> Reply to a channel post containing a photo and link with <code>/addpost [Category]</code>"
        )
        
    args = message.text.split(" ", 1)[1].split("|")
    if len(args) < 4:
        return await message.reply_text("<b>❌ Please provide all 4 fields separated by '|' for manual add.</b>")
        
    title = args[0].strip()
    image_url = args[1].strip()
    category = args[2].strip()
    deeplink = args[3].strip()
    
    bot_username = None
    if "t.me/" in deeplink:
        import re
        bot_match = re.search(r"https?://t\.me/([A-Za-z0-9_]+)\?start=([A-Za-z0-9_-]+)", deeplink)
        if bot_match:
            bot_username = bot_match.group(1)
            deeplink = bot_match.group(2)

    import uuid
    import time
    post_id = str(uuid.uuid4())[:8]
    
    await clone_mongo_db.posts.insert_one({
        "_id": post_id,
        "title": title,
        "image_url": image_url,
        "category": category,
        "file_deeplink": deeplink,
        "bot_username": bot_username,
        "created_at": time.time()
    })
    
    await message.reply_text(f"<b>✅ Post added successfully!\n\nID: <code>{post_id}</code>\nTitle: {title}\nCategory: {category}\nBot Username: {bot_username or 'Default'}</b>")


@Client.on_message(filters.command("delpost") & filters.private & filters.user(ADMINS))
async def del_post_cmd_handler(client, message):
    replied = message.reply_to_message
    if replied:
        if not replied.caption:
            return await message.reply_text("<b>❌ The replied message must have a caption containing the start link to delete.</b>")
            
        import re
        deeplink = None
        # Try to find full link e.g. https://t.me/my_clone_bot?start=payload
        bot_match = re.search(r"https?://t\.me/[A-Za-z0-9_]+\?start=([A-Za-z0-9_-]+)", replied.caption)
        if bot_match:
            deeplink = bot_match.group(1)
        else:
            links = re.findall(r"start=([A-Za-z0-9_-]+)", replied.caption)
            if not links:
                links = re.findall(r"https?://t\.me/[A-Za-z0-9_]+\?start=([A-Za-z0-9_-]+)", replied.caption)
            if not links:
                return await message.reply_text("<b>❌ Could not find a bot start link (payload) in the caption to identify the post.</b>")
            deeplink = links[0]
            
        res = await clone_mongo_db.posts.delete_one({"file_deeplink": deeplink})
        if res.deleted_count > 0:
            return await message.reply_text("<b>✅ Post deleted successfully by reply!</b>")
        else:
            return await message.reply_text("<b>❌ Post not found in database for this link.</b>")

    if len(message.command) < 2:
        return await message.reply_text(
            "<b>📋 Usage:</b> <code>/delpost [Post ID]</code>\n"
            "<b>Usage (Reply):</b> Reply to the post's message with <code>/delpost</code>"
        )
        
    post_id = message.command[1].strip()
    res = await clone_mongo_db.posts.delete_one({"_id": post_id})
    if res.deleted_count > 0:
        await message.reply_text("<b>✅ Post deleted successfully!</b>")
    else:
        await message.reply_text("<b>❌ Post not found in database.</b>")



@Client.on_message(filters.command("bulkaddpost") & filters.private & filters.user(ADMINS))
async def bulk_add_post_cmd_handler(client, message):
    # Interactive flow variables
    chat_id = None
    start_msg_id = None
    end_msg_id = None
    default_category = "General"
    
    import re
    
    # Check if arguments were passed directly (non-interactive fallback)
    if len(message.command) >= 4:
        chat_id = message.command[1].strip()
        if chat_id.isdigit() or chat_id.startswith("-100"):
            chat_id = int(chat_id)
            
        try:
            start_msg_id = int(message.command[2].strip())
            end_msg_id = int(message.command[3].strip())
        except ValueError:
            return await message.reply_text("<b>❌ Message IDs must be integers.</b>")
            
        default_category = message.command[4].strip() if len(message.command) > 4 else "General"
    else:
        # Step-by-step interactive flow using client.ask
        try:
            # 1. Ask for first message
            first_prompt = await client.ask(
                message.chat.id, 
                "<b>Forward the FIRST message from the channel here, or paste its link.</b>\n\nType <code>/cancel</code> to abort."
            )
            if first_prompt.text == "/cancel":
                return await message.reply_text("<b>❌ Cancelled bulk import.</b>")
                
            if first_prompt.forward_from_chat:
                chat_id = first_prompt.forward_from_chat.id
                start_msg_id = first_prompt.forward_from_message_id
            elif first_prompt.text:
                link_match = re.search(r"t\.me/(?:c/)?([a-zA-Z0-9_-]+)/(\d+)", first_prompt.text)
                if link_match:
                    chat_id = link_match.group(1)
                    if chat_id.isdigit():
                        chat_id = int("-100" + chat_id)
                    start_msg_id = int(link_match.group(2))
                elif first_prompt.text.isdigit():
                    start_msg_id = int(first_prompt.text)
                    
            if not start_msg_id:
                return await message.reply_text("<b>❌ Invalid message. Please forward the message or paste a message link.</b>")
                
            # 2. Ask for last message
            last_prompt = await client.ask(
                message.chat.id, 
                "<b>Forward the LAST message from the channel here, or paste its link.</b>\n\nType <code>/cancel</code> to abort."
            )
            if last_prompt.text == "/cancel":
                return await message.reply_text("<b>❌ Cancelled bulk import.</b>")
                
            if last_prompt.forward_from_chat:
                end_msg_id = last_prompt.forward_from_message_id
                if not chat_id:
                    chat_id = last_prompt.forward_from_chat.id
            elif last_prompt.text:
                link_match = re.search(r"t\.me/(?:c/)?([a-zA-Z0-9_-]+)/(\d+)", last_prompt.text)
                if link_match:
                    end_msg_id = int(link_match.group(2))
                elif last_prompt.text.isdigit():
                    end_msg_id = int(last_prompt.text)
                    
            if not end_msg_id:
                return await message.reply_text("<b>❌ Invalid message. Please forward the last message or paste a message link.</b>")
                
            # Ask for chat_id if we couldn't get it from forwarded chat details
            if not chat_id:
                chat_prompt = await client.ask(
                    message.chat.id, 
                    "<b>Send the Channel Username (e.g. @mychannel) or ID:</b>"
                )
                chat_id = chat_prompt.text.strip()
                if chat_id.isdigit() or chat_id.startswith("-100"):
                    chat_id = int(chat_id)
                    
            # 3. Ask for default category
            cat_prompt = await client.ask(
                message.chat.id, 
                "<b>Send the default category name (e.g. Action) or type <code>/skip</code> to use 'General':</b>"
            )
            default_category = cat_prompt.text.strip() if cat_prompt.text != "/skip" else "General"
            
        except Exception as ask_err:
            return await message.reply_text(f"<b>❌ Interactive mode error: {ask_err}</b>")

    # Run Bulk Import
    sts = await message.reply_text("<b>⏳ Fetching messages and importing posts... Please wait.</b>")
    imported_count = 0
    skipped_count = 0
    
    import uuid
    import time

    for msg_id in range(start_msg_id, end_msg_id + 1):
        try:
            msg = await client.get_messages(chat_id, msg_id)
            if not msg or msg.empty:
                skipped_count += 1
                continue
                
            if msg.video or msg.document or msg.audio or msg.voice:
                skipped_count += 1
                continue
                
            if not msg.photo or not msg.caption:
                skipped_count += 1
                continue
                
            # Parse start payload link and bot username
            bot_username = None
            bot_match = re.search(r"https?://t\.me/([A-Za-z0-9_]+)\?start=([A-Za-z0-9_-]+)", msg.caption)
            if bot_match:
                bot_username = bot_match.group(1)
                deeplink = bot_match.group(2)
            else:
                links = re.findall(r"start=([A-Za-z0-9_-]+)", msg.caption)
                if not links:
                    links = re.findall(r"https?://t\.me/[A-Za-z0-9_]+\?start=([A-Za-z0-9_-]+)", msg.caption)
                if not links:
                    skipped_count += 1
                    continue
                deeplink = links[0]
            
            # Parse title & category
            lines = [l.strip() for l in msg.caption.split('\n') if l.strip()]
            title = lines[0] if lines else "Untitled"
            title = re.sub(r'<[^>]+>', '', title)
            title = re.sub(r'[*_`~]', '', title).strip()
            
            category = default_category
            for line in lines:
                if line.lower().startswith("category:") or line.lower().startswith("genre:"):
                    parsed_cat = line.split(":", 1)[1].strip()
                    parsed_cat = re.sub(r'<[^>]+>', '', parsed_cat).strip()
                    if parsed_cat:
                        category = parsed_cat
                        break
            
            # Download and upload photo using multi-provider helper
            image_url, debug_info = await upload_image(client, msg.photo)
            if not image_url:
                image_url = "/static/LOGO.jpg"
                
            post_id = str(uuid.uuid4())[:8]
            await clone_mongo_db.posts.insert_one({
                "_id": post_id,
                "title": title,
                "image_url": image_url,
                "category": category,
                "file_deeplink": deeplink,
                "bot_username": bot_username,
                "created_at": time.time()
            })
            imported_count += 1
            # Prevent rate limits / flood waits
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error importing message {msg_id}: {e}")
            skipped_count += 1
            
    await sts.edit_text(
        f"<b>✅ Bulk Import Complete!</b>\n\n"
        f"📥 Imported: <code>{imported_count}</code> posts\n"
        f"🚫 Skipped: <code>{skipped_count}</code> messages"
    )

