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
from pyrogram import Client, filters, enums
from plugins.clone import async_mongo_db as mongo_db
from pyrogram.errors import ChatAdminRequired, FloodWait, UserNotParticipant
from config import BOT_USERNAME, ADMINS, LOG_CHANNEL
from config import PICS, CUSTOM_FILE_CAPTION, AUTO_DELETE_TIME, AUTO_DELETE, UNIVERSAL_FORCE_SUB_CHANNEL, URL
from utils import is_subscribed_universal, check_tma_verification, get_tma_link, verify_tma_user, is_token_consumed, consume_token, validate_tma_token, is_vip
import config
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto, WebAppInfo
import re
import json
import base64
import time
import string
from shortzy import Shortzy

logger = logging.getLogger(__name__)

CLONE_TOKENS = {}
CLONE_VERIFIED = {}
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

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    me = client.me or await client.get_me()
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
        buttons = [[
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
    
    is_unlocked = False
    if data.split("-", 1)[0] == "unlock":
        parts = data.split("-", 4)
        if len(parts) >= 5:
            _, userid_str, ts, sig, file_data = parts
            token = f"{ts}-{sig}"
            if str(message.from_user.id) == userid_str:
                if validate_tma_token(message.from_user.id, token):
                    if not is_token_consumed(token):
                        consume_token(token)
                        is_unlocked = True
                        data = file_data
                        await verify_tma_user(message.from_user.id, token)
                        await message.reply_text(
                            text=script.TMA_VERIFIED_TEXT.format(message.from_user.mention),
                            protect_content=True
                        )
                    else:
                        return await message.reply_text(text="<b>This link has already been used to unlock the file! Please click the file link again to get a fresh ad session.</b>", protect_content=True)
                else:
                    return await message.reply_text(text="<b>This verification link has expired! Please watch the ad again.</b>", protect_content=True)
            else:
                return await message.reply_text(text="<b>This verification link belongs to another user!</b>", protect_content=True)
        else:
            return await message.reply_text(text="<b>Invalid unlock link!</b>", protect_content=True)

    if data.split("-", 1)[0] == "tma":
        parts = data.split("-")
        if len(parts) >= 3:
            tma_uid = int(parts[1])
            tma_token = "-".join(parts[2:])
            if message.from_user.id != tma_uid:
                return await message.reply_text(text=script.TMA_EXPIRED_TEXT, protect_content=True)
            ok = await verify_tma_user(tma_uid, tma_token)
            if ok:
                await message.reply_text(
                    text=script.TMA_VERIFIED_TEXT.format(message.from_user.mention),
                    protect_content=True
                )
            else:
                await message.reply_text(text=script.TMA_EXPIRED_TEXT, protect_content=True)
        return

    if data.startswith("verify-"):
        logger.info("Detected verification payload")
        parts = data.split("-", 3)
        if len(parts) >= 3:
            _, userid, token = parts[:3]
            file_data = parts[3] if len(parts) == 4 else None
        else:
            return await message.reply_text("<b>Invalid format!</b>", protect_content=True)
            
        if str(message.from_user.id) != str(userid):
            return await message.reply_text("<b>Invalid link or Expired link!</b>", protect_content=True)
        
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
            return await message.reply_text("<b>Invalid link or Expired link!</b>", protect_content=True)

    if data.startswith("BATCH-"):
        logger.info("Detected BATCH payload")
        try:
            # Token Verification Check for Batch
            token_mode = bot_doc.get("token_verify", False) if bot_doc else False
            tma_mode = bot_doc.get("tma_mode", False) if bot_doc else False
            if token_mode or tma_mode:
                user_is_vip = await is_vip(me.id, message.from_user.id)
                if user_is_vip:
                    is_verified = True
                else:
                    timeout = bot_doc.get("token_timeout", 86400)
                    key = f"{me.id}_{message.from_user.id}"
                    is_verified = False
                    
                    if tma_mode:
                        is_verified = await check_tma_verification(message.from_user.id)
                    else:
                        if key in CLONE_VERIFIED:
                            if time.time() < CLONE_VERIFIED[key] + timeout:
                                is_verified = True
                
                if not is_verified and not is_unlocked:
                    tma_mode = bot_doc.get("tma_mode", False) if bot_doc else False
                    if tma_mode:
                        tma_app_url = f"{URL.rstrip('/')}/tma"
                        tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data, bot_username=me.username)
                        btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))]]
                        return await message.reply_text(
                            text=script.TMA_UNLOCK_TEXT.format(message.from_user.mention),
                            protect_content=True,
                            reply_markup=InlineKeyboardMarkup(btn)
                        )
                    pass
                else:
                    is_verified = True
            
            if not token_mode or (token_mode and (is_verified or is_unlocked)):
                sts = await message.reply("<b>🔺 ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ... ɢᴇᴛᴛɪɴɢ ʙᴀᴛᴄʜ ғɪʟᴇs</b>")
                file_id = data.split("-", 1)[1]
                msgs = BATCH_FILES.get(file_id)
                if not msgs:
                    from TechVJ.bot import StreamBot
                    from config import LOG_CHANNEL
                    decode_file_id = base64.urlsafe_b64decode(file_id + "=" * (-len(file_id) % 4)).decode("ascii")
                    # Use Main Bot to get the message from Log Channel
                    msg = await StreamBot.get_messages(LOG_CHANNEL, int(decode_file_id))
                    media = getattr(msg, msg.media.value)
                    # Download the JSON file using Main Bot
                    path = await StreamBot.download_media(media.file_id)
                    with open(path, "r") as f:
                        msgs = json.load(f)
                    os.remove(path)
                    BATCH_FILES[file_id] = msgs
                
                for m_data in msgs:
                    try:
                        c_id = m_data.get("channel_id")
                        m_id = m_data.get("msg_id")
                        # Clone bot sends the message to the user
                        is_nofwd = bot_doc.get("no_forward", False) if bot_doc else False
                        await client.copy_message(
                            chat_id=message.from_user.id, 
                            from_chat_id=c_id, 
                            message_id=m_id,
                            protect_content=is_nofwd
                        )
                    except Exception as e:
                        logger.error(f"Batch copy error: {e}")
                
                await sts.delete()
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

    # Token Verification Check
    token_mode = bot_owner.get("token_verify", False) if bot_owner else False
    tma_mode = bot_owner.get("tma_mode", False) if bot_owner else False
    logger.info(f"Token verify mode: {token_mode}, TMA mode: {tma_mode}")
    if token_mode or tma_mode:
        site = bot_owner.get("shortener_site") or ""
        api = bot_owner.get("shortener_api") or ""
        timeout = bot_owner.get("token_timeout", 86400)
        tut_url = bot_owner.get("token_tutorial") or "https://t.me"
        
        key = f"{me.id}_{message.from_user.id}"
        user_is_vip = await is_vip(me.id, message.from_user.id)
        if user_is_vip:
            is_verified = True
        else:
            tma_mode = bot_owner.get("tma_mode", False) if bot_owner else False
            if tma_mode:
                is_verified = await check_tma_verification(message.from_user.id)
            else:
                if key in CLONE_VERIFIED:
                    if time.time() < CLONE_VERIFIED[key] + timeout:
                        is_verified = True
        
        logger.info(f"User verified status: {is_verified}")
        if not is_verified and not is_unlocked:
            tma_mode = bot_owner.get("tma_mode", False) if bot_owner else False
            if tma_mode:
                tma_app_url = f"{URL.rstrip('/')}/tma"
                tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data, bot_username=me.username)
                btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))]]
                return await message.reply_text(
                    text=script.TMA_UNLOCK_TEXT.format(message.from_user.mention),
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            
            if not site or not api:
                return await message.reply_text("<b>Access Token settings are not fully configured by the bot owner.</b>")
            
            logger.info("Redirecting user to verification")
            # Clean URL to prevent Shortzy crashes
            clean_site = site.replace("https://", "").replace("http://", "").strip("/")
            
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
            CLONE_TOKENS[key] = {token: False}
            verify_link = f"https://t.me/{me.username}?start=verify-{message.from_user.id}-{token}-{data}"
            
            try:
                shortzy = Shortzy(api_key=api, base_site=clean_site)
                short_link = await shortzy.convert(verify_link)
                logger.info(f"Shortlink generated: {short_link}")
            except Exception as e:
                logger.error(f"Clone shortener error: {e}")
                short_link = verify_link
                
            # Ensure tut_url is a valid URL string
            if not tut_url or not str(tut_url).startswith("http"):
                tut_url = "https://t.me/viralverse0909"
            
            btn = [[
                InlineKeyboardButton("Verify", url=str(short_link))
            ],[
                InlineKeyboardButton("How To Open Link & Verify", url=str(tut_url))
            ]]
            
            try:
                logger.info(f"Sending verification message to {message.from_user.id}...")
                v_msg = await asyncio.wait_for(
                    client.send_message(
                        chat_id=message.from_user.id,
                        text="<b>You are not verified!\nKindly verify to continue!</b>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    ),
                    timeout=15
                )
                logger.info(f"Verification message sent. ID: {v_msg.id}")
            except asyncio.TimeoutError:
                logger.error("CRITICAL: send_message timed out after 15 seconds!")
                await message.reply_text("<b>⚠️ Verification service is slow. Please try again in a moment.</b>")
            except Exception as e:
                logger.error(f"Failed to send verification message: {e}")
                await message.reply_text(f"<b>❌ Error: {e}</b>")
            return

    logger.info("Proceeding to send_cached_media...")
    try:
        is_nofwd = bot_owner.get("no_forward", False) if bot_owner else False
        msg = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            protect_content=is_nofwd
        )
        logger.info(f"send_cached_media successful (protect_content={is_nofwd})")
    except Exception as e:
        logger.error(f"Clone bot send_cached_media error for file_id {file_id}: {e}")
        return await message.reply_text(f"<b>❌ Error sending file! The file ID might be invalid or generated by a different bot.\n\nError: <code>{e}</code></b>")
        
    try:
        filetype = msg.media
        file = getattr(msg, filetype.value)
        # Build title: strip existing @mentions/URLs, then prepend owner's prefix
        old_title = getattr(file, "file_name", "") or ""
        clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('http') and not x.startswith('www.'), old_title.split()))
        title = (caption_prefix + ' ' + clean_name).strip() if caption_prefix else clean_name
        size = get_size(getattr(file, "file_size", 0))
        f_caption = f"<code>{title}</code>" if title else ""
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
            except:
                pass
        
        if f_caption:
            await msg.edit_caption(f_caption)
        
        # Dynamic Auto Delete
        is_autodel = bot_owner.get("auto_delete_enabled", True) if bot_owner else True
        if is_autodel:
            del_time = bot_owner.get("auto_delete_time", 5) if bot_owner else 5
            k = await msg.reply(f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{del_time} mins</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</i></b>",quote=True)
            
            async def auto_delete_task(m, warning_msg, delay):
                await asyncio.sleep(delay * 60)
                try:
                    await m.delete()
                    await warning_msg.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
                except: pass
            
            asyncio.create_task(auto_delete_task(msg, k, del_time))
        return
    except Exception as e:
        logger.error(f"Clone bot caption/auto-delete error: {e}")

@Client.on_message(filters.command("setting") & filters.private & filters.incoming)
async def settings_command(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    # Owner/Moderator check
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods:
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
    buttons = [[
        InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ', callback_data='set_api'),
        InlineKeyboardButton('sᴇᴛ ʙᴀsᴇ sɪᴛᴇ', callback_data='set_site')
    ],[
        InlineKeyboardButton('📝 sᴇᴛ ᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx', callback_data='set_caption'),
        InlineKeyboardButton(f"TMA Ads: {'ON 🟢' if tma_mode else 'OFF 🔴'}", callback_data="toggle_tma")
    ],[
        InlineKeyboardButton('💳 Configure Plan', callback_data='setplan'),
        InlineKeyboardButton('💬 ᴄʜᴀᴛʙox', url='https://t.me/+cFO-dJGWlCMzNGRl')
    ],[
        InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909'),
        InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help')
    ],[
        InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about'),
        InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
    ]]
    
    if bot_doc and int(bot_doc['user_id']) == message.from_user.id:
        from TechVJ.bot import StreamBot
        main_bot_username = (await StreamBot.get_me()).username
        buttons.insert(0, [InlineKeyboardButton('🔒 Fᴏʀᴄᴇ Sᴜʙ Sᴇᴛᴛɪɴɢs', url=f"https://t.me/{main_bot_username}?start=manageclone_{me.id}")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴄᴜʀʀᴇɴᴛ ʙᴀsᴇ sɪᴛᴇ: {user['base_site']}\nᴄᴜʀʀᴇɴᴛ ᴀᴘɪ: <code>{user['shortener_api']}</code>\nᴛᴍᴀ ᴀᴅs: <code>{tma_status}</code>\nᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx: {prefix}</b>",
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

    if not bot_owner or int(bot_owner['user_id']) != m.from_user.id:
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

    # Owner/Moderator check
    owner_id = int(bot_owner.get("user_id", 0)) if bot_owner else 0
    mods = bot_owner.get("moderators", []) if bot_owner else []
    if m.from_user.id != owner_id and m.from_user.id not in mods:
        return await m.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")

    user_id = m.from_user.id
    user = await get_user(me.id, user_id)
    cmd = m.command

    if len(cmd) == 1:
        s = script.SHORTENER_API_MESSAGE.format(base_site=user["base_site"], shortener_api=user["shortener_api"])
        return await m.reply(s)

    elif len(cmd) == 2:    
        api = cmd[1].strip()
        await update_user_info(me.id, user_id, {"shortener_api": api})
        await m.reply("Shortener API updated successfully to " + api)
    else:
        await m.reply("You are not authorized to use this command.")

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    me = client.me or await client.get_me()
    bot_owner = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_owner and bot_owner.get("is_deactivated", False):
        return await m.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    # Owner/Moderator check
    owner_id = int(bot_owner.get("user_id", 0)) if bot_owner else 0
    mods = bot_owner.get("moderators", []) if bot_owner else []
    if m.from_user.id != owner_id and m.from_user.id not in mods:
        return await m.reply("<b>❌ Only the bot owner and moderators can use this command.</b>")

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
    
    # Owner/Moderator check
    owner_id = int(bot_doc.get("user_id", 0))
    mods = bot_doc.get("moderators", [])
    if message.from_user.id != owner_id and message.from_user.id not in mods:
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

    # Owner/Moderator check
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    if message.from_user.id != owner_id and message.from_user.id not in mods:
        return await message.reply("<b>❌ Only the bot owner and moderators can access this command.</b>")

    from utils import TMA_VERIFIED
    import time
    
    text = "<b>📅 <u>Active Verifications</u></b>\n\n"
    
    # 1. TMA Verifications (3 Hours)
    tma_count = 0
    tma_text = "<b>⚡ TMA Verifications (3-Hour Validity):</b>\n"
    current_time = time.time()
    for uid, verified_time in list(TMA_VERIFIED.items()):
        elapsed = current_time - verified_time
        if elapsed < 3 * 3600:
            tma_count += 1
            remaining = int((3 * 3600) - elapsed)
            hours = remaining // 3600
            mins = (remaining % 3600) // 60
            tma_text += f"• <code>{uid}</code> (Remaining: {hours}h {mins}m)\n"
        else:
            TMA_VERIFIED.pop(uid, None)
            
    if tma_count == 0:
        tma_text += "<i>No active TMA verifications.</i>\n"
        
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
        
    total_text = text + tma_text + std_text
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
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "toggle_tma":
        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
        mods = bot_doc.get("moderators", []) if bot_doc else []
        if query.from_user.id != owner_id and query.from_user.id not in mods:
            return await query.answer("❌ Only the bot owner and moderators can configure TMA settings!", show_alert=True)
        tma_mode = bot_doc.get("tma_mode", False) if bot_doc else False
        new_mode = not tma_mode
        await mongo_db.bots.update_one({"bot_id": me.id}, {"$set": {"tma_mode": new_mode}})
        await query.answer(f"TMA Ads {'Enabled 🟢' if new_mode else 'Disabled 🔴'}", show_alert=True)
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

        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(photo)
        )
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

        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(photo)
        )
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
        bot_doc = mongo_db.bots.find_one({'bot_id': me.id})
        photo = bot_doc.get("start_photo") if bot_doc else None
        if photo and not photo.startswith("http"): photo = None
        if not photo: photo = random.choice(PICS)

        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(photo)
        )
        owner = await mongo_db.bots.find_one({'bot_id': me.id})
        ownerid = int(owner['user_id'])
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CABOUT_TXT.format(me.mention, ownerid),
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
        
        buttons = [[
            InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ', callback_data='set_api'),
            InlineKeyboardButton('sᴇᴛ ʙᴀsᴇ sɪᴛᴇ', callback_data='set_site')
        ],[
            InlineKeyboardButton('📝 sᴇᴛ ᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx', callback_data='set_caption'),
            InlineKeyboardButton(f"TMA Ads: {'ON 🟢' if tma_mode else 'OFF 🔴'}", callback_data="toggle_tma")
        ],[
            InlineKeyboardButton('💳 Configure Plan', callback_data='setplan'),
            InlineKeyboardButton('💬 ᴄʜᴀᴛʙox', url='https://t.me/+cFO-dJGWlCMzNGRl')
        ],[
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909'),
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help')
        ],[
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about'),
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
        ]]
        
        photo = bot_doc.get("start_photo") if bot_doc else None
        if photo and not photo.startswith("http"): photo = None
        if not photo: photo = random.choice(PICS)

        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(photo)
        )
        if bot_doc and int(bot_doc['user_id']) == query.from_user.id:
            from TechVJ.bot import StreamBot
            main_bot_username = (await StreamBot.get_me()).username
            buttons.insert(0, [InlineKeyboardButton('🔒 Fᴏʀᴄᴇ Sᴜʙ Sᴇᴛᴛɪɴɢs', url=f"https://t.me/{main_bot_username}?start=manageclone_{me.id}")])

        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴄᴜʀʀᴇɴᴛ ʙᴀsᴇ sɪᴛᴇ: {user['base_site']}\nᴄᴜʀʀᴇɴᴛ ᴀᴘɪ: <code>{user['shortener_api']}</code>\nᴛᴍᴀ ᴀᴅs: <code>{tma_status}</code>\nᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx: {prefix}</b>",
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
            text="<b>✍️ Now please send the plans text with prices (or send /cancel to skip).\n\nExample:\n<code>1 Month - $5\n3 Months - $12\nLifetime - $30</code></b>"
        )
        if msg_text.text and msg_text.text.strip() == "/cancel":
            return await msg_text.reply("<b>Cancelled plan configuration.</b>")
            
        plans_text = msg_text.text.html if msg_text.text else "Plans not configured"
        
        await mongo_db.plans_config.update_one(
            {"_id": me.id},
            {"$set": {
                "payment_qr": qr_file_id,
                "plans_text": plans_text
            }},
            upsert=True
        )
        
        await msg_text.reply("<b>✅ Payment Plan configured successfully!</b>")
        query.data = "settings"
        return await cb_handler(client, query)

    elif query.data == "buy_plan":
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
        
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=qr_file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start")]])
        )
        await query.message.delete()
        await query.answer()

@Client.on_message(filters.command("plan") & filters.private)
async def plan_command_handler(client, message):
    me = client.me or await client.get_me()
    plan_cfg = await mongo_db.plans_config.find_one({"_id": me.id})
    if not plan_cfg:
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

@Client.on_message(filters.photo & filters.private & filters.incoming)
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
                             f"👤 <b>From User:</b> {message.from_user.mention} (ID: <code>{message.from_user.id}</code>)\n"
                             f"To activate, use: `/addvip {message.from_user.id} [days]`"
                    )
                except Exception as e:
                    logger.error(f"Failed to forward screenshot to {rcpt}: {e}")
                
        await message.reply_text(
            "<b>Receipt sent successfully! Please wait for confirmation.</b>"
        )

@Client.on_message(filters.command("addvip") & filters.private)
async def add_vip_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if message.from_user.id != owner_id and message.from_user.id not in mods:
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

@Client.on_message(filters.command("delvip") & filters.private)
async def del_vip_handler(client, message):
    me = client.me or await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if message.from_user.id != owner_id and message.from_user.id not in mods:
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
