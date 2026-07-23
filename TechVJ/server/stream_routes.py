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
    limit = int(request.rel_url.query.get('limit', 100))

    query = {"is_gdrive": True}
    if category != 'All':
        query['category'] = category
    if search:
        query['title'] = {'$regex': search, '$options': 'i'}

    total_posts = await async_mongo_db.posts.count_documents(query)
    total_pages = math.ceil(total_posts / limit) or 1
    page = max(1, min(page, total_pages))
    skip = (page - 1) * limit

    posts_cursor = async_mongo_db.posts.find(query).sort([('is_paid', -1), ('created_at', -1)]).skip(skip).limit(limit)
    posts = []
    async for doc in posts_cursor:
        posts.append({
            'id': str(doc['_id']),
            'title': doc.get('title', ''),
            'image_url': _normalize_image_url(doc.get('image_url', '')),
            'category': doc.get('category', ''),
            'file_deeplink': doc.get('file_deeplink', ''),
            'bot_username': doc.get('bot_username', ''),
            'views': doc.get('views', 0),
            'reactions': doc.get('reactions', {"❤️": 0, "👍": 0, "🔥": 0, "💦": 0}),
            'is_paid': bool(doc.get('is_paid', False)),
            'gdrive_file_id': doc.get('gdrive_file_id', ''),
            'gdrive_file_ids': doc.get('gdrive_file_ids', []),
            'is_batch': bool(doc.get('is_batch', False)),
            'caption': doc.get('caption', doc.get('title', '')),
            'is_gdrive': bool(doc.get('is_gdrive', False)),
            'thumbnails': [_normalize_image_url(t) for t in doc.get('thumbnails', [])] if doc.get('thumbnails') else [_normalize_image_url(doc.get('image_url', ''))]
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

def _normalize_image_url(url_str):
    if not url_str:
        return 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80'
    
    if "miniapp.anihubyt.com/stream" in url_str:
        url_str = url_str.replace("https://miniapp.anihubyt.com/stream", f"{CLOUDFLARE_WORKER_URL}/stream")
        
    if url_str.startswith("/static/"):
        from config import URL
        base_url = (URL or "https://miniapp.anihubyt.com").rstrip("/")
        url_str = f"{base_url}{url_str}"
        
    return url_str


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
    thumbnail = _normalize_image_url(_get_aesthetic_thumbnail(title, props.get('thumbnail_url') or gfile.get('thumbnailLink')))

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
                    p['image_url'] = _normalize_image_url(_get_aesthetic_thumbnail(p['title'], match.get('image_url')))
                    p['views'] = int(match.get('views', 0)) or p['views']
                    p['is_paid'] = bool(match.get('is_paid', False))
                    p['thumbnails'] = [_normalize_image_url(t) for t in match.get('thumbnails', [])] if match.get('thumbnails') else [p['image_url']]
                    if match.get('duration'):
                        p['duration'] = match.get('duration')
                else:
                    p['image_url'] = _normalize_image_url(p['image_url'])
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


@routes.get("/payment-config")
async def payment_config_handler(request: web.Request):
    from config import RAZORPAY_KEY_ID
    return web.json_response({"key_id": RAZORPAY_KEY_ID})


@routes.post("/verify-payment")
async def verify_payment_handler(request: web.Request):
    import time
    from config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
    from plugins.clone import async_mongo_db
    import aiohttp

    try:
        data = await request.json()
        payment_id = data.get("payment_id")
        plan_duration = data.get("plan_duration", "1 Month")
        price_str = data.get("price", "199").replace("₹", "").strip()
        expected_price = int(price_str)
        user_id = int(data.get("user_id", 8494193109))
        bot_id = int(data.get("bot_id", 7687702448))

        if not payment_id:
            return web.json_response({"status": "error", "message": "Missing payment_id"}, status=400)

        # Verify payment with Razorpay
        url = f"https://api.razorpay.com/v1/payments/{payment_id}"
        auth = aiohttp.BasicAuth(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=auth) as resp:
                if resp.status == 200:
                    resp_data = await resp.json()
                    status = resp_data.get('status')
                    amount_paid = int(resp_data.get('amount'))  # In paise

                    # Direct payment check
                    if status in ('captured', 'authorized') and amount_paid == (expected_price * 100):
                        # Upgrade user to VIP in MongoDB
                        now = time.time()
                        if "day" in plan_duration.lower():
                            expiry = now + 86400
                        elif "week" in plan_duration.lower():
                            expiry = now + 86400 * 7
                        elif "month" in plan_duration.lower():
                            if "3" in plan_duration:
                                expiry = now + 86400 * 30 * 3
                            elif "6" in plan_duration:
                                expiry = now + 86400 * 30 * 6
                            else:
                                expiry = now + 86400 * 30
                        elif "lifetime" in plan_duration.lower():
                            expiry = None
                        else:
                            expiry = now + 86400 * 30

                        await async_mongo_db.vip_users.update_one(
                            {"bot_id": bot_id, "user_id": user_id},
                            {"$set": {"expiry": expiry, "payment_id": payment_id, "updated_at": now}},
                            upsert=True
                        )

                        # If email provided (app user), also link VIP by email
                        email = data.get("email", "").strip().lower()
                        if email:
                            await async_mongo_db.vip_users.update_one(
                                {"email": email},
                                {"$set": {
                                    "email": email,
                                    "expiry": expiry,
                                    "payment_id": payment_id,
                                    "plan_duration": plan_duration,
                                    "activated_at": now,
                                    "updated_at": now,
                                }},
                                upsert=True
                            )
                            # Also mark app_users as VIP
                            await async_mongo_db.app_users.update_one(
                                {"email": email},
                                {"$set": {"is_vip": True, "vip_since": now}}
                            )

                        return web.json_response({
                            "status": "success",
                            "message": f"Payment verified! VIP status activated for {plan_duration}."
                        })
                    else:
                        return web.json_response({
                            "status": "error",
                            "message": f"Payment verification failed: Status is {status}, Expected: {expected_price * 100}, Paid: {amount_paid}"
                        }, status=400)
                else:
                    return web.json_response({
                        "status": "error",
                        "message": f"Failed to connect to Razorpay. Response status: {resp.status}"
                    }, status=400)
    except Exception as e:
        logging.error(f"/verify-payment error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/register-user")
async def register_user_handler(request: web.Request):
    """Register or update a user in MongoDB after Google Sign-In."""
    import time
    from plugins.clone import async_mongo_db

    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        name = data.get("name", "")
        photo = data.get("photo", "")
        google_id = data.get("google_id", "")

        if not email:
            return web.json_response({"status": "error", "message": "Email is required"}, status=400)

        now = time.time()

        # Upsert user record by email
        await async_mongo_db.app_users.update_one(
            {"email": email},
            {"$set": {
                "name": name,
                "photo": photo,
                "google_id": google_id,
                "last_login": now,
            }, "$setOnInsert": {
                "email": email,
                "created_at": now,
                "is_vip": False,
            }},
            upsert=True
        )

        # Fetch updated user
        user = await async_mongo_db.app_users.find_one({"email": email}, {"_id": 0})

        # Check VIP status from vip_users collection (linked by email)
        vip = await async_mongo_db.vip_users.find_one({"email": email})
        is_vip = False
        vip_expiry = None
        if vip:
            expiry = vip.get("expiry")
            if expiry is None:
                is_vip = True
            elif time.time() < expiry:
                is_vip = True
                vip_expiry = expiry

        return web.json_response({
            "status": "ok",
            "user": {
                "email": email,
                "name": name,
                "photo": photo,
                "is_vip": is_vip,
                "vip_expiry": vip_expiry,
            }
        })

    except Exception as e:
        logging.error(f"/register-user error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user-status")
async def user_status_handler(request: web.Request):
    """Get VIP status of a user by email."""
    import time
    from plugins.clone import async_mongo_db

    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email param required"}, status=400)

        user = await async_mongo_db.app_users.find_one({"email": email}, {"_id": 0})
        if not user:
            return web.json_response({"status": "error", "message": "User not found"}, status=404)

        vip = await async_mongo_db.vip_users.find_one({"email": email})
        is_vip = False
        vip_expiry = None
        if vip:
            expiry = vip.get("expiry")
            if expiry is None:
                is_vip = True
            elif time.time() < expiry:
                is_vip = True
                vip_expiry = expiry

        return web.json_response({
            "status": "ok",
            "email": email,
            "name": user.get("name", ""),
            "photo": user.get("photo", ""),
            "is_vip": is_vip,
            "vip_expiry": vip_expiry,
        })

    except Exception as e:
        logging.error(f"/user-status error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


# ─── USER ACTIVITY ENDPOINTS ────────────────────────────────────────────

@routes.post("/user/activity/like")
async def toggle_like(request: web.Request):
    """Toggle like on a video. Creates/removes document in user_liked_videos."""
    import time
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        video_id = data.get("video_id", "")
        title = data.get("title", "")
        thumbnail = data.get("thumbnail", "")
        if not email or not video_id:
            return web.json_response({"status": "error", "message": "email and video_id required"}, status=400)

        existing = await async_mongo_db.user_liked_videos.find_one({"email": email, "video_id": video_id})
        if existing:
            await async_mongo_db.user_liked_videos.delete_one({"email": email, "video_id": video_id})
            liked = False
        else:
            await async_mongo_db.user_liked_videos.insert_one({
                "email": email, "video_id": video_id,
                "title": title, "thumbnail": thumbnail,
                "liked_at": time.time()
            })
            liked = True
        count = await async_mongo_db.user_liked_videos.count_documents({"email": email})
        return web.json_response({"status": "ok", "liked": liked, "count": count})
    except Exception as e:
        logging.error(f"/user/activity/like error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/activity/likes")
async def get_likes(request: web.Request):
    """Get all liked videos for a user."""
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)
        cursor = async_mongo_db.user_liked_videos.find({"email": email}, {"_id": 0}).sort("liked_at", -1)
        videos = await cursor.to_list(length=200)
        return web.json_response({"status": "ok", "count": len(videos), "videos": videos})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/user/activity/save")
async def toggle_save(request: web.Request):
    """Toggle save/watch-later on a video."""
    import time
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        video_id = data.get("video_id", "")
        title = data.get("title", "")
        thumbnail = data.get("thumbnail", "")
        if not email or not video_id:
            return web.json_response({"status": "error", "message": "email and video_id required"}, status=400)

        existing = await async_mongo_db.user_saved_videos.find_one({"email": email, "video_id": video_id})
        if existing:
            await async_mongo_db.user_saved_videos.delete_one({"email": email, "video_id": video_id})
            saved = False
        else:
            await async_mongo_db.user_saved_videos.insert_one({
                "email": email, "video_id": video_id,
                "title": title, "thumbnail": thumbnail,
                "saved_at": time.time()
            })
            saved = True
        count = await async_mongo_db.user_saved_videos.count_documents({"email": email})
        return web.json_response({"status": "ok", "saved": saved, "count": count})
    except Exception as e:
        logging.error(f"/user/activity/save error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/activity/saved")
async def get_saved(request: web.Request):
    """Get all saved videos for a user."""
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)
        cursor = async_mongo_db.user_saved_videos.find({"email": email}, {"_id": 0}).sort("saved_at", -1)
        videos = await cursor.to_list(length=200)
        return web.json_response({"status": "ok", "count": len(videos), "videos": videos})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/user/activity/watch")
async def add_watch_history(request: web.Request):
    """Record a video watch event. Keeps latest 500 per user."""
    import time
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        video_id = data.get("video_id", "")
        title = data.get("title", "")
        thumbnail = data.get("thumbnail", "")
        if not email or not video_id:
            return web.json_response({"status": "error", "message": "email and video_id required"}, status=400)

        # Update or insert (upsert), update watched_at timestamp
        await async_mongo_db.user_watch_history.update_one(
            {"email": email, "video_id": video_id},
            {"$set": {"title": title, "thumbnail": thumbnail, "watched_at": time.time()}},
            upsert=True
        )
        count = await async_mongo_db.user_watch_history.count_documents({"email": email})
        return web.json_response({"status": "ok", "count": count})
    except Exception as e:
        logging.error(f"/user/activity/watch error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/activity/history")
async def get_watch_history(request: web.Request):
    """Get watch history for a user."""
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)
        cursor = async_mongo_db.user_watch_history.find({"email": email}, {"_id": 0}).sort("watched_at", -1)
        videos = await cursor.to_list(length=100)
        return web.json_response({"status": "ok", "count": len(videos), "videos": videos})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/stats")
