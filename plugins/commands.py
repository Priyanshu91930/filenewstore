# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import os
import logging
import random
import asyncio
from validators import domain
from Script import script
from plugins.dbusers import db
from pyrogram import Client, filters, enums
from plugins.users_api import get_user, update_user_info
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery, Message, WebAppInfo
from utils import verify_user, check_token, check_verification, get_token, is_subscribed, is_subscribed_universal, get_tma_link, verify_tma_user, check_tma_verification
from config import *
from config import TMA_MODE, MONETAG_ZONE_ID, URL
import config
import re
import json
import base64
from urllib.parse import quote_plus
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size
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
            buttons = [[
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
        
        # Handle clone redirect from button
        if data == "clone":
            from plugins.clone import clone
            return await clone(client, message)
            
        if data.startswith("manageclone_"):
            bot_id = int(data.split("_")[-1])
            bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
            if not bot or int(bot.get("user_id", 0)) != message.from_user.id:
                return await message.reply("<b>❌ You don't own this bot!</b>")
                
            buttons = [
                [InlineKeyboardButton("START MSG", callback_data=f"startmsg_{bot_id}"), InlineKeyboardButton("FORCE SUB", callback_data=f"forcesub_{bot_id}")],
                [InlineKeyboardButton("MODERATORS", callback_data=f"mods_{bot_id}"), InlineKeyboardButton("AUTO DELETE", callback_data=f"autodel_{bot_id}")],
                [InlineKeyboardButton("NO FORWARD", callback_data=f"nofwd_{bot_id}"), InlineKeyboardButton("ACCESS TOKEN", callback_data=f"token_{bot_id}")],
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
                return await message.reply_text(
                    text="<b>Invalid link or Expired link !</b>",
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
                return await message.reply_text(
                    text="<b>Invalid link or Expired link !</b>",
                    protect_content=True
                )
        # TMA verification callback: /start tma-{uid}-{token}
        elif data.split("-", 1)[0] == "tma":
            parts = data.split("-")
            if len(parts) >= 3:
                tma_uid = int(parts[1])
                tma_token = "-".join(parts[2:])  # token may contain a dash
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
        elif data.split("-", 1)[0] == "BATCH":
            try:
                # TMA Mode: use Monetag Mini App for verification
                if config.TMA_MODE and not await check_tma_verification(message.from_user.id):
                    tma_app_url = f"{URL.rstrip('/')}/tma"
                    # Pass the raw /start data so the Mini App knows which file to deliver
                    tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data)
                    btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))]]
                    await message.reply_text(
                        text=script.TMA_UNLOCK_TEXT.format(message.from_user.mention),
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
                    if STREAM_MODE == True:
                            if info.video or info.document:
                                log_msg = info
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
            if AUTO_DELETE_MODE == True:
                k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
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
        # TMA Mode: use Monetag Mini App for verification
        if config.TMA_MODE and not await check_tma_verification(message.from_user.id):
            tma_app_url = f"{URL.rstrip('/')}/tma"
            # Pass the raw /start data so the Mini App knows which file to deliver
            tma_link = await get_tma_link(client, message.from_user.id, tma_app_url, file_data=data)
            btn = [[InlineKeyboardButton("🎯 Watch Ad & Unlock File", web_app=WebAppInfo(url=tma_link))]]
            await message.reply_text(
                text=script.TMA_UNLOCK_TEXT.format(message.from_user.mention),
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
                if STREAM_MODE == True:
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
                            ]]
                            reply_markup=InlineKeyboardMarkup(button)
                del_msg = await msg.copy(chat_id=message.from_user.id, caption=f_caption, reply_markup=reply_markup, protect_content=False)
            else:
                del_msg = await msg.copy(chat_id=message.from_user.id, protect_content=False)
            if AUTO_DELETE_MODE == True:
                k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</b>")
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
    
    # 2. Total Clones
    total_clones = await clone_mongo_db.bots.count_documents({})
    
    # 3. Total Users Across Clones
    total_clone_users = 0
    try:
        collections = await clonedb.db.list_collection_names()
        for col in collections:
            # Clonedb stores users in collections named by bot_id (numeric)
            if col.isdigit(): 
                count = await clonedb.db[col].count_documents({})
                total_clone_users += count
    except Exception as e:
        logger.error(f"Error counting clone users: {e}")
            
    await m.edit_text(
        f"<b>📊 <u>Bot Statistics</u>\n\n"
        f"👤 Main Bot Users: <code>{main_users}</code>\n"
        f"🤖 Total Clones Made: <code>{total_clones}</code>\n"
        f"👥 Total Users in Clones: <code>{total_clone_users}</code></b>"
    )

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
    buttons = [[
        InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ', callback_data='set_api'),
        InlineKeyboardButton('sᴇᴛ ʙᴀsᴇ sɪᴛᴇ', callback_data='set_site')
    ],[
        InlineKeyboardButton(f"TMA Ads: {'ON 🟢' if config.TMA_MODE else 'OFF 🔴'}", callback_data="toggle_tma")
    ],[
        InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴄᴜʀʀᴇɴᴛ ʙᴀsᴇ sɪᴛᴇ: {user['base_site']}\nᴄᴜʀʀᴇɴᴛ ᴀᴘɪ: <code>{user['shortener_api']}</code>\nᴛᴍᴀ ᴀᴅs: <code>{tma_status}</code></b>",
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
        buttons = [[
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
        user_id = query.from_user.id
        bots = [b async for b in clone_mongo_db.bots.find({"user_id": user_id})]
        buttons = []
        for bot in bots:
            buttons.append([InlineKeyboardButton(f"{bot['name']}", callback_data=f"cust_{bot['bot_id']}")])
        
        buttons.append([InlineKeyboardButton("➕ Add Clone", callback_data="add_clone")])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="start")])
        
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text="<b>✨ <u>Manage Clone's</u>\n\nYou can now manage and create your very own identical clone bot, mirroring all my awesome features, using the given buttons.</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
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
        
        await query.message.edit_text(
            text=f"<b>🪄 <u>Customize Clone</u>\n\n➜ Name: <i>{bot['name']}</i>\n\nConfigure Your Clone Settings Using Given Buttons</b>",
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
            clone_mongo_db.bots.delete_one({"bot_id": bot_id})
            await query.message.edit_text(f"<b>✅ @{bot['username']} has been stopped and deleted.</b>")
            await msg.reply("<b>Bot stopped and deleted successfully. ✅</b>")
        else:
            await msg.reply("<b>Deletion cancelled.</b>")

    elif query.data.startswith("stxt_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Please send the new START TEXT for your clone bot.\n\nUse {mention} for user mention and {mention2} for bot mention.\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"start_text": msg.text.html}})
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
                photo_bytes = await client.download_media(msg.photo.file_id, in_memory=True)
                photo_bytes.seek(0)
                
                # Upload to telegra.ph (Telegraph's image host) to get a permanent public URL
                async with aiohttp.ClientSession() as session:
                    form = aiohttp.FormData()
                    form.add_field("file", photo_bytes, filename="start.jpg")
                    async with session.post("https://telegra.ph/upload", data=form) as resp:
                        result = await resp.json()
                        if isinstance(result, list) and result[0].get("src"):
                            photo_url = "https://telegra.ph" + result[0]["src"]
                        else:
                            # Fallback to graph.org if telegra.ph fails
                            async with session.post("https://graph.org/upload", data=form) as resp2:
                                result2 = await resp2.json()
                                if isinstance(result2, list) and result2[0].get("src"):
                                    photo_url = "https://graph.org" + result2[0]["src"]
                                else:
                                    raise Exception(f"Upload failed on both providers. Response: {result}")
                
                clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"start_photo": photo_url}})
                await msg.reply(f"<b>✅ Start Photo updated successfully!\n\nURL: <code>{photo_url}</code></b>")
            except Exception as e:
                logger.error(f"Media upload error: {e}")
                await msg.reply(f"<b>❌ Upload failed: {e}\n\nPlease send a direct image URL instead.</b>")
        elif msg.text and msg.text.strip().startswith("http"):
            clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"start_photo": msg.text.strip()}})
            await msg.reply("<b>✅ Start Photo URL updated successfully!</b>")
        else:
            return await msg.reply("<b>❌ Invalid input. Please upload a photo or send an http/https URL.</b>")
            
        query.data = f"startmsg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("cdeltime_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Please send the new Auto-Delete time in minutes (integer).\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        try:
            time = int(msg.text.strip())
            clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"auto_delete_time": time}})
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
        
        text = f"<b><u>Force Subscribe Management</u></b>\n\n"
        if channels:
            text += "<b>Current Channels:</b>\n"
            for i, c in enumerate(channels, 1):
                title = channel_names.get(str(c), str(c))
                text += f"{i}. <code>{title}</code>\n"
        else:
            text += "<i>No channels added yet.</i>\n"
        
        text += f"\n<b>Current Mode:</b> <code>{mode.upper()}</code>"
        
        buttons = [
            [InlineKeyboardButton("➕ Add Channel", callback_data=f"add_fsub_{bot_id}"), InlineKeyboardButton("🧹 Clear All", callback_data=f"clear_fsub_{bot_id}")],
            [InlineKeyboardButton(f"Switch to {'JOIN REQ' if mode=='normal' else 'NORMAL'} Mode", callback_data=f"mode_fsub_{bot_id}")],
            [InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]
        ]
        await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

    elif query.data.startswith("add_fsub_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        if len(bot.get("force_sub_channels", [])) >= 6:
            return await query.answer("Max 6 channels allowed!", show_alert=True)
            
        msg = await client.ask(query.message.chat.id, "<b>Please forward a message from the channel you want to add as Force Sub.\n\nMake sure your clone bot is ADMIN in that channel!</b>")
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
            
            clone_mongo_db.bots.update_one(
                {"bot_id": bot_id}, 
                {
                    "$push": {"force_sub_channels": f_chat_id},
                    "$set": {f"channel_names.{f_chat_id}": f_chat_title}
                }
            )
            await msg.reply(f"<b>✅ Channel '{f_chat_title}' added successfully!</b>")
        else:
            await msg.reply("<b>❌ Please forward a message from a channel.</b>")
        query.data = f"forcesub_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("clear_fsub_"):
        bot_id = int(query.data.split("_")[-1])
        clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"force_sub_channels": []}})
        await query.answer("All channels cleared!")
        query.data = f"forcesub_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("mode_fsub_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        new_mode = "joinreq" if bot.get("force_sub_mode", "normal") == "normal" else "normal"
        clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"force_sub_mode": new_mode}})
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
            clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$addToSet": {"moderators": mod_id}})
            await msg.reply(f"<b>✅ User <code>{mod_id}</code> added as moderator!</b>")
        except:
            await msg.reply("<b>❌ Invalid User ID. Please send a number.</b>")
        query.data = f"mods_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("clear_mod_"):
        bot_id = int(query.data.split("_")[-1])
        clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"moderators": []}})
        await query.answer("All moderators cleared!")
        query.data = f"mods_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("nofwd_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        is_nofwd = bot.get("no_forward", False)
        new_status = not is_nofwd
        clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"no_forward": new_status}})
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
        token_mode = bot.get("token_verify", False)
        status_txt = "Enabled ✅" if token_mode else "Disabled ❌"
        
        domain = bot.get("shortener_site", "None")
        api = bot.get("shortener_api", "None")
        validity = bot.get("token_timeout", 86400) // 3600
        tutorial = bot.get("token_tutorial", "None")
        
        buttons = [
            [InlineKeyboardButton("Shorteners", callback_data=f"tok_api_{bot_id}"), InlineKeyboardButton("Validity", callback_data=f"tok_val_{bot_id}"), InlineKeyboardButton("Tutorial", callback_data=f"tok_tut_{bot_id}")],
            [InlineKeyboardButton(f"{'Disable ❌' if token_mode else 'Enable ✅'} Token", callback_data=f"token_{bot_id}"), InlineKeyboardButton("🧹 Clear Settings", callback_data=f"tok_clr_{bot_id}")],
            [InlineKeyboardButton("🔙 Back", callback_data=f"cust_{bot_id}")]
        ]
        
        text = (
            f"<b><u>Access Token</u></b>\n\n"
            f"Users need to pass a shortened link to gain special access to messages from all clone shareable links. This access will be valid for the next custom validity period.\n\n"
            f"<b>- Status:</b> {status_txt}\n"
            f"<b>- Domain:</b> <code>{domain}</code>\n"
            f"<b>- API Key:</b> <code>{api}</code>\n"
            f"<b>- Validity:</b> {validity} hours\n"
            f"<b>- Tutorial:</b> {tutorial}"
        )
        
        await query.message.edit_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

    elif query.data.startswith("token_"):
        bot_id = int(query.data.split("_")[-1])
        bot = await clone_mongo_db.bots.find_one({"bot_id": bot_id})
        token_mode = bot.get("token_verify", False)
        new_status = not token_mode
        clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"token_verify": new_status}})
        await query.answer(f"Access Token {'Enabled' if new_status else 'Disabled'}", show_alert=True)
        query.data = f"tokencfg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("tok_val_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Send the token validity time in HOURS (e.g. 24).\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        try:
            val = int(msg.text.strip())
            clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"token_timeout": val * 3600}})
            await msg.reply(f"<b>✅ Token Validity set to {val} hours!</b>")
        except:
            await msg.reply("<b>❌ Invalid time. Must be a number.</b>")
        query.data = f"tokencfg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("tok_api_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Send your Shortener Base Site and API Key separated by space.\nFormat: <code>domain.com api_key</code>\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        try:
            site, api = msg.text.strip().split(" ", 1)
            clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"shortener_site": site, "shortener_api": api}})
            await msg.reply(f"<b>✅ Shortener configured to {site}!</b>")
        except:
            await msg.reply("<b>❌ Invalid format. Make sure you sent Domain and API Key separated by a space.</b>")
        query.data = f"tokencfg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("tok_tut_"):
        bot_id = int(query.data.split("_")[-1])
        msg = await client.ask(query.message.chat.id, "<b>Send the Tutorial Link URL for how to bypass your shortener.\n\n/cancel to skip.</b>")
        if msg.text == "/cancel": return await msg.reply("Cancelled.")
        clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"token_tutorial": msg.text.strip()}})
        await msg.reply(f"<b>✅ Tutorial link updated!</b>")
        query.data = f"tokencfg_{bot_id}"
        return await cb_handler(client, query)

    elif query.data.startswith("tok_clr_"):
        bot_id = int(query.data.split("_")[-1])
        clone_mongo_db.bots.update_one(
            {"bot_id": bot_id},
            {"$set": {
                "shortener_site": "None",
                "shortener_api": "None",
                "token_tutorial": "None",
                "token_timeout": 86400,
                "token_verify": False
            }}
        )
        await query.answer("All Token settings cleared and disabled!", show_alert=True)
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
        clone_mongo_db.bots.update_one({"bot_id": bot_id}, {"$set": {"bot_mode": mode}})
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
            from pyrogram import Client as PyroClient
            # Stop existing client if running, then restart
            bot_token = bot["token"]
            vj = PyroClient(
                f"clone_{bot_token[:10]}",
                API_ID, API_HASH,
                bot_token=bot_token,
                plugins={"root": "clone_plugins"},
                in_memory=True
            )
            await vj.start()
            await query.answer(f"✅ @{bot['username']} restarted!", show_alert=True)
        except Exception as e:
            await query.answer(f"❌ Restart failed: {str(e)[:100]}", show_alert=True)
        buttons = [[InlineKeyboardButton("🔙 back", callback_data=f"cust_{bot_id}")]]
        await query.message.edit_text(
            text=f"<b>Restart triggered for @{bot.get('username', 'bot')}.\n\nNote: If the bot was already running, it will continue. If stopped, it has been restarted.</b>",
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
        config.TMA_MODE = not config.TMA_MODE
        await query.answer(f"TMA Ads {'Enabled 🟢' if config.TMA_MODE else 'Disabled 🔴'}", show_alert=True)
        query.data = "settings"
        return await cb_handler(client, query)

    elif query.data == "settings":
        user_id = query.from_user.id
        user = await get_user(user_id)
        tma_status = "Enabled 🟢" if config.TMA_MODE else "Disabled 🔴"
        buttons = [[
            InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ', callback_data='set_api'),
            InlineKeyboardButton('sᴇᴛ ʙᴀsᴇ sɪᴛᴇ', callback_data='set_site')
        ],[
            InlineKeyboardButton('💬 ᴄʜᴀᴛʙᴏx', url='https://t.me/+cFO-dJGWlCMzNGRl'),
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
        ],[
            InlineKeyboardButton(f"TMA Ads: {'ON 🟢' if config.TMA_MODE else 'OFF 🔴'}", callback_data="toggle_tma")
        ],[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ],[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴄᴜʀʀᴇɴᴛ ʙᴀsᴇ sɪᴛᴇ: {user['base_site']}\nᴄᴜʀʀᴇɴᴛ ᴀᴘɪ: <code>{user['shortener_api']}</code>\nᴛᴍᴀ ᴀᴅs: <code>{tma_status}</code></b>",
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
