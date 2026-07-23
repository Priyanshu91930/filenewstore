# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from plugins.dbusers import db
from pyrogram import Client, filters
from config import ADMINS
import asyncio
import datetime
import time

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        return False, "Deleted"
    except UserIsBlocked:
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception as e:
        return False, "Error"

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def verupikkals(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(text='**Broadcasting your messages...**')
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed = 0
    success = 0

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

    async for user in users:
        if 'id' in user:
            pti, sh = await broadcast_messages(int(user['id']), b_msg)
            if pti:
                success += 1
            elif pti == False:
                if sh == "Blocked":
                    blocked += 1
                elif sh == "Deleted":
                    deleted += 1
                elif sh == "Error":
                    failed += 1
            done += 1
            if not done % 20:
                try:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
                except:
                    pass
        else:
            # Handle the case where 'id' key is missing in the user dictionary
            done += 1
            failed += 1
            if not done % 20:
                try:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
                except:
                    pass
    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")


@Client.on_message(filters.command("broadcast_app") & filters.user(ADMINS))
async def broadcast_app_handler(bot, message):
    from plugins.clone import async_mongo_db
    
    # Extract message content
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ **Usage:** `/broadcast_app Title | Body text of the notification`\n\n"
            "Use the `|` symbol to separate Title and Description."
        )
        
    full_text = message.text.split(None, 1)[1]
    title = "Announcement 📢"
    body = full_text
    
    if "|" in full_text:
        parts = full_text.split("|", 1)
        title = parts[0].strip()
        body = parts[1].strip()
        
    # Save notification to MongoDB
    now = time.time()
    notification_doc = {
        "title": title,
        "body": body,
        "created_at": now
    }
    
    try:
        await async_mongo_db.app_notifications.insert_one(notification_doc)
        await message.reply_text(
            f"✅ **Notification Broadcasted successfully!**\n\n"
            f"📌 **Title:** {title}\n"
            f"📝 **Body:** {body}\n\n"
            f"All app users will now see this notification inside their Notification tab."
        )
    except Exception as e:
        await message.reply_text(f"❌ **Error saving notification:** {e}")

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

