# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

from pyrogram import filters, Client, enums
from clone_plugins.users_api import get_user, get_short_link
from utils import is_subscribed_universal
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LOG_CHANNEL
import base64

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command(['link']))
async def gen_link_s(client: Client, message):
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
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await message.reply("<b>Reply to a supported media file (video, audio, or document).</b>")

    # Copy the file to LOG_CHANNEL to get a stable message ID for the link
    try:
        post = await replied.copy(LOG_CHANNEL)
    except Exception as e:
        return await message.reply(f"<b>❌ Failed to store file. Make sure the bot is admin in LOG_CHANNEL.\n\nError: {e}</b>")

    file_id = str(post.id)
    string = 'file_' + file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

    user_id = message.from_user.id
    user = await get_user(user_id)
    bot_username = (await client.get_me()).username
    share_link = f"https://t.me/{bot_username}?start={outstr}"

    if user["base_site"] and user["shortener_api"]:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")


# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
