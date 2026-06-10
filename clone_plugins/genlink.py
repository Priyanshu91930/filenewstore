# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import asyncio
import logging
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

logger = logging.getLogger(__name__)

# ─── Custom ask() helper (no pyromod needed, works with pyrofork) ───────────
# Stores pending futures: {(client_id, chat_id): asyncio.Future}
_pending_asks = {}

@Client.on_message(filters.private & filters.incoming & ~filters.command(
    ["start","batch","link","setting","setcaption","api","base_site","stats","broadcast","shortner_api","shortner_domain","validity","plan","addvip","delvip"]
))
async def _ask_listener(client: Client, message):
    """Intercepts the next private message for any active ask() session."""
    key = (id(client), message.chat.id)
    future = _pending_asks.get(key)
    if future and not future.done():
        logger.debug(f"[ask_listener] Resolving future for key={key}")
        future.set_result(message)
        raise StopPropagation  # don't let other handlers fire

async def _ask(client: Client, chat_id: int, text: str, timeout: int = 120):
    """Send a question and wait for the user's next message."""
    logger.debug(f"[_ask] Sending prompt to chat_id={chat_id}")
    await client.send_message(chat_id, text, parse_mode=enums.ParseMode.HTML)
    key = (id(client), chat_id)
    loop = asyncio.get_event_loop()
    future = loop.create_future()
    _pending_asks[key] = future
    try:
        result = await asyncio.wait_for(future, timeout=timeout)
        logger.debug(f"[_ask] Got response from chat_id={chat_id}")
        return result
    except asyncio.TimeoutError:
        logger.warning(f"[_ask] Timed out waiting for response from chat_id={chat_id}")
        raise
    finally:
        _pending_asks.pop(key, None)
# ─────────────────────────────────────────────────────────────────────────────

try:
    from pyrogram.handlers.handler import StopPropagation
except ImportError:
    from pyrogram import StopPropagation


# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

