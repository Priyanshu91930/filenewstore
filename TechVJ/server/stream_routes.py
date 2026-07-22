# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import re
import time
import math
import logging
import secrets
import mimetypes
from aiohttp import web
from aiohttp.http_exceptions import BadStatusLine
from TechVJ.bot import multi_clients, work_loads, StreamBot
from TechVJ.server.exceptions import FIleNotFound, InvalidHash
from TechVJ import StartTime, __version__
from ..utils.time_format import get_readable_time
from ..utils.custom_dl import ByteStreamer
from TechVJ.utils.render_template import render_page
from config import MULTI_CLIENT


routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(_):
    try:
        with open("static/website/index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return web.Response(text=content, content_type='text/html')
    except Exception:
        return web.json_response(
            {
                "server_status": "running",
                "uptime": get_readable_time(time.time() - StartTime),
                "telegram_bot": "@" + StreamBot.username,
                "connected_bots": len(multi_clients),
                "version": __version__,
            }
        )

import asyncio
async def check_and_track_referral_click(bot_username: str, user_id: str, file_id: str):
    if not bot_username or not user_id:
        return
    try:
        from plugins.clone import async_mongo_db
        bot_doc = await async_mongo_db.bots.find_one({"username": re.compile(f"^{bot_username}$", re.IGNORECASE)})
        if bot_doc:
            bot_id = bot_doc.get("bot_id")
            if bot_id:
                from clone_plugins.db_referral import is_campaign_active, track_click
                if await is_campaign_active(bot_id):
                    await track_click(bot_id, int(user_id), file_id)
    except Exception as e:
        logging.error(f"Error tracking referral click: {e}")

@routes.get("/tma", allow_head=True)
async def tma_route_handler(request: web.Request):
    from config import MONETAG_ZONE_ID, BOT_USERNAME, LOG_CHANNEL
    from TechVJ.bot import StreamBot
    import jinja2
    import base64
    from urllib.parse import unquote
    from utils import get_tma_shortlink

    uid          = request.rel_url.query.get('uid', '')
    token        = request.rel_url.query.get('token', '')
    file_data    = unquote(request.rel_url.query.get('file', ''))
    bot_username = request.rel_url.query.get('bot', BOT_USERNAME)
    zone         = MONETAG_ZONE_ID or ''

    short_link = ""
    if uid and token and file_data:
        try:
            short_link = await get_tma_shortlink(int(uid), token, file_data, bot_username)
        except Exception as e:
            logging.error(f"Error generating shortlink: {e}")

    # Fetch actual file details
    file_name = "Your File"
    file_size = ""
    file_emoji = "📁"
    
    is_verified = False
    remaining_time = 0
    
    if uid:
        from utils import check_tma_verification, TMA_VERIFIED, TMA_TIMEOUT
        import time
        try:
            from TechVJ.bot import StreamBot
            from plugins.clone import async_mongo_db
            bot_id = None
            if bot_username.lower() != StreamBot.username.lower():
                bot_doc = await async_mongo_db.bots.find_one({"username": bot_username})
                if bot_doc:
                    bot_id = bot_doc.get("bot_id")
            else:
                bot_id = StreamBot.me.id if (hasattr(StreamBot, 'me') and StreamBot.me) else None

            is_verified = await check_tma_verification(int(uid), bot_id=bot_id)
            key = f"{bot_id}_{uid}" if (bot_id and f"{bot_id}_{uid}" in TMA_VERIFIED) else int(uid)
            if is_verified and key in TMA_VERIFIED:
                val = TMA_VERIFIED[key]
                if isinstance(val, dict):
                    verified_at = val.get("verified_at", 0)
                    elapsed = time.time() - verified_at
                    remaining_time = max(0, int(3600 - elapsed))
                else:
                    elapsed = time.time() - val
                    remaining_time = max(0, int(TMA_TIMEOUT - elapsed))
        except Exception as e:
            logging.error(f"Error checking verification: {e}")
    
    if file_data:
        if file_data.startswith("BATCH-"):
            file_name = "Batch Folder"
            file_emoji = "📂"
        else:
            try:
                # Decode file details
                decoded = base64.urlsafe_b64decode(file_data + "=" * (-len(file_data) % 4)).decode("ascii")
                if "_" in decoded:
                    _, decode_file_id = decoded.split("_", 1)
                else:
                    decode_file_id = decoded
                
                if decode_file_id.isdigit():
                    msg = await StreamBot.get_messages(LOG_CHANNEL, int(decode_file_id))
                    if msg and msg.media:
                        media = getattr(msg, msg.media.value)
                        raw_name = getattr(media, "file_name", "Your File")
                        # Format name
                        file_name = ' '.join(filter(lambda x: not x.startswith('http') and not x.startswith('@') and not x.startswith('www.'), raw_name.replace("[", "").replace("]", "").replace("(", "").replace(")", "").split()))
                        
                        # Calculate size
                        size_bytes = float(media.file_size)
                        units = ["Bytes", "KB", "MB", "GB"]
                        i = 0
                        while size_bytes >= 1024.0 and i < len(units) - 1:
                            i += 1
                            size_bytes /= 1024.0
                        file_size = "%.2f %s" % (size_bytes, units[i])
                        
                        # Set emoji based on type
                        mtype = msg.media.value
                        if mtype in ["video", "animation"]:
                            file_emoji = "🎬"
                        elif mtype == "audio":
                            file_emoji = "🎵"
                        elif mtype == "photo":
                            file_emoji = "🖼️"
                        else:
                            file_emoji = "📄"
                else:
                    from plugins.clone import async_mongo_db
                    file_doc = await async_mongo_db.clone_files.find_one({"_id": decode_file_id})
                    if file_doc:
                        file_name = "Cloned File"
                        file_emoji = "📁"
            except Exception as e:
                logging.error(f"Error fetching file details: {e}")

    # Load and render templates/index.html using Jinja2
    template_path = "templates/index.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = jinja2.Template(f.read())
        
        rendered = template.render(
            monetag_zone_id = zone,
            user_id         = uid,
            token           = token,
            bot_username    = bot_username,
            file_id         = file_data,
            file_deeplink   = file_data,
            short_link      = short_link,
            file_name       = file_name,
            file_size       = file_size,
            file_emoji      = file_emoji,
            is_verified     = is_verified,
            remaining_time  = remaining_time,
        )
        return web.Response(text=rendered, content_type='text/html')
    except Exception as e:
        return web.Response(text=f"Error rendering TMA template: {e}", status=500)

@routes.post("/tma-verify")
async def tma_verify_handler(request: web.Request):
    from config import TMA_SECRET_KEY, BOT_USERNAME
    import hmac as _hmac, hashlib, time as _time

    try:
        data = await request.json()
    except Exception:
        data = {}

    uid_str   = str(data.get('uid', ''))
    token     = str(data.get('token', ''))
    file_data = str(data.get('file', ''))
    bot_username = str(data.get('bot', BOT_USERNAME))

    # Validate HMAC token and mark the user as verified for today!
    from utils import verify_tma_user
    try:
        from TechVJ.bot import StreamBot
        from plugins.clone import async_mongo_db
        bot_id = None
        if bot_username.lower() != StreamBot.username.lower():
            bot_doc = await async_mongo_db.bots.find_one({"username": bot_username})
            if bot_doc:
                bot_id = bot_doc.get("bot_id")
        else:
            bot_id = StreamBot.me.id if (hasattr(StreamBot, 'me') and StreamBot.me) else None

        is_verified = await verify_tma_user(int(uid_str), token, bot_id=bot_id)
        if not is_verified:
            return web.json_response({'ok': False, 'error': 'invalid_token'}, status=400)
    except Exception as e:
        return web.json_response({'ok': False, 'error': f'validation_error: {e}'}, status=400)

    # Build deeplink
    if file_data:
        deeplink = f"https://t.me/{bot_username}?start=unlock-{uid_str}-{token}-{file_data}"
    else:
        deeplink = f"https://t.me/{bot_username}?start=tma-{uid_str}-{token}"

    return web.json_response({'ok': True, 'deeplink': deeplink})


@routes.get("/sw.js")
async def sw_route_handler(_):
    try:
        with open("templates/sw.js", "r", encoding="utf-8") as f:
            content = f.read()
        return web.Response(text=content, content_type='application/javascript')
    except Exception as e:
        return web.Response(text=f"Error loading service worker: {e}", status=404)


@routes.get(r"/watch/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        filename = None
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            first_part = path.split("/")[0]
            if first_part.isdigit():
                id = int(first_part)
            else:
                id = first_part
            if "/" in path:
                filename = "/".join(path.split("/")[1:])
            secure_hash = request.rel_url.query.get("hash")
        bot = request.rel_url.query.get("bot")
        user = request.rel_url.query.get("user")
        if bot and user:
            asyncio.create_task(check_and_track_referral_click(bot, user, str(id)))
        return web.Response(text=await render_page(id, secure_hash, bot=bot, filename=filename), content_type='text/html')
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except AttributeError:
        raise web.HTTPNotFound(text="Not Found")
    except (BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

@routes.get(r"/{path:\S+}", allow_head=True)
async def stream_handler(request: web.Request):
    try:
        path = request.match_info["path"]
        match = re.search(r"^([a-zA-Z0-9_-]{6})(\d+)$", path)
        if match:
            secure_hash = match.group(1)
            id = int(match.group(2))
        else:
            first_part = path.split("/")[0]
            if first_part.isdigit():
                id = int(first_part)
            else:
                id = first_part
            secure_hash = request.rel_url.query.get("hash")
        return await media_streamer(request, id, secure_hash)
    except InvalidHash as e:
        raise web.HTTPForbidden(text=e.message)
    except FIleNotFound as e:
        raise web.HTTPNotFound(text=e.message)
    except AttributeError:
        raise web.HTTPNotFound(text="Not Found")
    except (BadStatusLine, ConnectionResetError):
        pass
    except Exception as e:
        logging.critical(e.with_traceback(None))
        raise web.HTTPInternalServerError(text=str(e))

class_cache = {}

async def media_streamer(request: web.Request, id: int, secure_hash: str):
    range_header = request.headers.get("Range", 0)
    logging.info(f"media_streamer called: id={id} ({type(id)}), secure_hash={secure_hash}")
    
    bot_param = request.rel_url.query.get("bot")
    user_param = request.rel_url.query.get("user")
    if bot_param and user_param:
        asyncio.create_task(check_and_track_referral_click(bot_param, user_param, str(id)))
    faster_client = None
    index = None

    if bot_param:
        try:
            from plugins.clone import running_clones
            target_bot_id = None
            if bot_param.isdigit():
                target_bot_id = int(bot_param)
            else:
                from plugins.clone import async_mongo_db
                bot_doc = await async_mongo_db.bots.find_one({"username": re.compile(f"^{bot_param}$", re.IGNORECASE)})
                if bot_doc:
                    target_bot_id = bot_doc.get("bot_id")
            
            if target_bot_id and target_bot_id in running_clones:
                faster_client = running_clones[target_bot_id]
                index = target_bot_id
                logging.info(f"Using cloned bot client {bot_param} (ID: {target_bot_id}) to serve request")
        except Exception as e:
            logging.error(f"Error resolving clone bot client for download: {e}")

    if not faster_client:
        index = min(work_loads, key=work_loads.get)
        faster_client = multi_clients[index]
        if MULTI_CLIENT:
            logging.info(f"Client {index} is now serving {request.remote}")

    if faster_client in class_cache:
        tg_connect = class_cache[faster_client]
        logging.debug(f"Using cached ByteStreamer object for client {index}")
    else:
        logging.debug(f"Creating new ByteStreamer object for client {index}")
        tg_connect = ByteStreamer(faster_client)
        class_cache[faster_client] = tg_connect
    if isinstance(id, str):
        from plugins.clone import async_mongo_db
        from pyrogram.file_id import FileId
        try:
            logging.info(f"Querying MongoDB clone_files collection for _id={id} inside database: {async_mongo_db.name}")
            cols = await async_mongo_db.list_collection_names()
            logging.info(f"Available collections in {async_mongo_db.name}: {cols}")
            file_doc = await async_mongo_db.clone_files.find_one({"_id": id})
            logging.info(f"Query result for _id={id}: {file_doc}")
        except Exception as db_err:
            logging.error(f"MongoDB query error: {db_err}")
            file_doc = None

        if not file_doc:
            logging.debug(f"Clone file with ID {id} not found in DB")
            raise FIleNotFound
            
        import time
        refreshed_at = file_doc.get("refreshed_at", 0)
        chat_id = file_doc.get("chat_id")
        message_id = file_doc.get("message_id")
        raw_file_id = file_doc["file_id"]
        
        if chat_id and message_id and (time.time() - refreshed_at > 7200):
            try:
                logging.info(f"Refreshing file reference for cloned file {id} on the fly...")
                msg = await faster_client.get_messages(chat_id, message_id)
                if msg and msg.media:
                    media = getattr(msg, msg.media.value)
                    raw_file_id = media.file_id
                    await async_mongo_db.clone_files.update_one(
                        {"_id": id},
                        {"$set": {"file_id": raw_file_id, "refreshed_at": time.time()}}
                    )
                    logging.info(f"Successfully refreshed file reference for {id}")
            except Exception as ref_err:
                logging.error(f"Failed to refresh file reference for {id}: {ref_err}")
                
        file_id = FileId.decode(raw_file_id)
        safe_hash = secure_hash or ""
        setattr(file_id, "unique_id", safe_hash + "xxxxx")
        db_file_size = file_doc.get("file_size") or (2 * 1024 * 1024 * 1024)
        setattr(file_id, "file_size", db_file_size)
    else:
        logging.debug("before calling get_file_properties")
        file_id = await tg_connect.get_file_properties(id)
        logging.debug("after calling get_file_properties")
    
    if file_id.unique_id[:6] != secure_hash:
        logging.debug(f"Invalid hash for message with ID {id}")
        raise InvalidHash
    
    file_size = file_id.file_size

    if range_header:
        from_bytes, until_bytes = range_header.replace("bytes=", "").split("-")
        from_bytes = int(from_bytes)
        until_bytes = int(until_bytes) if until_bytes else file_size - 1
    else:
        from_bytes = request.http_range.start or 0
        until_bytes = (request.http_range.stop or file_size) - 1

    if (until_bytes > file_size) or (from_bytes < 0) or (until_bytes < from_bytes):
        return web.Response(
            status=416,
            body="416: Range not satisfiable",
            headers={"Content-Range": f"bytes */{file_size}"},
        )

    chunk_size = 1024 * 1024
    until_bytes = min(until_bytes, file_size - 1)

    offset = from_bytes - (from_bytes % chunk_size)
    first_part_cut = from_bytes - offset
    last_part_cut = until_bytes % chunk_size + 1

    req_length = until_bytes - from_bytes + 1
    part_count = math.ceil(until_bytes / chunk_size) - math.floor(offset / chunk_size)
    body = tg_connect.yield_file(
        file_id, index, offset, first_part_cut, last_part_cut, part_count, chunk_size
    )

    url_filename = None
    path_param = request.match_info.get("path", "")
    if "/" in path_param:
        url_filename = path_param.split("/")[-1]
    
    file_name = getattr(file_id, "file_name", None) or url_filename or f"{secrets.token_hex(4)}"
    mime_type = getattr(file_id, "mime_type", None)
    
    if not mime_type:
        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        
    import urllib.parse
    disposition = "attachment"
    safe_file_name = file_name.replace('"', '\\"')
    try:
        encoded_filename = urllib.parse.quote(file_name)
        content_disposition = f'{disposition}; filename="{safe_file_name}"; filename*=UTF-8\'\'{encoded_filename}'
    except Exception:
        content_disposition = f'{disposition}; filename="{safe_file_name}"'

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": content_disposition,
            "Accept-Ranges": "bytes",
            "X-Accel-Buffering": "no",
        },
    )

@routes.get("/portal", allow_head=True)
async def portal_route_handler(request: web.Request):
    import jinja2
    template_path = "templates/portal.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = jinja2.Template(f.read())
        rendered = template.render()
        return web.Response(text=rendered, content_type='text/html')
    except Exception as e:
        return web.Response(text=f"Error rendering portal template: {e}", status=500)

@routes.get("/portal-data")
async def portal_data_route_handler(request: web.Request):
    from plugins.clone import async_mongo_db
    import math

    page = int(request.rel_url.query.get('page', 1))
    category = request.rel_url.query.get('category', 'All')
    search = request.rel_url.query.get('search', '')
    limit = 12

    query = {}
    if category != 'All':
        query['category'] = category
    if search:
        query['title'] = {'$regex': search, '$options': 'i'}

    total_posts = await async_mongo_db.posts.count_documents(query)
    total_pages = math.ceil(total_posts / limit) or 1
    page = max(1, min(page, total_pages))
    skip = (page - 1) * limit

    posts_cursor = async_mongo_db.posts.find(query).sort('created_at', -1).skip(skip).limit(limit)
    posts = []
    async for doc in posts_cursor:
        posts.append({
            'id': str(doc['_id']),
            'title': doc.get('title', ''),
            'image_url': doc.get('image_url', ''),
            'category': doc.get('category', ''),
            'file_deeplink': doc.get('file_deeplink', ''),
            'bot_username': doc.get('bot_username', ''),
            'views': doc.get('views', 0),
            'reactions': doc.get('reactions', {"❤️": 0, "👍": 0, "🔥": 0, "💦": 0})
        })

    # Get unique categories
    categories = ['All']
    unique_cats = await async_mongo_db.posts.distinct('category')
    for cat in unique_cats:
        if cat and cat not in categories:
            categories.append(cat)

    return web.json_response({
        'posts': posts,
        'categories': categories,
        'page': page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    })

@routes.post("/api/view-post")
async def api_view_post_handler(request: web.Request):
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        post_id = data.get('post_id')
        if not post_id:
            return web.json_response({"success": False, "error": "Missing post_id"}, status=400)
            
        await async_mongo_db.posts.update_one(
            {"_id": post_id},
            {"$inc": {"views": 10}}
        )
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=500)

