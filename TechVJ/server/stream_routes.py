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
                elapsed = time.time() - TMA_VERIFIED[key]
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
    
    bot_param = request.rel_url.query.get("bot")
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
        file_doc = await async_mongo_db.clone_files.find_one({"_id": id})
        if not file_doc:
            logging.debug(f"Clone file with ID {id} not found in DB")
            raise FIleNotFound
        file_id = FileId.decode(file_doc["file_id"])
        setattr(file_id, "unique_id", secure_hash + "xxxxx")
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

    mime_type = file_id.mime_type
    file_name = file_id.file_name
    disposition = "attachment"

    if mime_type:
        if not file_name:
            try:
                file_name = f"{secrets.token_hex(2)}.{mime_type.split('/')[1]}"
            except (IndexError, AttributeError):
                file_name = f"{secrets.token_hex(2)}.unknown"
    else:
        if file_name:
            mime_type = mimetypes.guess_type(file_id.file_name)[0] or "application/octet-stream"
        else:
            mime_type = "application/octet-stream"
            file_name = f"{secrets.token_hex(2)}.unknown"

    return web.Response(
        status=206 if range_header else 200,
        body=body,
        headers={
            "Content-Type": f"{mime_type}",
            "Content-Range": f"bytes {from_bytes}-{until_bytes}/{file_size}",
            "Content-Length": str(req_length),
            "Content-Disposition": f'{disposition}; filename="{file_name}"',
            "Accept-Ranges": "bytes",
            "X-Accel-Buffering": "no",
        },
    )