async def get_user_stats(request: web.Request):
    """Get all activity counts + VIP status + expiry for a user."""
    import time
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)

        liked_count, saved_count, history_count, download_count = await asyncio.gather(
            async_mongo_db.user_liked_videos.count_documents({"email": email}),
            async_mongo_db.user_saved_videos.count_documents({"email": email}),
            async_mongo_db.user_watch_history.count_documents({"email": email}),
            async_mongo_db.user_downloads.count_documents({"email": email}),
        )

        # VIP check
        vip = await async_mongo_db.vip_users.find_one({"email": email})
        is_vip = False
        vip_expiry_ts = None
        vip_expiry_str = None
        if vip:
            expiry = vip.get("expiry")
            if expiry is None:
                is_vip = True
                vip_expiry_str = "Lifetime"
            elif time.time() < expiry:
                is_vip = True
                vip_expiry_ts = expiry
                from datetime import datetime
                dt = datetime.fromtimestamp(expiry)
                vip_expiry_str = dt.strftime("%d %b %Y, %I:%M %p")

        user_record = await async_mongo_db.user.find_one({"email": email})
        allowed_views = user_record.get("allowed_views", 0) if user_record else 0

        return web.json_response({
            "status": "ok",
            "liked_count": liked_count,
            "saved_count": saved_count,
            "history_count": history_count,
            "download_count": download_count,
            "downloads_enabled": is_vip,
            "is_vip": is_vip,
            "vip_expiry": vip_expiry_str,
            "allowed_views": allowed_views,
        })
    except Exception as e:
        logging.error(f"/user/stats error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/user/ad-watched")