@routes.post("/api/react-post")
async def api_react_post_handler(request: web.Request):
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        post_id = data.get('post_id')
        emoji = data.get('emoji')
        
        if not post_id or not emoji:
            return web.json_response({"success": False, "error": "Missing post_id or emoji"}, status=400)
            
        # Ensure emoji is valid
        if emoji not in ["❤️", "👍", "🔥", "💦"]:
            return web.json_response({"success": False, "error": "Invalid emoji"}, status=400)
            
        await async_mongo_db.posts.update_one(
            {"_id": post_id},
            {"$inc": {f"reactions.{emoji}": 1}}
        )
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=500)



@routes.get("/api/check-vip")
async def api_check_vip_route_handler(request: web.Request):
    from plugins.clone import async_mongo_db
    import time

    uid = request.rel_url.query.get('uid', '')
    bot_username = request.rel_url.query.get('bot', '')

    if not uid or not bot_username:
        return web.json_response({'is_vip': False})

    bot_doc = await async_mongo_db.bots.find_one({"username": bot_username})
    if not bot_doc:
        return web.json_response({'is_vip': False})

    bot_id = bot_doc["bot_id"]
    vip_user = await async_mongo_db.vip_users.find_one({"bot_id": int(bot_id), "user_id": int(uid)})

    is_user_vip = False
    if vip_user:
        expiry = vip_user.get("expiry")
        if expiry is None or time.time() < expiry:
            is_user_vip = True

    return web.json_response({'is_vip': is_user_vip})


