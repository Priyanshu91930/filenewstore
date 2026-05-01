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
from plugins.clone import mongo_db
from pyrogram.errors import ChatAdminRequired, FloodWait
from config import BOT_USERNAME, ADMINS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, InputMediaPhoto
from config import PICS, CUSTOM_FILE_CAPTION, AUTO_DELETE_TIME, AUTO_DELETE, UNIVERSAL_FORCE_SUB_CHANNEL
from utils import is_subscribed_universal
import re
import json
import base64

logger = logging.getLogger(__name__)

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
    me = await client.get_me()
    if not await clonedb.is_user_exist(me.id, message.from_user.id):
        await clonedb.add_user(me.id, message.from_user.id)
    
    # Universal Force Sub Check for Clones
    chk = await is_subscribed_universal(client, message)
    if chk == "kicked":
        await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
        return
    if isinstance(chk, list):
        buttons = []
        for i, channel_id in enumerate(chk, start=1):
            try:
                chat = await client.get_chat(channel_id)
                btn = [InlineKeyboardButton(f"ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link or f"https://t.me/{chat.username}")]
                buttons.append(btn)
            except: continue
        buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=true")])
        return await message.reply_text(
            text="<b>ʜᴇʏ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    if len(message.command) != 2 or message.command[1] == "true":
        buttons = [[
            InlineKeyboardButton('⚙️ sᴇᴛᴛɪɴɢs', callback_data='settings'),
            InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ᴄʟᴏɴᴇ', url=f'https://t.me/{BOT_USERNAME}?start=clone')
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
                caption=script.CLONE_START_TXT.format(message.from_user.mention, me.mention),
                reply_markup=reply_markup
            )
        except Exception as e:
            await message.reply_text(
                text=script.CLONE_START_TXT.format(message.from_user.mention, me.mention),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        return

@Client.on_message(filters.command("setting") & filters.private & filters.incoming)
async def settings_command(client, message):
    # Force Subscribe Check
    chk_u = await is_subscribed_universal(client, message)
    if chk_u == "kicked" or isinstance(chk_u, list):
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
    
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""   

    pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
    # Get owner's caption prefix from DB
    me = await client.get_me()
    bot_owner = mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(bot_owner['user_id']) if bot_owner else None
    caption_prefix = ""
    if owner_id:
        owner_data = await get_user(owner_id)
        caption_prefix = owner_data.get("caption_prefix", "").strip()

    try:
        msg = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            protect_content=True if pre == 'filep' else False,
        )
        filetype = msg.media
        file = getattr(msg, filetype.value)
        # Build title: strip existing @mentions/URLs, then prepend owner's prefix
        clean_name = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('http') and not x.startswith('www.'), file.file_name.split()))
        title = (caption_prefix + ' ' + clean_name).strip() if caption_prefix else clean_name
        size=get_size(file.file_size)
        f_caption = f"<code>{title}</code>"
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
            except:
                return
        await msg.edit_caption(f_caption)
        k = await msg.reply(f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>{AUTO_DELETE} mins</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</i></b>",quote=True)
        await asyncio.sleep(AUTO_DELETE_TIME)
        await msg.delete()
        await k.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
        return
    except:
        pass
        
# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command('setcaption') & filters.private)
async def set_caption_handler(client, m: Message):
    """Allow clone bot owner to set a custom prefix added to all file names.
    Usage: /setcaption @MyChannel
    To remove: /setcaption off
    """
    me = await client.get_me()
    bot_owner = mongo_db.bots.find_one({'bot_id': me.id})
    if not bot_owner or int(bot_owner['user_id']) != m.from_user.id:
        return await m.reply("<b>❌ Only the bot owner can use this command.</b>")

    cmd = m.command
    if len(cmd) == 1:
        user = await get_user(m.from_user.id)
        current = user.get("caption_prefix", "") or "<i>Not set</i>"
        return await m.reply(
            f"<b>📝 Caption Prefix</b>\n\n"
            f"Current prefix: <code>{current}</code>\n\n"
            f"<b>Usage:</b> <code>/setcaption @YourName</code>\n"
            f"<b>To remove:</b> <code>/setcaption off</code>"
        )
    prefix = cmd[1].strip()
    if prefix.lower() == "off":
        await update_user_info(m.from_user.id, {"caption_prefix": ""})
        return await m.reply("<b>✅ Caption prefix removed. Files will be sent without a prefix.</b>")
    await update_user_info(m.from_user.id, {"caption_prefix": prefix})
    await m.reply(f"<b>✅ Caption prefix set to:</b> <code>{prefix}</code>\n\nAll files sent by your bot will now start with this name.")

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
        await m.reply("Shortener API updated successfully to " + api)
    else:
        await m.reply("You are not authorized to use this command.")

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command("base_site") & filters.private)
async def base_site_handler(client, m: Message):
    user_id = m.from_user.id
    user = await get_user(user_id)
    cmd = m.command
    text = f"/base_site (base_site)\n\nCurrent base site: None\n\n EX: /base_site shortnerdomain.com\n\nIf You Want To Remove Base Site Then Copy This And Send To Bot - `/base_site None`"
    
    if len(cmd) == 1:
        return await m.reply(text=text, disable_web_page_preview=True)
    elif len(cmd) == 2:
        base_site = cmd[1].strip()
        if not domain(base_site):
            return await m.reply(text=text, disable_web_page_preview=True)
        await update_user_info(user_id, {"base_site": base_site})
        await m.reply("Base Site updated successfully")
    else:
        await m.reply("You are not authorized to use this command.")

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    me = await client.get_me()
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('⚙️ sᴇᴛᴛɪɴɢs', callback_data='settings'),
            InlineKeyboardButton('🤖 ᴄʀᴇᴀᴛᴇ ᴄʟᴏɴᴇ', url=f'https://t.me/{BOT_USERNAME}?start=clone')
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
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
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
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        owner = mongo_db.bots.find_one({'bot_id': me.id})
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
        user = await get_user(user_id)
        prefix = user.get("caption_prefix", "") or "<i>Not set</i>"
        buttons = [[
            InlineKeyboardButton('sᴇᴛ sʜᴏʀᴛɴᴇʀ ᴀᴘɪ', callback_data='set_api'),
            InlineKeyboardButton('sᴇᴛ ʙᴀsᴇ sɪᴛᴇ', callback_data='set_site')
        ],[
            InlineKeyboardButton('📝 sᴇᴛ ᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx', callback_data='set_caption')
        ],[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=f"<b>⚙️ sᴇᴛᴛɪɴɢs ᴘᴀɴᴇʟ\n\nᴄᴜʀʀᴇɴᴛ ʙᴀsᴇ sɪᴛᴇ: {user['base_site']}\nᴄᴜʀʀᴇɴᴛ ᴀᴘɪ: <code>{user['shortener_api']}</code>\nᴄᴀᴘᴛɪᴏɴ ᴘʀᴇꜰɪx: {prefix}</b>",
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