async def register_ad_watched(request: web.Request):
    """Credit 3 video views to free user after ad completion."""
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)

        await async_mongo_db.user.update_one(
            {"email": email},
            {"$inc": {"allowed_views": 3}},
            upsert=True
        )

        user_record = await async_mongo_db.user.find_one({"email": email})
        allowed_views = user_record.get("allowed_views", 0) if user_record else 0

        return web.json_response({
            "status": "ok",
            "message": "3 views credited successfully!",
            "allowed_views": allowed_views
        })
    except Exception as e:
        logging.error(f"/user/ad-watched error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/verify/generate-link")
async def generate_verification_shortlink(request: web.Request):
    """Generates a shortened link that redirects back to the app schema after completion."""
    from utils import get_verify_shorted_link
    from plugins.clone import async_mongo_db
    import time
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)
            
        token = data.get("token")
        if not token:
            return web.json_response({"status": "error", "message": "token required"}, status=400)
            
        # Target redirect URL (backend verify endpoint that registers view and redirects to app deep link)
        target_url = f"https://miniapp.anihubyt.com/verify/complete?email={email}&token={token}"
        
        # Get rotated shortlink based on user's daily verification count
        from utils import get_tma_shortlink
        from config import BOT_USERNAME
        
        # Get numeric user_id if exists in database or fall back to hash
        user_rec = await async_mongo_db.user.find_one({"email": email})
        user_id = user_rec.get("user_id", 999999) if user_rec else 999999
        
        short_link = await get_tma_shortlink(user_id=user_id, token=token, file_data="", bot_username=BOT_USERNAME, custom_link=target_url)
        
        # Save token in DB for validation on redirection
        await async_mongo_db.user_verifications.update_one(
            {"email": email},
            {"$set": {"token": token, "verified": False, "created_at": time.time()}},
            upsert=True
        )
        
        return web.json_response({"status": "ok", "shortlink": short_link})
    except Exception as e:
        logging.error(f"/verify/generate-link error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/verify/complete")