# ─── GDrive Video Feed (for React Native App) ────────────────────────────────

CLOUDFLARE_WORKER_URL = "https://appvideo.solankipriyanshu94.workers.dev"

def _get_gdrive_service_sync():
    """Returns authenticated Google Drive service."""
    import os
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials

    scopes = ['https://www.googleapis.com/auth/drive']
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    elif os.path.exists('service_account.json'):
        creds = service_account.Credentials.from_service_account_file(
            'service_account.json', scopes=scopes
        )
    else:
        raise FileNotFoundError("No Google credentials found.")
    return build('drive', 'v3', credentials=creds)


def _list_gdrive_files_sync(folder_id, page_size=50):
    try:
        service = _get_gdrive_service_sync()
        query = f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query,
            pageSize=page_size,
            fields="files(id, name, description, mimeType, createdTime, thumbnailLink, appProperties)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        logging.error(f"GDrive list files error: {e}")
        return []


def _list_gdrive_subfolders_sync(parent_folder_id):
    try:
        service = _get_gdrive_service_sync()
        query = f"'{parent_folder_id}' in parents and trashed=false and mimeType = 'application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query, pageSize=100,
            fields="files(id, name, description)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        logging.error(f"GDrive list subfolders error: {e}")
        return []


def _get_aesthetic_thumbnail(title, original_thumbnail):
    t = (title or "").lower()
    # If it is a real non-default image link, use it
    if original_thumbnail and "unsplash.com/photo-1618005182384" not in original_thumbnail and original_thumbnail.startswith("http"):
        return original_thumbnail

    # Keyword matched sexy/adult assets
    if any(x in t for x in ["nud", "sex", "fuck", "girl", "hot", "bhabhi", "aunty", "nude", "desi"]):
        adults = [
            "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500&auto=format&fit=crop&q=60",
            "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=500&auto=format&fit=crop&q=60",
            "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=500&auto=format&fit=crop&q=60",
            "https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d?w=500&auto=format&fit=crop&q=60"
        ]
        val = sum(ord(c) for c in t)
        return adults[val % len(adults)]

    # Tech collections
    if any(x in t for x in ["tech", "code", "ai", "cyber"]):
        return "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=500&auto=format&fit=crop&q=60"

    # Music/Dance collections
    if any(x in t for x in ["music", "song", "dance"]):
        return "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500&auto=format&fit=crop&q=60"

    # Fallback general collection
    general = [
        "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=500&auto=format&fit=crop&q=60",
        "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&auto=format&fit=crop&q=60"
    ]
    val = sum(ord(c) for c in t)
    return general[val % len(general)]


