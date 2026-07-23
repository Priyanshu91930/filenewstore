# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

# Clone Code Credit : YT - @Tech_VJ / TG - @viralverse0909 / GitHub - @VJBots

import datetime, time, asyncio
from pyrogram import Client, filters
from plugins.clone import mongo_db
from pyrogram.errors import *
from clone_plugins.dbusers import clonedb
        
@Client.on_message(filters.command("broadcast"))
async def pm_broadcast(bot, message):
    me = await bot.get_me()
    owner = mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(owner.get("user_id", 0)) if owner else 0
    mods = owner.get("moderators", []) if owner else []
    if message.from_user.id != owner_id and message.from_user.id not in mods:
        await message.reply_text("❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴀɴᴅ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ❗")
        return
        
    if owner and owner.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

    b_msg = await bot.ask(chat_id = message.from_user.id, text = "Now Send Me Your Broadcast Message")
    try:
        users = await clonedb.get_all_users(me.id)
        sts = await message.reply_text('Broadcasting your messages...')
        start_time = time.time()
        total_users = await clonedb.total_users_count(me.id)
        done = 0
        blocked = 0
        deleted = 0
        failed = 0
        success = 0
        async for user in users:
            if 'user_id' in user:
                pti, sh = await broadcast_messages(me.id, int(user['user_id']), b_msg)
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
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
            else:
                # Handle the case where 'id' key is missing in the user dictionary 
                done += 1
                failed += 1
                if not done % 20:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
    
        time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
        await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")
    except Exception as e:
        print(f"error: {e}")

# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190

async def broadcast_messages(bot_id, user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(bot_id, user_id, message)
    except InputUserDeactivated:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Deleted"
    except UserIsBlocked:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Blocked"
    except PeerIdInvalid:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Error"
    except Exception as e:
        await clonedb.delete_user(bot_id, user_id)
        return False, "Error"


@Client.on_message(filters.command("broadcast_app"))
async def clone_broadcast_app_handler(bot, message):
    me = await bot.get_me()
    owner = mongo_db.bots.find_one({'bot_id': me.id})
    owner_id = int(owner.get("user_id", 0)) if owner else 0
    mods = owner.get("moderators", []) if owner else []
    
    if message.from_user.id != owner_id and message.from_user.id not in mods:
        await message.reply_text("❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴀɴᴅ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ❗")
        return

    if owner and owner.get("is_deactivated", False):
        return await message.reply_text("<b>⚠️ This bot has been deactivated by the owner.</b>")

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
        from plugins.clone import async_mongo_db
        await async_mongo_db.app_notifications.insert_one(notification_doc)
        
        # Fetch all registered user push tokens from database
        cursor = async_mongo_db.user.find({"push_token": {"$exists": True, "$ne": ""}}, {"push_token": 1, "_id": 0})
        users_list = await cursor.to_list(length=1000)
        tokens = [u.get("push_token") for u in users_list if u.get("push_token")]
        
        sent_count = 0
        if tokens:
            import aiohttp
            # Expo sends in batches (max 100 per request)
            chunk_size = 100
            for i in range(0, len(tokens), chunk_size):
                chunk = tokens[i:i + chunk_size]
                payload = [
                    {
                        "to": token,
                        "sound": "default",
                        "title": title,
                        "body": body,
                        "data": {"screen": "notification"}
                    } for token in chunk
                ]
                
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "https://exp.host/--/api/v2/push/send",
                            json=payload,
                            headers={"Content-Type": "application/json"}
                        ) as resp:
                            if resp.status == 200:
                                sent_count += len(chunk)
                except Exception as send_err:
                    print(f"Error sending push chunk: {send_err}")

        await message.reply_text(
            f"✅ **Notification Broadcasted successfully from clone!**\n\n"
            f"📌 **Title:** {title}\n"
            f"📝 **Body:** {body}\n\n"
            f"🔔 **Push Alerts Sent:** To {sent_count} registered app devices!"
        )
    except Exception as e:
        await message.reply_text(f"❌ **Error saving/sending notification:** {e}")


# Don't Remove Credit Tg - @viralverse0909
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @Brainaxe190