async def verification_complete_redirect(request: web.Request):
    """Processes verification completion, credits views, deletes the token, and redirects back to the app."""
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        token = request.rel_url.query.get("token", "")
        
        record = await async_mongo_db.user_verifications.find_one({"email": email})
        
        # Security Check: Only allow if token matches and token hasn't already been consumed/marked verified
        if record and record.get("token") == token:
            if record.get("verified") is True:
                # Token already consumed
                return web.Response(text="Verification link already consumed/expired. Please generate a new one.", status=400)
            
            # Consume token by marking verified (this is retrieved once by polling check-status)
            await async_mongo_db.user_verifications.update_one(
                {"email": email},
                {"$set": {"verified": True}}
            )
            # Credit 3 views
            await async_mongo_db.user.update_one(
                {"email": email},
                {"$inc": {"allowed_views": 3}},
                upsert=True
            )
            
            # Increment daily verify count to trigger shortlink rotation for next time
            try:
                import pytz
                from datetime import datetime
                tz = pytz.timezone('Asia/Kolkata')
                today_str = datetime.now(tz).strftime('%Y-%m-%d')
                user_rec = await async_mongo_db.user.find_one({"email": email})
                user_id = user_rec.get("user_id", 999999) if user_rec else 999999
                
                # Update main bot verification count (bot_id = 999999999 as configured in rotation utils)
                await async_mongo_db.tma_verify_count.update_one(
                    {"bot_id": 999999999, "user_id": user_id, "date": today_str},
                    {"$inc": {"count": 1}},
                    upsert=True
                )
            except Exception as ex:
                logging.error(f"Error updating verify count for rotation: {ex}")
            
            # Redirect back to the app using custom URI scheme (viralverse://)
            raise web.HTTPFound("viralverse://home?verified=true")
        else:
            return web.Response(text="Invalid or expired verification token.", status=400)
            
    except web.HTTPFound as redirect:
        raise redirect
    except Exception as e:
        logging.error(f"/verify/complete error: {e}")
        return web.Response(text=f"Verification Error: {str(e)}", status=500)