def _gdrive_file_to_post(gfile, category_name="All"):
    props = gfile.get('appProperties') or {}
    file_id = gfile['id']
    title = props.get('title') or gfile.get('description') or gfile['name'].replace('.dat', '').replace('-', ' ').replace('_', ' ').title()
    thumbnail = _get_aesthetic_thumbnail(title, props.get('thumbnail_url') or gfile.get('thumbnailLink'))

    raw_ids = props.get('gdrive_file_ids', '')
    if raw_ids and isinstance(raw_ids, str):
        gdrive_file_ids = [x.strip() for x in raw_ids.split(',') if x.strip()]
    else:
        gdrive_file_ids = [file_id]

    return {
        "id": file_id,
        "title": title,
        "category": category_name,
        "views": int(props.get('views', 0)),
        "duration": props.get('duration', '03:15'),
        "image_url": thumbnail,
        "stream_url": f"{CLOUDFLARE_WORKER_URL}/video.mp4?fileId={file_id}",
        "is_gdrive": True,
        "gdrive_file_id": file_id,
        "gdrive_file_ids": gdrive_file_ids,
        "is_paid": props.get('is_paid', 'false') == 'true',
        "bot_username": props.get('bot_username', 'ViralVideosBot'),
        "reactions": {"❤️": 0, "👍": 0, "🔥": 0, "💦": 0},
        "thumbnails": [thumbnail],
    }


