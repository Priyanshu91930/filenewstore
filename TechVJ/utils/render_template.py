# Don't Remove Credit @viralverse0909
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @Brainaxe190

import jinja2
from config import LOG_CHANNEL, URL
from TechVJ.bot import StreamBot
from TechVJ.utils.human_readable import humanbytes
from TechVJ.utils.file_properties import get_file_ids
from TechVJ.server.exceptions import InvalidHash
import urllib.parse
import logging
import aiohttp


async def render_page(id, secure_hash, src=None, bot=None, filename=None):
    if isinstance(id, str):
        from plugins.clone import async_mongo_db
        from pyrogram.file_id import FileId
        import mimetypes
        file_doc = await async_mongo_db.clone_files.find_one({"_id": id})
        if not file_doc:
            raise InvalidHash
        file_data = FileId.decode(file_doc["file_id"])
        safe_hash = secure_hash or ""
        setattr(file_data, "unique_id", safe_hash + "xxxxx")
        resolved_filename = filename or getattr(file_data, "file_name", "Cloned File")
        setattr(file_data, "file_size", file_doc.get("file_size") or 0)
        guessed_mime = mimetypes.guess_type(resolved_filename)[0] or "application/octet-stream"
        setattr(file_data, "mime_type", file_doc.get("mime_type") or guessed_mime)
    else:
        file = await StreamBot.get_messages(int(LOG_CHANNEL), int(id))
        file_data = await get_file_ids(StreamBot, int(LOG_CHANNEL), int(id))
        resolved_filename = filename or file_data.file_name or ""

    if not hasattr(file_data, "file_size") or file_data.file_size is None:
        setattr(file_data, "file_size", 0)
    if not hasattr(file_data, "mime_type") or not file_data.mime_type:
        import mimetypes
        guessed_mime = mimetypes.guess_type(resolved_filename)[0] or "application/octet-stream"
        setattr(file_data, "mime_type", guessed_mime)

    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    src = urllib.parse.urljoin(
        URL,
        f"{id}/{urllib.parse.quote_plus(resolved_filename)}?hash={secure_hash}",
    )
    if bot:
        src += f"&bot={bot}"

    tag = file_data.mime_type.split("/")[0].strip()
    filename_lower = resolved_filename.lower()
    if tag not in ["video", "audio"]:
        if filename_lower.endswith(('.mkv', '.mp4', '.webm', '.avi', '.mov', '.flv', '.3gp', '.mpeg', '.mpg')):
            tag = "video"
            setattr(file_data, "mime_type", "video/mp4")
        elif filename_lower.endswith(('.mp3', '.ogg', '.wav', '.flac', '.m4a', '.aac')):
            tag = "audio"
            setattr(file_data, "mime_type", "audio/mpeg")

    file_size = humanbytes(file_data.file_size)
    if tag in ["video", "audio"]:
        template_file = "TechVJ/template/req.html"
    else:
        template_file = "TechVJ/template/dl.html"
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                file_size = humanbytes(int(u.headers.get("Content-Length")))

    with open(template_file) as f:
        template = jinja2.Template(f.read())

    f_name = resolved_filename or ""
    file_name = f_name.replace("_", " ")

    return template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        file_unique_id=file_data.unique_id,
    )
    return html