@routes.get("/verify/check-status")
async def check_verification_status(request: web.Request):
    """Allows app to poll status if deep link redirection fails or to verify view credits."""
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        record = await async_mongo_db.user_verifications.find_one({"email": email})
        
        if record and record.get("verified") is True:
            # Clear status so it isn't reused
            await async_mongo_db.user_verifications.delete_one({"email": email})
            
            user_record = await async_mongo_db.user.find_one({"email": email})
            allowed_views = user_record.get("allowed_views", 0) if user_record else 0
            
            return web.json_response({"status": "verified", "allowed_views": allowed_views})
            
        return web.json_response({"status": "pending"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/user/consume-view")
async def consume_user_view(request: web.Request):
    """Decrement allowed_views by 1 when a free user plays a video."""
    import time
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)

        vip = await async_mongo_db.vip_users.find_one({"email": email})
        is_vip = False
        if vip:
            expiry = vip.get("expiry")
            is_vip = expiry is None or time.time() < expiry

        if is_vip:
            return web.json_response({"status": "ok", "is_vip": True})

        user_record = await async_mongo_db.user.find_one({"email": email})
        current_views = user_record.get("allowed_views", 0) if user_record else 0

        if current_views > 0:
            await async_mongo_db.user.update_one(
                {"email": email},
                {"$inc": {"allowed_views": -1}}
            )
            new_views = current_views - 1
        else:
            new_views = 0

        return web.json_response({
            "status": "ok",
            "allowed_views": new_views
        })
    except Exception as e:
        logging.error(f"/user/consume-view error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/user/activity/download")
async def add_download(request: web.Request):
    """Record a downloaded video in user_downloads (VIP only). Auto-rejects if not VIP."""
    import time
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        video_id = data.get("video_id", "")
        title = data.get("title", "")
        thumbnail = data.get("thumbnail", "")
        file_url = data.get("file_url", "")

        if not email or not video_id:
            return web.json_response({"status": "error", "message": "email and video_id required"}, status=400)

        # VIP check — only VIP users can download
        vip = await async_mongo_db.vip_users.find_one({"email": email})
        is_vip = False
        if vip:
            expiry = vip.get("expiry")
            is_vip = expiry is None or time.time() < expiry

        if not is_vip:
            return web.json_response({
                "status": "error",
                "message": "VIP subscription required for offline downloads."
            }, status=403)

        # Upsert download record (no duplicate entries for same video)
        now = time.time()
        await async_mongo_db.user_downloads.update_one(
            {"email": email, "video_id": video_id},
            {"$set": {
                "title": title,
                "thumbnail": thumbnail,
                "file_url": file_url,
                "downloaded_at": now,
            }},
            upsert=True
        )
        count = await async_mongo_db.user_downloads.count_documents({"email": email})
        return web.json_response({"status": "ok", "count": count})
    except Exception as e:
        logging.error(f"/user/activity/download error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/activity/downloads")
async def get_downloads(request: web.Request):
    """Get all downloaded videos for a user."""
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)
        cursor = async_mongo_db.user_downloads.find({"email": email}, {"_id": 0}).sort("downloaded_at", -1)
        videos = await cursor.to_list(length=200)
        return web.json_response({"status": "ok", "count": len(videos), "videos": videos})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.delete("/user/activity/download")