@routes.get("/gdrive-portal-data", allow_head=True)
async def gdrive_portal_data_handler(request: web.Request):
    """GDrive-based video feed joined with MongoDB metadata."""
    import asyncio
    import math
    from config import GDRIVE_FOLDER_ID

    category = request.rel_url.query.get('category', 'All')
    limit = int(request.rel_url.query.get('limit', 30))
    page = int(request.rel_url.query.get('page', 1))

    try:
        loop = asyncio.get_event_loop()

        if category == 'All':
            files = await loop.run_in_executor(None, lambda: _list_gdrive_files_sync(GDRIVE_FOLDER_ID, limit * page))
            posts = [_gdrive_file_to_post(f, 'All') for f in files]
        else:
            subfolders = await loop.run_in_executor(None, lambda: _list_gdrive_subfolders_sync(GDRIVE_FOLDER_ID))
            matched = next((f for f in subfolders if f['id'] == category or f['name'].lower() == category.lower()), None)
            if matched:
                files = await loop.run_in_executor(None, lambda: _list_gdrive_files_sync(matched['id'], limit * page))
                posts = [_gdrive_file_to_post(f, matched['name']) for f in files]
            else:
                files = await loop.run_in_executor(None, lambda: _list_gdrive_files_sync(GDRIVE_FOLDER_ID, limit * page))
                posts = [_gdrive_file_to_post(f, 'All') for f in files]

        # ── MongoDB Integration: Fetch actual captions & images ──
        from plugins.clone import async_mongo_db
        file_ids = [p['gdrive_file_id'] for p in posts if p.get('gdrive_file_id')]
        if file_ids:
            cursor = async_mongo_db.posts.find({
                "$or": [
                    {"gdrive_file_id": {"$in": file_ids}},
                    {"gdrive_file_ids": {"$in": file_ids}}
                ]
            })
            db_posts = await cursor.to_list(length=100)
            
            db_map = {}
            for db_p in db_posts:
                gid = db_p.get("gdrive_file_id")
                if gid:
                    db_map[gid] = db_p
                gids = db_p.get("gdrive_file_ids") or []
                for sub_gid in gids:
                    db_map[sub_gid] = db_p

            for p in posts:
                match = db_map.get(p['gdrive_file_id'])
                if match:
                    p['title'] = match.get('title') or p['title']
                    p['image_url'] = _get_aesthetic_thumbnail(p['title'], match.get('image_url'))
                    p['views'] = int(match.get('views', 0)) or p['views']
                    p['is_paid'] = bool(match.get('is_paid', False))
                    p['thumbnails'] = match.get('thumbnails') or [p['image_url']]
                else:
                    p['thumbnails'] = [p['image_url']]

            # Sort all fetched posts by views count descending (highest views first)
            posts.sort(key=lambda x: x.get('views', 0), reverse=True)

        # Fetch unique categories dynamically from GDrive subfolders
        subfolders = await loop.run_in_executor(None, lambda: _list_gdrive_subfolders_sync(GDRIVE_FOLDER_ID))
        categories = ['All'] + [f['name'] for f in subfolders]

        start = (page - 1) * limit
        paged = posts[start:start + limit]
        total_pages = max(1, math.ceil(len(posts) / limit))

        return web.json_response({
            "status": "ok",
            "posts": paged,
            "categories": categories,
            "page": page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        })

    except Exception as e:
        logging.error(f"/gdrive-portal-data error: {e}")
        return web.json_response({"error": str(e), "posts": [], "categories": ['All']}, status=500)


@routes.get("/gdrive-folders", allow_head=True)
async def gdrive_folders_handler(request: web.Request):
    """Returns GDrive sub-folders as categories for the React Native app."""
    import asyncio
    from config import GDRIVE_FOLDER_ID

    try:
        loop = asyncio.get_event_loop()
        folders = await loop.run_in_executor(None, lambda: _list_gdrive_subfolders_sync(GDRIVE_FOLDER_ID))
        categories = [{"id": f['id'], "name": f['name']} for f in folders]
        return web.json_response({"categories": categories})
    except Exception as e:
        return web.json_response({"error": str(e), "categories": []}, status=500)
