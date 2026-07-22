import sys
import os
import json
import base64
import time
import asyncio
from pymongo import MongoClient
from pyrogram import Client

# Reconfigure stdout for UTF-8 compatibility
sys.stdout.reconfigure(encoding='utf-8')

# Import configuration
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from config import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, GDRIVE_FOLDER_ID, GDRIVE_SERVICE_ACCOUNT_FILE
    from gdrive_helper import upload_file_to_gdrive
except ImportError as e:
    print(f"❌ Failed to import configuration or helpers: {e}")
    sys.exit(1)

# Connect to MongoDB
print("Connecting to MongoDB database...")
db_client = MongoClient("mongodb+srv://anihubyt:Zxcvbnmm9193@cluster0.qv5tu12.mongodb.net/?appName=Cluster0")
db = db_client["cloned_vjbotz"]

# Main migration runner
async def run_migration():
    if not os.path.exists(GDRIVE_SERVICE_ACCOUNT_FILE):
        print(f"❌ Error: Service account key not found at {GDRIVE_SERVICE_ACCOUNT_FILE}")
        return

    if not GDRIVE_FOLDER_ID:
        print("❌ Error: GDRIVE_FOLDER_ID is empty in config.py")
        return

    print("Initializing Telegram Bot Client...")
    bot = Client(
        "migration_session",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        in_memory=True
    )
    
    await bot.start()
    print("✅ Bot client logged in successfully.")

    # Find posts for @Miakhalifaaah_bot that have not been migrated
    bot_username = "Miakhalifaaah_bot"
    query = {"bot_username": bot_username, "is_gdrive": {"$ne": True}}
    total_posts = db.posts.count_documents(query)
    print(f"🔍 Found {total_posts} posts to migrate for @{bot_username}.")

    if total_posts == 0:
        print("🎉 No posts left to migrate!")
        await bot.stop()
        return

    posts_cursor = db.posts.find(query).sort("created_at", -1)
    
    # Create temp download directory
    temp_dir = "scratch/temp_migration"
    os.makedirs(temp_dir, exist_ok=True)

    success_count = 0
    fail_count = 0

    for idx, post in enumerate(posts_cursor):
        post_id = post["_id"]
        title = post.get("title", "Untitled")
        deeplink = post.get("file_deeplink", "")
        
        print(f"\n──────────────────────────────────────────────────")
        print(f"[{idx+1}/{total_posts}] Processing: '{title}' (ID: {post_id})")
        print(f"Deeplink: {deeplink}")

        if not deeplink:
            print("⚠️ Skip: Empty file_deeplink")
            continue

        gdrive_ids = []
        is_batch = False

        # --- CASE 1: BATCH LINKS ---
        if deeplink.startswith("BATCH-"):
            is_batch = True
            try:
                batch_file_id = deeplink.split("-", 1)[1]
                # Decode BATCH string to get LOG_CHANNEL message ID
                decoded_msg_id = int(base64.urlsafe_b64decode(batch_file_id + "=" * (-len(batch_file_id) % 4)).decode("ascii"))
                print(f"📥 Fetching Batch JSON document from LOG_CHANNEL message ID {decoded_msg_id}...")
                
                # Fetch message
                msg = await bot.get_messages(LOG_CHANNEL, decoded_msg_id)
                if not msg or not msg.document:
                    print(f"❌ Error: Could not fetch document from LOG_CHANNEL message {decoded_msg_id}")
                    fail_count += 1
                    continue
                
                # Download Batch JSON file
                batch_json_path = await bot.download_media(msg.document.file_id, file_name=os.path.join(temp_dir, f"batch_{post_id}.json"))
                if not batch_json_path or not os.path.exists(batch_json_path):
                    print("❌ Error: Failed to download Batch JSON file.")
                    fail_count += 1
                    continue
                
                with open(batch_json_path, "r", encoding="utf-8") as f:
                    batch_data = json.load(f)
                
                try:
                    os.remove(batch_json_path)
                except:
                    pass
                
                print(f"📦 Batch contains {len(batch_data)} video files. Migrating all...")
                
                # Process each file in the batch
                for b_idx, item in enumerate(batch_data):
                    channel_id = item["channel_id"]
                    msg_id = item["msg_id"]
                    
                    print(f"  └─► [{b_idx+1}/{len(batch_data)}] Downloading video from channel {channel_id}, message {msg_id}...")
                    
                    # Fetch video message
                    video_msg = await bot.get_messages(channel_id, msg_id)
                    if not video_msg or not (video_msg.video or video_msg.document):
                        print(f"  ⚠️ Skip: Message {msg_id} has no valid video or document.")
                        continue
                        
                    media = video_msg.video or video_msg.document
                    local_filename = getattr(media, "file_name", f"video_{post_id}_{b_idx}.mp4")
                    local_path = os.path.join(temp_dir, local_filename)
                    
                    # Download video file
                    video_path = await bot.download_media(media.file_id, file_name=local_path)
                    if not video_path or not os.path.exists(video_path):
                        print("  ❌ Skip: Failed to download video file.")
                        continue
                        
                    # Upload to Google Drive
                    print("  ⚡ Uploading to Google Drive...")
                    gdrive_id, masked_name = upload_file_to_gdrive(video_path, local_filename)
                    
                    # Clean up local video
                    try:
                        os.remove(video_path)
                    except:
                        pass
                        
                    if gdrive_id:
                        gdrive_ids.append(gdrive_id)
                        print(f"  ✅ Uploaded! GDrive File ID: {gdrive_id}")
                    else:
                        print(f"  ❌ GDrive Upload Failed: {masked_name}")
                        
            except Exception as e:
                print(f"❌ Error parsing Batch link: {e}")
                fail_count += 1
                continue

        # --- CASE 2: SINGLE FILE LINKS ---
        else:
            try:
                # Decode file details
                decoded = base64.urlsafe_b64decode(deeplink + "=" * (-len(deeplink) % 4)).decode("ascii")
                if "_" in decoded:
                    _, decode_file_id = decoded.split("_", 1)
                else:
                    decode_file_id = decoded

                file_id = None
                
                # If numeric, fetch directly from LOG_CHANNEL
                if decode_file_id.isdigit():
                    msg = await bot.get_messages(LOG_CHANNEL, int(decode_file_id))
                    if msg and msg.media:
                        media = getattr(msg, msg.media.value)
                        file_id = media.file_id
                        local_filename = getattr(media, "file_name", f"video_{post_id}.mp4")
                else:
                    # Fetch from clone_files collection in DB
                    file_doc = db.clone_files.find_one({"_id": decode_file_id})
                    if file_doc:
                        file_id = file_doc.get("file_id")
                        local_filename = f"video_{post_id}.mp4"
                
                if not file_id:
                    print("❌ Error: Could not locate Telegram file_id in DB or LOG_CHANNEL")
                    fail_count += 1
                    continue
                    
                local_path = os.path.join(temp_dir, local_filename)
                
                # Download video file
                print("📥 Downloading video from Telegram...")
                video_path = await bot.download_media(file_id, file_name=local_path)
                if not video_path or not os.path.exists(video_path):
                    print("❌ Error: Failed to download video file.")
                    fail_count += 1
                    continue
                    
                # Upload to Google Drive
                print("⚡ Uploading to Google Drive...")
                gdrive_id, masked_name = upload_file_to_gdrive(video_path, local_filename)
                
                # Clean up local video
                try:
                    os.remove(video_path)
                except:
                    pass
                    
                if gdrive_id:
                    gdrive_ids.append(gdrive_id)
                    print(f"✅ Uploaded! GDrive File ID: {gdrive_id}")
                else:
                    print(f"❌ GDrive Upload Failed: {masked_name}")
                    fail_count += 1
                    continue

            except Exception as e:
                print(f"❌ Error processing single file link: {e}")
                fail_count += 1
                continue

        # --- UPDATE DATABASE RECORD ---
        if gdrive_ids:
            # Set the main file ID and list of all parts/episodes
            update_data = {
                "$set": {
                    "is_gdrive": True,
                    "is_batch": is_batch,
                    "gdrive_file_id": gdrive_ids[0],
                    "gdrive_file_ids": gdrive_ids
                }
            }
            db.posts.update_one({"_id": post_id}, update_data)
            print(f"🎉 Post updated in DB! Saved {len(gdrive_ids)} parts.")
            success_count += 1
        else:
            print("❌ Migration Failed: No videos were successfully uploaded to Google Drive.")
            fail_count += 1

    print(f"\n==================================================")
    print(f"Migration finished. Success: {success_count}, Failed: {fail_count}")
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(run_migration())
