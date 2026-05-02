# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import re
from pymongo import MongoClient
from Script import script
from pyrogram import Client, filters
from pyrogram.types import Message, BotCommand
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from config import API_ID, API_HASH, DB_URI, DB_NAME, CLONE_MODE, UNIVERSAL_FORCE_SUB_CHANNEL
from utils import is_subscribed_universal
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

mongo_client = MongoClient(DB_URI)
mongo_db = mongo_client["cloned_vjbotz"]

@Client.on_message(filters.command("clone") & filters.private)
async def clone(client, message):
    if CLONE_MODE == False:
        return 
    
    # Universal Force Sub Check
    chk = await is_subscribed_universal(client, message)
    if chk == "kicked":
        return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
    if isinstance(chk, list):
        buttons = []
        for i, channel_id in enumerate(chk, start=1):
            try:
                chat = await client.get_chat(channel_id)
                btn = [InlineKeyboardButton(f"ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link or f"https://t.me/{chat.username}")]
                buttons.append(btn)
            except: continue
        buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{(await client.get_me()).username}?start=clone")])
        return await message.reply_text(
            text="<b>ʜᴇʏ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜɴɪᴠᴇʀsᴀʟ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴀ ᴄʜᴀɴɴᴇʟ ʙᴏᴛ!</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    techvj = await client.ask(message.chat.id, "<b>1) sᴇɴᴅ <code>/newbot</code> ᴛᴏ @BotFather\n2) ɢɪᴠᴇ ᴀ ɴᴀᴍᴇ ꜰᴏʀ ʏᴏᴜʀ ʙᴏᴛ.\n3) ɢɪᴠᴇ ᴀ ᴜɴɪǫᴜᴇ ᴜsᴇʀɴᴀᴍᴇ.\n4) ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ.\n5) ꜰᴏʀᴡᴀʀᴅ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss.</b>")
    if techvj.text == '/cancel':
        await techvj.delete()
        return await message.reply('<b>ᴄᴀɴᴄᴇʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss 🚫</b>')
    # Try to extract bot token from forwarded BotFather message or directly pasted text
    try:
        bot_token = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", techvj.text)[0]
    except:
        return await message.reply('<b>ɴᴏ ᴠᴀʟɪᴅ ʙᴏᴛ ᴛᴏᴋᴇɴ ғᴏᴜɴᴅ 😕\nᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ғʀᴏᴍ @BotFather ᴏʀ ᴘᴀsᴛᴇ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ ᴅɪʀᴇᴄᴛʟʏ.</b>')
    user_id = message.from_user.id
    msg = await message.reply_text("**👨‍💻 ᴡᴀɪᴛ ᴀ ᴍɪɴᴜᴛᴇ ɪ ᴀᴍ ᴄʀᴇᴀᴛɪɴɢ ʏᴏᴜʀ ʙᴏᴛ ❣️**")
    try:
        vj = Client(
            f"clone_{bot_token[:10]}", API_ID, API_HASH,
            bot_token=bot_token,
            plugins={"root": "clone_plugins"},
            in_memory=True
        )
        await vj.start()
        bot = await vj.get_me()
        # Set bot commands so they appear in Telegram menu
        try:
            await vj.set_bot_commands([
                BotCommand("start", "Start the bot"),
                BotCommand("link", "Reply to a file to get a shareable link"),
                BotCommand("setting", "Manage your bot settings"),
                BotCommand("api", "Set your shortener API key"),
                BotCommand("base_site", "Set your shortener base site"),
                BotCommand("setcaption", "Set your custom file name prefix"),
            ])
        except: pass
        details = {
            'bot_id': bot.id,
            'is_bot': True,
            'user_id': user_id,
            'name': bot.first_name,
            'token': bot_token,
            'username': bot.username,
            'force_sub_channels': []
        }
        mongo_db.bots.insert_one(details)
        await msg.edit_text(
            f"<b>✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʟᴏɴᴇᴅ ʏᴏᴜʀ ʙᴏᴛ: @{bot.username}\n\n"
            f"📋 <b>Commands set automatically!</b>\n\n"
            f"📢 <b>To add force subscribe channels, go to the main bot and use /setforcesub</b></b>"
        )
    except BaseException as e:
        await msg.edit_text(f"⚠️ <b>Bot Error:</b>\n\n<code>{e}</code>\n\n**Kindly forward this message to @Brainaxe190 to get assistance.**")

@Client.on_message(filters.command("deletecloned") & filters.private)
async def delete_cloned_bot(client, message):
    if CLONE_MODE == False:
        return 
    try:
        techvj = await client.ask(message.chat.id, "**Send Me Bot Token To Delete**")
        bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', techvj.text, re.IGNORECASE)
        bot_token = bot_token[0] if bot_token else None
        bot_id = re.findall(r'\d[0-9]{8,10}', techvj.text)
        cloned_bot = mongo_db.bots.find_one({"token": bot_token})
        if cloned_bot:
            mongo_db.bots.delete_one({"token": bot_token})
            await message.reply_text("**🤖 ᴛʜᴇ ᴄʟᴏɴᴇᴅ ʙᴏᴛ ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴛʜᴇ ʟɪsᴛ ᴀɴᴅ ɪᴛs ᴅᴇᴛᴀɪʟs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ. ☠️**")
        else:
            await message.reply_text("**⚠️ ᴛʜᴇ ʙᴏᴛ ᴛᴏᴋᴇɴ ᴘʀᴏᴠɪᴅᴇᴅ ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʟᴏɴᴇᴅ ʟɪsᴛ.**")
    except:
        await message.reply_text("An error occurred while deleting the cloned bot.")

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

async def restart_bots():
    bots = list(mongo_db.bots.find())
    for bot in bots:
        bot_token = bot['token']
        try:
            vj = Client(
                f"clone_{bot_token[:10]}", API_ID, API_HASH,
                bot_token=bot_token,
                plugins={"root": "clone_plugins"},
                in_memory=True
            )
            await vj.start()
        except:
            pass
