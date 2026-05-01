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
from utils import verify_user, check_token, check_verification, get_token, is_subscribed, is_subscribed_universal
from config import *
import re
import json
import base64
from urllib.parse import quote_plus
from TechVJ.utils.file_properties import get_name, get_hash, get_media_file_size
from plugins.clone import mongo_db as clone_mongo_db
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
    chars = ["[", "]", "(", ")"]
    for c in chars:
        file_name.replace(c, "")
    file_name = '@anihubYT2 ' + ' '.join(filter(lambda x: not x.startswith('http') and not x.startswith('@') and not x.startswith('www.'), file_name.split()))
    return file_name

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ0


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        me = await client.get_me()
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
            if isinstance(chk_u, list):
                buttons = []
                for channel_id in chk_u:
                    try:
                        chat = await client.get_chat(channel_id)
                        buttons.append([InlineKeyboardButton("ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link or f"https://t.me/{chat.username}")])
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
            if isinstance(chk, list):
                buttons = []
                for i, channel_id in enumerate(chk, start=1):
                    try:
                        chat = await client.get_chat(channel_id)
                        buttons.append([InlineKeyboardButton(f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {i}", url=chat.invite_link or f"https://t.me/{chat.username}")])
                    except: continue
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
                InlineKeyboardButton('🤖 ᴄʟᴏɴᴇ', url=f'https://t.me/{me.username}?start=clone')
            ],[
                InlineKeyboardButton('💬 ᴄʜᴀᴛʙᴏx', url='https://t.me/+cFO-dJGWlCMzNGRl'),
                InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
            ],[
                InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
                InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
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
        elif data.split("-", 1)[0] == "BATCH":
            try:
                if not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
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
                await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
            return

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

        pre, decode_file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        if not await check_verification(client, message.from_user.id) and VERIFY_MODE == True:
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
                await k.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
            return
        except Exception as e:
            logger.exception(f"File Send Error: {e}")
            await message.reply_text(f"<b>⚠️ Error sending file.\n\nError:</b> <code>{e}</code>")
        
    except Exception as e:
        logger.exception(f"Start Error: {e}")
        try: await message.reply_text(f"<b>⚠️ Error occurred while processing /start command.\n\nError:</b> <code>{e}</code>")
        except: pass

@Client.on_message(filters.command("setting") & filters.private & filters.incoming)
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
    buttons = [[
        InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ', callback_data='set_api'),
        InlineKeyboardButton('sᴇᴛ ʙᴀsᴇ sɪᴛᴇ', callback_data='set_site')
    ],[
        InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴄᴜʀʀᴇɴᴛ ʙᴀsᴇ sɪᴛᴇ: {user['base_site']}\nᴄᴜʀʀᴇɴᴛ ᴀᴘɪ: <code>{user['shortener_api']}</code></b>",
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command('api') & filters.private)
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

@Client.on_message(filters.command("base_site") & filters.private)
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
    bot_doc = clone_mongo_db.bots.find_one({"user_id": user_id})
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
    clone_mongo_db.bots.update_one(
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
    bot_doc = clone_mongo_db.bots.find_one({"user_id": user_id})
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
    bot_doc = clone_mongo_db.bots.find_one({"user_id": user_id})
    if not bot_doc:
        return await message.reply_text("<b>❌ You don't have a clone bot yet.</b>")
    clone_mongo_db.bots.update_one({"user_id": user_id}, {"$set": {"force_sub_channels": []}})
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
        clone_mongo_db.bots.update_one(
            {"user_id": owner_id},
            {"$set": {"force_sub_mode": mode_value}}
        )
        bot_doc = clone_mongo_db.bots.find_one({"user_id": owner_id})
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
        me2 = (await client.get_me()).mention
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(me2),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
    
    elif query.data == "start":
        me = await client.get_me()
        buttons = [[
            InlineKeyboardButton('⚙️ sᴇᴛᴛɪɴɢs', callback_data='settings'),
            InlineKeyboardButton('🤖 ᴄʟᴏɴᴇ', url=f'https://t.me/{me.username}?start=clone')
        ],[
            InlineKeyboardButton('💬 ᴄʜᴀᴛʙᴏx', url='https://t.me/+cFO-dJGWlCMzNGRl'),
            InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/viralverse0909')
        ],[
            InlineKeyboardButton('💁‍♀️ ʜᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('😊 ᴀʙᴏᴜᴛ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        me2 = (await client.get_me()).mention
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, me2),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
    
    elif query.data == "clone":
        me = await client.get_me()
        buttons = [[
            InlineKeyboardButton('🤖 sᴛᴀʀᴛ ᴄʟᴏɴᴇ', url=f'https://t.me/{me.username}?start=clone'),
        ],[
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
            text=script.CLONE_TXT.format(query.from_user.mention),
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

    elif query.data == "settings":
        user_id = query.from_user.id
        user = await get_user(user_id)
        buttons = [[
            InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ', callback_data='set_api'),
            InlineKeyboardButton('sᴇᴛ ʙᴀsᴇ sɪᴛᴇ', callback_data='set_site')
        ],[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴄᴜʀʀᴇɴᴛ ʙᴀsᴇ sɪᴛᴇ: {user['base_site']}\nᴄᴜʀʀᴇɴᴛ ᴀᴘɪ: <code>{user['shortener_api']}</code></b>",
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
