# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

from pyrogram import filters, Client, enums
from clone_plugins.users_api import get_user, get_short_link
from TechVJ.bot import StreamBot
from utils import is_subscribed_universal
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import base64
import uuid
import json
import os
import re

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command(['link']))
async def gen_link_s(client: Client, message):
    from plugins.clone import mongo_db
    me = await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    # Bot Mode Check (Public/Private)
    bot_mode = bot_doc.get("bot_mode", "public") if bot_doc else "public"
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if bot_mode == "private" and message.from_user.id != owner_id and message.from_user.id not in mods:
        return await message.reply("<b>❌ This bot is in Private Mode. Only the bot owner and moderators can generate links!</b>")

    # Universal Force Sub Check
    chk_u = await is_subscribed_universal(client, message)
    if chk_u == "kicked":
        return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
    
    if type(chk_u) == list:
        buttons = []
        for channel_id in chk_u:
            try:
                chat = await client.get_chat(channel_id)
                buttons.append([InlineKeyboardButton("ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link or f"https://t.me/{chat.username}")])
            except: continue
        buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=true")])
        return await message.reply_text(
            text="<b>ʜᴇʏ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # Clone-specific Force Sub Check
    clone_force_channels = bot_doc.get('force_sub_channels', []) if bot_doc else []
    if clone_force_channels:
        not_joined = []
        for ch_id in clone_force_channels:
            try:
                member = await client.get_chat_member(ch_id, message.from_user.id)
                if member.status == enums.ChatMemberStatus.BANNED:
                    return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs!</b>")
                if member.status == enums.ChatMemberStatus.LEFT:
                    not_joined.append(ch_id)
            except:
                not_joined.append(ch_id)
        
        if not_joined:
            buttons = []
            for i, ch_id in enumerate(not_joined, 1):
                try:
                    chat = await client.get_chat(ch_id)
                    buttons.append([InlineKeyboardButton(f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {i}", url=chat.invite_link or f"https://t.me/{chat.username}")])
                except: pass
            buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=true")])
            return await message.reply_text(
                text="<b>ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋs!</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    replied = message.reply_to_message
    if not replied:
        return await message.reply('<b>Reply to a media file to get a shareable link.</b>')

    file_type = replied.media
    media = getattr(replied, file_type.value)
    file_id = media.file_id
    
    # Generate a short unique ID (8 chars is enough)
    short_id = str(uuid.uuid4())[:8]
    bot_username = me.username
    
    # Store in DB
    await mongo_db.clone_files.insert_one({
        "_id": short_id,
        "bot_username": bot_username,
        "file_id": file_id
    })

    string = 'file_' + short_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")

    user_id = message.from_user.id
    user = await get_user(me.id, user_id)

    # Link points to the clone bot itself, using the short_id
    share_link = f"https://t.me/{bot_username}?start={outstr}"

    if user["base_site"] and user["shortener_api"]:
        short_link = await get_short_link(user, share_link)
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
    else:
        await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")


@Client.on_message(filters.command(['batch']) & filters.private)
async def gen_link_batch(client: Client, message):
    from plugins.clone import mongo_db
    from config import LOG_CHANNEL
    
    me = await client.get_me()
    bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
    if bot_doc and bot_doc.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    # Bot Mode Check (Public/Private)
    bot_mode = bot_doc.get("bot_mode", "public") if bot_doc else "public"
    owner_id = int(bot_doc.get("user_id", 0)) if bot_doc else 0
    mods = bot_doc.get("moderators", []) if bot_doc else []
    
    if bot_mode == "private" and message.from_user.id != owner_id and message.from_user.id not in mods:
        return await message.reply("<b>❌ This bot is in Private Mode. Only the bot owner and moderators can generate links!</b>")

    # Universal Force Sub Check
    chk_u = await is_subscribed_universal(client, message)
    if chk_u == "kicked":
        return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴇ!</b>")
    
    if type(chk_u) == list:
        buttons = []
        for channel_id in chk_u:
            try:
                chat = await client.get_chat(channel_id)
                buttons.append([InlineKeyboardButton("ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link or f"https://t.me/{chat.username}")])
            except: continue
        buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=true")])
        return await message.reply_text(
            text="<b>ʜᴇʏ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # Clone-specific Force Sub Check
    clone_force_channels = bot_doc.get('force_sub_channels', []) if bot_doc else []
    if clone_force_channels:
        not_joined = []
        for ch_id in clone_force_channels:
            try:
                member = await client.get_chat_member(ch_id, message.from_user.id)
                if member.status == enums.ChatMemberStatus.BANNED:
                    return await message.reply_text("<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs!</b>")
                if member.status == enums.ChatMemberStatus.LEFT:
                    not_joined.append(ch_id)
            except:
                not_joined.append(ch_id)
        
        if not_joined:
            buttons = []
            for i, ch_id in enumerate(not_joined, 1):
                try:
                    chat = await client.get_chat(ch_id)
                    buttons.append([InlineKeyboardButton(f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {i}", url=chat.invite_link or f"https://t.me/{chat.username}")])
                except: pass
            buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=true")])
            return await message.reply_text(
                text="<b>ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋs!</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    # Interactive Batch Flow
    f_msg = await client.ask(message.chat.id, "<b>Forward the FIRST message from the channel or send the message link.\n\n/cancel to stop.</b>")
    if f_msg.text == "/cancel": return await f_msg.reply("Cancelled.")

    # Parse First Message
    regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
    if f_msg.forward_from_chat:
        f_chat_id = f_msg.forward_from_chat.id
        f_msg_id = f_msg.forward_from_message_id
    elif f_msg.text:
        match = regex.match(f_msg.text.strip())
        if not match: return await f_msg.reply("<b>Invalid link!</b>")
        f_chat_id = match.group(4)
        f_msg_id = int(match.group(5))
        if f_chat_id.isnumeric(): f_chat_id = int("-100" + f_chat_id)
    else:
        return await f_msg.reply("<b>Please forward a message or send a link!</b>")

    # Ask for Last Message
    l_msg = await client.ask(message.chat.id, "<b>Forward the LAST message from the channel or send the message link.\n\n/cancel to stop.</b>")
    if l_msg.text == "/cancel": return await l_msg.reply("Cancelled.")

    # Parse Last Message
    if l_msg.forward_from_chat:
        l_chat_id = l_msg.forward_from_chat.id
        l_msg_id = l_msg.forward_from_message_id
    elif l_msg.text:
        match = regex.match(l_msg.text.strip())
        if not match: return await l_msg.reply("<b>Invalid link!</b>")
        l_chat_id = match.group(4)
        l_msg_id = int(match.group(5))
        if l_chat_id.isnumeric(): l_chat_id = int("-100" + l_chat_id)
    else:
        return await l_msg.reply("<b>Please forward a message or send a link!</b>")

    if f_chat_id != l_chat_id:
        return await l_msg.reply("<b>Chat IDs do not match! Both messages must be from the same channel.</b>")

    try:
        chat_id = (await client.get_chat(f_chat_id)).id
    except Exception as e:
        return await l_msg.reply(f"<b>Error: {e}\nMake sure I am admin in that channel.</b>")

    sts = await l_msg.reply("**ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪɴᴋ ғᴏʀ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ**.\n**ᴛʜɪs ᴍᴀʏ ᴛᴀᴋᴇ ᴛɪᴍᴇ ᴅᴇᴘᴇɴᴅɪɴɢ ᴜᴘᴏɴ ɴᴜᴍʙᴇʀ ᴏғ ᴍᴇssᴀɢᴇs**")
    FRMT = "**ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪɴᴋ...**\n**ᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs:** {total}\n**ᴅᴏɴᴇ:** {current}\n**ʀᴇᴍᴀɪɴɪɴɢ:** {rem}\n**sᴛᴀᴛᴜs:** {sts}"

    outlist = []
    tot = 0
    total_count = l_msg_id - f_msg_id + 1
    
    for m_id in range(f_msg_id, l_msg_id + 1):
        tot += 1
        if tot % 10 == 0:
            try: await sts.edit(FRMT.format(total=total_count, current=tot, rem=(total_count - tot), sts="Fetching Messages"))
            except: pass
        
        try:
            msg = await client.get_messages(f_chat_id, m_id)
            if msg.empty or msg.service:
                continue
            outlist.append({"channel_id": f_chat_id, "msg_id": msg.id})
        except:
            continue

    if not outlist:
        return await sts.edit("<b>❌ No valid messages found in that range!</b>")

    # Use LOG_CHANNEL to store the batch JSON
    temp_file = f"batchmode_clone_{message.from_user.id}.json"
    with open(temp_file, "w+") as out:
        json.dump(outlist, out)
    
    # Use Main Bot (StreamBot) to send document
    post = await StreamBot.send_document(LOG_CHANNEL, temp_file, file_name="Batch.json", caption="⚠️ Clone Batch Generated.")
    os.remove(temp_file)
    
    string = str(post.id)
    outstr = "BATCH-" + base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    
    bot_username = me.username
    share_link = f"https://t.me/{bot_username}?start={outstr}"
    
    user_id = message.from_user.id
    user = await get_user(me.id, user_id)
    if user["base_site"] and user["shortener_api"]:
        short_link = await get_short_link(user, share_link)
        await sts.edit(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
    else:
        await sts.edit(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