async def remove_download(request: web.Request):
    """Remove a downloaded video from user_downloads."""
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        existing = await async_mongo_db.user_saved_videos.find_one({"email": email, "video_id": video_id})
        if existing:
            await async_mongo_db.user_saved_videos.delete_one({"email": email, "video_id": video_id})
            saved = False
        else:
            await async_mongo_db.user_saved_videos.insert_one({
                "email": email, "video_id": video_id,
                "title": title, "thumbnail": thumbnail,
                "saved_at": time.time()
            })
            saved = True
        count = await async_mongo_db.user_saved_videos.count_documents({"email": email})
        return web.json_response({"status": "ok", "saved": saved, "count": count})
    except Exception as e:
        logging.error(f"/user/activity/save error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/activity/saved")
async def get_saved(request: web.Request):
    """Get all saved videos for a user."""
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)
        cursor = async_mongo_db.user_saved_videos.find({"email": email}, {"_id": 0}).sort("saved_at", -1)
        videos = await cursor.to_list(length=200)
        return web.json_response({"status": "ok", "count": len(videos), "videos": videos})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/user/activity/watch")
async def add_watch_history(request: web.Request):
    """Record a video watch event. Keeps latest 500 per user."""
    import time
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        video_id = data.get("video_id", "")
        title = data.get("title", "")
        thumbnail = data.get("thumbnail", "")
        if not email or not video_id:
            return web.json_response({"status": "error", "message": "email and video_id required"}, status=400)

        # Update or insert (upsert), update watched_at timestamp
        await async_mongo_db.user_watch_history.update_one(
            {"email": email, "video_id": video_id},
            {"$set": {"title": title, "thumbnail": thumbnail, "watched_at": time.time()}},
            upsert=True
        )
        count = await async_mongo_db.user_watch_history.count_documents({"email": email})
        return web.json_response({"status": "ok", "count": count})
    except Exception as e:
        logging.error(f"/user/activity/watch error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/activity/history")
async def get_watch_history(request: web.Request):
    """Get watch history for a user."""
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)
        cursor = async_mongo_db.user_watch_history.find({"email": email}, {"_id": 0}).sort("watched_at", -1)
        videos = await cursor.to_list(length=100)
        return web.json_response({"status": "ok", "count": len(videos), "videos": videos})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)



@routes.post("/user/activity/download")
async def add_download(request: web.Request):
    """Record a downloaded video in user_downloads (VIP only). Auto-rejects if not VIP."""
    import time
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        video_id = data.get("video_id", "")
        title = data.get("title", "")
        thumbnail = data.get("thumbnail", "")
        file_url = data.get("file_url", "")

        if not email or not video_id:
            return web.json_response({"status": "error", "message": "email and video_id required"}, status=400)

        # VIP check — only VIP users can download
        vip = await async_mongo_db.vip_users.find_one({"email": email})
        is_vip = False
        if vip:
            expiry = vip.get("expiry")
            is_vip = expiry is None or time.time() < expiry

        if not is_vip:
            return web.json_response({
                "status": "error",
                "message": "VIP subscription required for offline downloads."
            }, status=403)

        # Upsert download record (no duplicate entries for same video)
        now = time.time()
        await async_mongo_db.user_downloads.update_one(
            {"email": email, "video_id": video_id},
            {"$set": {
                "title": title,
                "thumbnail": thumbnail,
                "file_url": file_url,
                "downloaded_at": now,
            }},
            upsert=True
        )
        count = await async_mongo_db.user_downloads.count_documents({"email": email})
        return web.json_response({"status": "ok", "count": count})
    except Exception as e:
        logging.error(f"/user/activity/download error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/activity/downloads")
