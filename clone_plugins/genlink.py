# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

from pyrogram import filters, Client, enums
from clone_plugins.users_api import get_user, get_short_link
from utils import is_subscribed_universal
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import base64

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command(['link']))
async def gen_link_s(client: Client, message):
    from plugins.clone import mongo_db
    me = await client.get_me()
    bot_doc = mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    # Universal Force Sub Check for Clones
    chk = await is_subscribed_universal(client, message)
    if chk == "kicked":
        return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
    if type(chk) == list:
        buttons = []
        for i, channel_id in enumerate(chk, start=1):
            try:
                chat = await client.get_chat(channel_id)
                buttons.append([InlineKeyboardButton("ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link or f"https://t.me/{chat.username}")])
            except: continue
        buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{(await client.get_me()).username}?start=true")])
        return await message.reply_text(
            text="<b>ʜᴇʏ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    replied = message.reply_to_message
    if not replied:
        return await message.reply('<b>Reply to a media file to get a shareable link.</b>')

    file_type = replied.media
    import uuid
    from plugins.clone import mongo_db
    from config import LOG_CHANNEL
    
    # Attempt to forward to the log channel if the user made the clone bot an admin
    try:
        await replied.forward(LOG_CHANNEL)
    except Exception:
        pass # Silently ignore if clone bot is not an admin
    
    media = getattr(replied, file_type.value)
    file_id = media.file_id
    
    # Generate a short unique ID (8 chars is enough and safely fits within 64 byte limit)
    short_id = str(uuid.uuid4())[:8]
    bot_username = (await client.get_me()).username
    
    # Store in DB so we can retrieve the massive file_id later
    mongo_db.clone_files.insert_one({
        "_id": short_id,
        "bot_username": bot_username,
        "file_id": file_id
    })

    string = 'file_' + short_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

    user_id = message.from_user.id
    user = await get_user(user_id)

    # Link points to the clone bot itself, using the short_id
    share_link = f"https://t.me/{bot_username}?start={outstr}"

    if user["base_site"] and user["shortener_api"]:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")


# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