@Client.on_message(filters.command(['link']) & filters.private & filters.incoming)
async def gen_link_s(client: Client, message):
    logger.info(f"[/link] Received from user {message.from_user.id}")
    try:
        from plugins.clone import async_mongo_db as mongo_db
        me = await client.get_me()
        logger.debug(f"[/link] Running as bot: @{me.username} (id={me.id})")

        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        if not bot_doc:
            logger.warning(f"[/link] No bot_doc found for bot_id={me.id}")
            return await message.reply('<b>⚠️ Bot not registered in DB. Please recreate it.</b>')

        if bot_doc.get("is_deactivated", False):
            return await message.reply_text('<b>⚠️ This bot has been deactivated by the owner.</b>')

        # Bot Mode Check
        bot_mode = bot_doc.get("bot_mode", "public")
        owner_id = int(bot_doc.get("user_id", 0))
        mods = bot_doc.get("moderators", [])
        logger.debug(f"[/link] bot_mode={bot_mode}, owner_id={owner_id}")

        if bot_mode == "private" and message.from_user.id != owner_id and message.from_user.id not in mods:
            return await message.reply('<b>❌ This bot is in Private Mode. Only the bot owner and moderators can generate links!</b>')

        # Universal Force Sub Check
        chk_u = await is_subscribed_universal(client, message)
        if chk_u == "kicked":
            return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ\'ᴛ ᴜsᴇ ᴍᴇ!</b>')
        if type(chk_u) == list:
            buttons = []
            for channel_id in chk_u:
                try:
                    chat = await client.get_chat(channel_id)
                    buttons.append([InlineKeyboardButton("ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link or f"https://t.me/{chat.username}")])
                except: continue
            buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=true")])
            return await message.reply_text(text="<b>ʜᴇʏ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!</b>", reply_markup=InlineKeyboardMarkup(buttons))

        # Clone Force Sub Check
        clone_force_channels = bot_doc.get('force_sub_channels', [])
        if clone_force_channels:
            not_joined = []
            for ch_id in clone_force_channels:
                try:
                    member = await client.get_chat_member(ch_id, message.from_user.id)
                    if member.status == enums.ChatMemberStatus.BANNED:
                        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs!</b>')
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
                return await message.reply_text(text="<b>ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋs!</b>", reply_markup=InlineKeyboardMarkup(buttons))

        replied = message.reply_to_message
        if not replied:
            return await message.reply('<b>Reply to a media file to get a shareable link.</b>')

        file_type = replied.media
        if not file_type:
            return await message.reply('<b>❌ The replied message has no media. Please reply to a file, video, audio, or document.</b>')

        try:
            media = getattr(replied, file_type.value)
            file_id = media.file_id
            logger.debug(f"[/link] Got file_id={file_id[:20]}...")
        except Exception as e:
            logger.error(f"[/link] Could not read media: {e}")
            return await message.reply(f'<b>❌ Could not read media: {e}</b>')

        short_id = str(uuid.uuid4())[:8]
        bot_username = me.username

        try:
            await mongo_db.clone_files.insert_one({
                "_id": short_id,
                "bot_username": bot_username,
                "file_id": file_id
            })
            logger.debug(f"[/link] Stored file in DB with short_id={short_id}")
        except Exception as e:
            logger.error(f"[/link] DB insert failed: {e}")
            return await message.reply(f'<b>❌ DB error: {e}</b>')

        string = 'file_' + short_id
        outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
        share_link = f"https://t.me/{bot_username}?start={outstr}"
        logger.info(f"[/link] Generated share_link={share_link}")

        user = await get_user(me.id, message.from_user.id)
        if user.get("base_site") and user.get("shortener_api"):
            short_link = await get_short_link(user, share_link)
            await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
        else:
            await message.reply(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")

    except Exception as e:
        logger.exception(f"[/link] Unhandled error: {e}")
        await message.reply(f"<b>❌ Error: <code>{e}</code></b>")


@Client.on_message(filters.command(['batch']) & filters.private & filters.incoming)
async def gen_link_batch(client: Client, message):
    logger.info(f"[/batch] Received from user {message.from_user.id}")
    try:
        from plugins.clone import async_mongo_db as mongo_db
        from config import LOG_CHANNEL

        me = await client.get_me()
        logger.debug(f"[/batch] Running as bot: @{me.username} (id={me.id})")

        bot_doc = await mongo_db.bots.find_one({'bot_id': me.id})
        if not bot_doc:
            logger.warning(f"[/batch] No bot_doc found for bot_id={me.id}")
            return await message.reply('<b>⚠️ Bot not registered in DB. Please recreate it.</b>')

        if bot_doc.get("is_deactivated", False):
            return await message.reply_text('<b>⚠️ This bot has been deactivated by the owner.</b>')

        bot_mode = bot_doc.get("bot_mode", "public")
        owner_id = int(bot_doc.get("user_id", 0))
        mods = bot_doc.get("moderators", [])

        if bot_mode == "private" and message.from_user.id != owner_id and message.from_user.id not in mods:
            return await message.reply('<b>❌ This bot is in Private Mode. Only the bot owner and moderators can generate links!</b>')

        # Universal Force Sub Check
        chk_u = await is_subscribed_universal(client, message)
        if chk_u == "kicked":
            return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs, sᴏ ʏᴏᴜ ᴄᴀɴ\'ᴛ ᴜsᴇ ᴍᴇ!</b>')
        if type(chk_u) == list:
            buttons = []
            for channel_id in chk_u:
                try:
                    chat = await client.get_chat(channel_id)
                    buttons.append([InlineKeyboardButton("ᴊᴏɪɴ ᴜɴɪᴠᴇʀsᴀʟ ᴄʜᴀɴɴᴇʟ", url=chat.invite_link or f"https://t.me/{chat.username}")])
                except: continue
            buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", url=f"https://t.me/{me.username}?start=true")])
            return await message.reply_text(text="<b>ʜᴇʏ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ!</b>", reply_markup=InlineKeyboardMarkup(buttons))

        # Clone Force Sub Check
        clone_force_channels = bot_doc.get('force_sub_channels', [])
        if clone_force_channels:
            not_joined = []
            for ch_id in clone_force_channels:
                try:
                    member = await client.get_chat_member(ch_id, message.from_user.id)
                    if member.status == enums.ChatMemberStatus.BANNED:
                        return await message.reply_text('<b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs!</b>')
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
                return await message.reply_text(text="<b>ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋs!</b>", reply_markup=InlineKeyboardMarkup(buttons))

        # ── Interactive Batch Flow using custom _ask() ──
        logger.debug("[/batch] Starting interactive flow")
        try:
            f_msg = await _ask(client, message.chat.id, "<b>Forward the FIRST message from the channel or send the message link.\n\n/cancel to stop.</b>", timeout=120)
        except asyncio.TimeoutError:
            return await message.reply("<b>❌ Timed out waiting for first message. Please try /batch again.</b>")
        if f_msg.text and f_msg.text.strip() == "/cancel":
            return await f_msg.reply("Cancelled.")

        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        if f_msg.forward_from_chat:
            f_chat_id = f_msg.forward_from_chat.id
            f_msg_id = f_msg.forward_from_message_id
            logger.debug(f"[/batch] First msg from forwarded: chat={f_chat_id}, msg={f_msg_id}")
        elif f_msg.text:
            match = regex.match(f_msg.text.strip())
            if not match:
                return await f_msg.reply("<b>Invalid link!</b>")
            f_chat_id = match.group(4)
            f_msg_id = int(match.group(5))
            if str(f_chat_id).isnumeric():
                f_chat_id = int("-100" + str(f_chat_id))
            logger.debug(f"[/batch] First msg from link: chat={f_chat_id}, msg={f_msg_id}")
        else:
            return await f_msg.reply("<b>Please forward a message or send a link!</b>")

        try:
            l_msg = await _ask(client, message.chat.id, "<b>Forward the LAST message from the channel or send the message link.\n\n/cancel to stop.</b>", timeout=120)
        except asyncio.TimeoutError:
            return await message.reply("<b>❌ Timed out waiting for last message. Please try /batch again.</b>")
        if l_msg.text and l_msg.text.strip() == "/cancel":
            return await l_msg.reply("Cancelled.")

        if l_msg.forward_from_chat:
            l_chat_id = l_msg.forward_from_chat.id
            l_msg_id = l_msg.forward_from_message_id
            logger.debug(f"[/batch] Last msg from forwarded: chat={l_chat_id}, msg={l_msg_id}")
        elif l_msg.text:
            match = regex.match(l_msg.text.strip())
            if not match:
                return await l_msg.reply("<b>Invalid link!</b>")
            l_chat_id = match.group(4)
            l_msg_id = int(match.group(5))
            if str(l_chat_id).isnumeric():
                l_chat_id = int("-100" + str(l_chat_id))
            logger.debug(f"[/batch] Last msg from link: chat={l_chat_id}, msg={l_msg_id}")
        else:
            return await l_msg.reply("<b>Please forward a message or send a link!</b>")

        if str(f_chat_id) != str(l_chat_id):
            return await l_msg.reply("<b>Chat IDs do not match! Both messages must be from the same channel.</b>")

        try:
            resolved = await client.get_chat(f_chat_id)
            chat_id = resolved.id
            logger.debug(f"[/batch] Resolved chat: {resolved.title} ({chat_id})")
        except Exception as e:
            logger.error(f"[/batch] get_chat failed: {e}")
            return await l_msg.reply(f"<b>Error: {e}\nMake sure I am admin in that channel.</b>")

        sts = await l_msg.reply("<b>ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪɴᴋ ғᴏʀ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ.\nᴛʜɪs ᴍᴀʏ ᴛᴀᴋᴇ ᴛɪᴍᴇ ᴅᴇᴘᴇɴᴅɪɴɢ ᴜᴘᴏɴ ɴᴜᴍʙᴇʀ ᴏғ ᴍᴇssᴀɢᴇs</b>")
        FRMT = "**ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪɴᴋ...**\n**ᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs:** {total}\n**ᴅᴏɴᴇ:** {current}\n**ʀᴇᴍᴀɪɴɪɴɢ:** {rem}\n**sᴛᴀᴛᴜs:** Fetching Messages"

        outlist = []
        tot = 0
        total_count = l_msg_id - f_msg_id + 1
        logger.info(f"[/batch] Fetching {total_count} messages from {f_msg_id} to {l_msg_id}")

        for m_id in range(f_msg_id, l_msg_id + 1):
            tot += 1
            if tot % 10 == 0:
                try:
                    await sts.edit(FRMT.format(total=total_count, current=tot, rem=(total_count - tot)))
                except: pass
            try:
                msg = await client.get_messages(chat_id, m_id)
                if msg.empty or msg.service:
                    continue
                outlist.append({"channel_id": chat_id, "msg_id": msg.id})
            except Exception as e:
                logger.debug(f"[/batch] Skipping msg {m_id}: {e}")
                continue

        if not outlist:
            return await sts.edit("<b>❌ No valid messages found in that range!</b>")

        logger.info(f"[/batch] Collected {len(outlist)} valid messages, uploading to LOG_CHANNEL={LOG_CHANNEL}")
        temp_file = f"batchmode_clone_{message.from_user.id}.json"
        with open(temp_file, "w+") as out:
            json.dump(outlist, out)

        try:
            post = await StreamBot.send_document(LOG_CHANNEL, temp_file, file_name="Batch.json", caption="⚠️ Clone Batch Generated.")
            logger.debug(f"[/batch] Uploaded batch JSON, post.id={post.id}")
        except Exception as e:
            logger.error(f"[/batch] Failed to upload to LOG_CHANNEL: {e}")
            os.remove(temp_file)
            return await sts.edit(f"<b>❌ Failed to save batch: {e}</b>")

        os.remove(temp_file)
        string = str(post.id)
        outstr = "BATCH-" + base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
        bot_username = me.username
        share_link = f"https://t.me/{bot_username}?start={outstr}"
        logger.info(f"[/batch] Generated share_link={share_link}")

        user = await get_user(me.id, message.from_user.id)
        if user.get("base_site") and user.get("shortener_api"):
            short_link = await get_short_link(user, share_link)
            await sts.edit(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ:\n\n🖇️ sʜᴏʀᴛ ʟɪɴᴋ :- {short_link}\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")
        else:
            await sts.edit(f"<b>⭕ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʙᴀᴛᴄʜ ʟɪɴᴋ:\n\n🔗 ᴏʀɪɢɪɴᴀʟ ʟɪɴᴋ :- {share_link}</b>")

    except Exception as e:
        logger.exception(f"[/batch] Unhandled error: {e}")
        await message.reply(f"<b>❌ Error: <code>{e}</code></b>")
