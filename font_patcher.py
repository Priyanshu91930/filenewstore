import re
import logging
from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, CallbackQuery

logger = logging.getLogger(__name__)

def to_small_caps(text: str) -> str:
    if not isinstance(text, str):
        return text
        
    normal_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small_caps   = "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    trans = str.maketrans(normal_chars, small_caps)
    
    # Preserve <code>...</code>, <pre>...</pre>, HTML tags, HTTP/HTTPS URLs, and Telegram handles
    pattern = re.compile(r'(<code>.*?</code>|<pre>.*?</pre>|<[^>]+>|https?://[^\s]+|@[a-zA-Z0-9_]+)', re.DOTALL)
    parts = pattern.split(text)
    
    for i in range(len(parts)):
        # Translate only if it's not a preserved block
        if not (
            parts[i].startswith("<code>") or 
            parts[i].startswith("<pre>") or 
            (parts[i].startswith("<") and parts[i].endswith(">")) or 
            parts[i].startswith("http") or 
            parts[i].startswith("@")
        ):
            parts[i] = parts[i].translate(trans)
            
    return "".join(parts)

# ── Monkeypatch pyrogram.types.InlineKeyboardButton ──
old_btn_init = InlineKeyboardButton.__init__
def new_btn_init(self, text, *args, **kwargs):
    if text:
        text = to_small_caps(text)
    old_btn_init(self, text, *args, **kwargs)
InlineKeyboardButton.__init__ = new_btn_init

# ── Monkeypatch pyrogram.Client Methods ──
old_send_message = Client.send_message
async def new_send_message(self, chat_id, text, *args, **kwargs):
    if text:
        text = to_small_caps(text)
    return await old_send_message(self, chat_id, text, *args, **kwargs)
Client.send_message = new_send_message

old_send_photo = Client.send_photo
async def new_send_photo(self, chat_id, photo, caption=None, *args, **kwargs):
    if caption:
        caption = to_small_caps(caption)
    return await old_send_photo(self, chat_id, photo, caption=caption, *args, **kwargs)
Client.send_photo = new_send_photo

old_send_cached_media = Client.send_cached_media
async def new_send_cached_media(self, chat_id, file_id, caption=None, *args, **kwargs):
    if caption:
        caption = to_small_caps(caption)
    return await old_send_cached_media(self, chat_id, file_id, caption=caption, *args, **kwargs)
Client.send_cached_media = new_send_cached_media

old_edit_message_text = Client.edit_message_text
async def new_edit_message_text(self, chat_id, message_id, text, *args, **kwargs):
    if text:
        text = to_small_caps(text)
    return await old_edit_message_text(self, chat_id, message_id, text, *args, **kwargs)
Client.edit_message_text = new_edit_message_text

old_edit_message_caption = Client.edit_message_caption
async def new_edit_message_caption(self, chat_id, message_id, caption=None, *args, **kwargs):
    if caption:
        caption = to_small_caps(caption)
    return await old_edit_message_caption(self, chat_id, message_id, caption=caption, *args, **kwargs)
Client.edit_message_caption = new_edit_message_caption

old_answer_callback_query = Client.answer_callback_query
async def new_answer_callback_query(self, callback_query_id, text=None, *args, **kwargs):
    if text:
        text = to_small_caps(text)
    return await old_answer_callback_query(self, callback_query_id, text=text, *args, **kwargs)
Client.answer_callback_query = new_answer_callback_query

# ── Monkeypatch pyrogram.types.CallbackQuery ──
old_answer = CallbackQuery.answer
async def new_answer(self, text=None, *args, **kwargs):
    if text:
        text = to_small_caps(text)
    return await old_answer(self, text=text, *args, **kwargs)
CallbackQuery.answer = new_answer

logger.info("Unicode Small Caps Font Patcher loaded and applied successfully globally!")
