# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import re
import motor.motor_asyncio
from Script import script
from pyrogram import Client, filters
from pyrogram.types import Message, BotCommand
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from config import API_ID, API_HASH, DB_URI, DB_NAME, CLONE_MODE, UNIVERSAL_FORCE_SUB_CHANNEL, ADMINS
from utils import is_subscribed_universal
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

# Async DB Client
async_mongo_client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
async_mongo_db = async_mongo_client["cloned_vjbotz"]

# Maintain synchronous for backward compatibility in some scripts if needed, 
# but we should move away from it.
from pymongo import MongoClient
mongo_client = MongoClient(DB_URI)
mongo_db = mongo_client["cloned_vjbotz"]

# Global registry: bot_id -> running Pyrogram Client instance
running_clones = {}

async def set_clone_commands(vj: Client):
    """Set bot commands for a clone client so they appear in the Telegram menu."""
    try:
        await vj.set_bot_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("batch", "Generate multi-file links (Interactive)"),
            BotCommand("link", "Reply to a file to get a shareable link"),
            BotCommand("broadcast", "Send a message to all bot users"),
            BotCommand("setting", "Manage your bot settings"),
            BotCommand("setcaption", "Set your custom file name prefix"),
            BotCommand("stats", "View bot statistics"),
            BotCommand("plan", "View VIP status / prices"),
            BotCommand("validity", "View active user verifications"),
            BotCommand("post", "Post a message or media to a channel"),
            BotCommand("editpost", "Edit a post in a channel"),
            BotCommand("delpost", "Delete a post from a channel"),
        ])
    except Exception as e:
        logger.error(f"Error setting bot commands for clone: {e}")

async def stop_clone(bot_id: int):
    """Stop a running clone client by bot_id."""
    vj = running_clones.pop(bot_id, None)
    if vj:
        try:
            await vj.stop()
        except Exception:
            pass

@Client.on_message(filters.command("clone") & filters.private)
async def clone(client, message):
    if CLONE_MODE == False:
        return 
    
    if message.from_user.id not in ADMINS:
        return await message.reply_text("<b>❌ Only the bot owner can create cloned bots.</b>")
    
    # Universal Force Sub Check
    chk = await is_subscribed_universal(client, message)
    if chk == "kicked":
        return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
    if isinstance(chk, list):
        buttons = []
        for channel_id in chk:
            try:
                chat = await client.get_chat(channel_id)
                btn = [InlineKeyboardButton(f"ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link or f"https://t.me/{chat.username}")]
                buttons.append(btn)
            except: continue
        me = client.me or await client.get_me()
        buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=clone")])
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
        # Track the running instance
        running_clones[bot.id] = vj
        # Set bot commands so they appear in Telegram menu
        await set_clone_commands(vj)
        details = {
            'bot_id': bot.id,
            'is_bot': True,
            'user_id': user_id,
            'name': bot.first_name,
            'token': bot_token,
            'username': bot.username,
            'force_sub_channels': [],
            'force_sub_mode': 'normal'
        }
        await async_mongo_db.bots.insert_one(details)
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
    
    if message.from_user.id not in ADMINS:
        return await message.reply_text("<b>❌ Only the bot owner can delete cloned bots.</b>")
        
    try:
        techvj = await client.ask(message.chat.id, "**Send Me Bot Token To Delete**")
        bot_token_find = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", techvj.text)
        bot_token = bot_token_find[0] if bot_token_find else None
        
        if not bot_token:
             return await message.reply_text("**⚠️ Invalid Bot Token.**")

        cloned_bot = await async_mongo_db.bots.find_one({"token": bot_token})
        if cloned_bot:
            bot_id = cloned_bot['bot_id']
            await stop_clone(int(bot_id))
            await async_mongo_db.bots.delete_one({"token": bot_token})
            # Also clean up users collection for this bot
            try:
                await async_mongo_db[str(bot_id)].drop()
            except: pass
            await message.reply_text("**🤖 ᴛʜᴇ ᴄʟᴏɴᴇᴅ ʙᴏᴛ ʜᴀs ʙᴇᴇɴ sᴛᴏᴘᴘᴇᴅ ᴀɴᴅ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ. ☠️**")
        else:
            await message.reply_text("**⚠️ ᴛʜᴇ ʙᴏᴛ ᴛᴏᴋᴇɴ ᴘʀᴏᴠɪᴅᴇᴅ ɪs ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʟᴏɴᴇᴅ ʟɪsᴛ.**")
    except Exception as e:
        logger.error(f"Error deleting bot: {e}")
        await message.reply_text("An error occurred while deleting the cloned bot.")

@Client.on_message(filters.command("purgeotherclones") & filters.private)
async def purge_other_clones(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply_text("<b>❌ Only the main bot owner can run this command.</b>")
    
    msg = await message.reply_text("<b>🧹 Purging all cloned bots created by other users... Please wait.</b>")
    purged_count = 0
    
    try:
        cursor = async_mongo_db.bots.find()
        async for bot in cursor:
            owner_id = bot.get("user_id")
            if owner_id not in ADMINS:
                bot_id = bot['bot_id']
                # Stop the running bot instance
                await stop_clone(int(bot_id))
                # Remove from DB
                await async_mongo_db.bots.delete_one({"bot_id": bot_id})
                # Drop users collection for this clone
                try:
                    await async_mongo_db[str(bot_id)].drop()
                except:
                    pass
                purged_count += 1
        
        await msg.edit_text(f"<b>✅ Successfully purged <code>{purged_count}</code> clone bots belonging to other users.</b>")
    except Exception as e:
        logger.error(f"Error purging other clones: {e}")
        await msg.edit_text(f"<b>❌ Error purging clones: <code>{e}</code></b>")

async def restart_bots():
    cursor = async_mongo_db.bots.find()
    async for bot in cursor:
        bot_token = bot.get('token')
        if not bot_token:
            continue
        bot_id = bot.get('bot_id')
        if not bot_id:
            continue
        # Stop and remove any stale running instance first to avoid duplicate handlers
        if bot_id in running_clones:
            await stop_clone(bot_id)
        try:
            vj = Client(
                f"clone_{bot_token[:10]}", API_ID, API_HASH,
                bot_token=bot_token,
                plugins={"root": "clone_plugins"},
                in_memory=True
            )
            await vj.start()
            # Set bot commands so they appear in Telegram menu
            await set_clone_commands(vj)
            running_clones[bot_id] = vj
        except Exception as startup_err:
            err_str = str(startup_err)
            if "ACCESS_TOKEN_EXPIRED" in err_str or "token has expired" in err_str:
                logger.warning(f"Clone bot {bot_id} token has expired. Removing from MongoDB...")
                await async_mongo_db.bots.delete_one({"bot_id": bot_id})
            else:
                logger.error(f"Error starting clone bot {bot_id}: {startup_err}")