async def get_downloads(request: web.Request):
    """Get all downloaded videos for a user."""
    from plugins.clone import async_mongo_db
    try:
        email = request.rel_url.query.get("email", "").strip().lower()
        if not email:
            return web.json_response({"status": "error", "message": "email required"}, status=400)
        cursor = async_mongo_db.user_downloads.find({"email": email}, {"_id": 0}).sort("downloaded_at", -1)
        videos = await cursor.to_list(length=200)
        return web.json_response({"status": "ok", "count": len(videos), "videos": videos})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.delete("/user/activity/download")
async def remove_download(request: web.Request):
    """Remove a downloaded video from user_downloads."""
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        video_id = data.get("video_id", "")
        if not email or not video_id:
            return web.json_response({"status": "error", "message": "email and video_id required"}, status=400)
        await async_mongo_db.user_downloads.delete_one({"email": email, "video_id": video_id})
        count = await async_mongo_db.user_downloads.count_documents({"email": email})
        return web.json_response({"status": "ok", "count": count})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/user/activity/comment")
async def post_comment_endpoint(request: web.Request):
    import time
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        email = data.get("email", "").strip().lower()
        user_name = data.get("user_name", "Anonymous")
        user_avatar = data.get("user_avatar", "")
        video_id = data.get("video_id", "")
        text = data.get("text", "").strip()
        reaction = data.get("reaction", "")
        if not video_id or not text:
            return web.json_response({"status": "error", "message": "video_id and text required"}, status=400)
        await async_mongo_db.user_comments.insert_one({
            "email": email, "user_name": user_name, "user_avatar": user_avatar,
            "video_id": video_id, "text": text, "reaction": reaction, "created_at": time.time()
        })
        return web.json_response({"status": "ok"})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/activity/comments")
async def get_comments_endpoint(request: web.Request):
    from plugins.clone import async_mongo_db
    try:
        video_id = request.rel_url.query.get("video_id", "")
        cursor = async_mongo_db.user_comments.find({"video_id": video_id}, {"_id": 0}).sort("created_at", -1)
        comments = await cursor.to_list(length=100)
        return web.json_response({"status": "ok", "comments": comments})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.post("/video/react")
async def post_reaction_endpoint(request: web.Request):
    from plugins.clone import async_mongo_db
    try:
        data = await request.json()
        video_id = data.get("video_id", "")
        emoji_id = data.get("emoji_id", "")
        field = f"reactions.{emoji_id}"
        await async_mongo_db.video_reactions.update_one(
            {"video_id": video_id},
            {"$inc": {field: 1}},
            upsert=True
        )
        doc = await async_mongo_db.video_reactions.find_one({"video_id": video_id}, {"_id": 0})
        return web.json_response({"status": "ok", "reactions": doc.get("reactions", {}) if doc else {}})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/video/reactions")
async def get_reactions_endpoint(request: web.Request):
    from plugins.clone import async_mongo_db
    try:
        video_id = request.rel_url.query.get("video_id", "")
        doc = await async_mongo_db.video_reactions.find_one({"video_id": video_id}, {"_id": 0})
        reactions = doc.get("reactions", {}) if doc else {}
        return web.json_response({"status": "ok", "reactions": reactions})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


@routes.get("/user/activity/notifications")
async def get_app_notifications(request: web.Request):
    """Fetch all admin broadcasted notifications for the app."""
    from plugins.clone import async_mongo_db
    try:
        cursor = async_mongo_db.app_notifications.find({}, {"_id": 0}).sort("created_at", -1)
        notifications = await cursor.to_list(length=100)
        return web.json_response({"status": "ok", "notifications": notifications})
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)
