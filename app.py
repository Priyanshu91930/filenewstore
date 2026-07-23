from flask import Flask, render_template, request, jsonify, send_from_directory
from urllib.parse import unquote
import os, sys

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    """Serve the File Portal website."""
    return send_from_directory('static/website', 'index.html')

@app.route('/tma')
def mini_app():
    """Serve the Telegram Mini App page.

    Query params:
      uid   - Telegram user_id (added by bot when generating the WebApp button)
      token - HMAC-signed verification token (added by bot)
      file  - URL-encoded raw /start parameter (the file data, e.g. base64 file id)
    """
    from config import MONETAG_ZONE_ID, BOT_USERNAME
    from utils import get_tma_shortlink
    import asyncio

    uid          = request.args.get('uid', '')
    token        = request.args.get('token', '')
    file_data    = unquote(request.args.get('file', ''))   # raw /start param
    bot_username = request.args.get('bot', BOT_USERNAME)
    zone         = MONETAG_ZONE_ID or ''

    short_link   = ""
    if uid and token and file_data:
        try:
            # Use a timeout so a slow/blocked shortlink API won't freeze the page
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                short_link = loop.run_until_complete(
                    asyncio.wait_for(
                        get_tma_shortlink(int(uid), token, file_data, bot_username),
                        timeout=4.0   # give up after 4 seconds
                    )
                )
            except asyncio.TimeoutError:
                print("Warning: shortlink generation timed out — using direct bot link fallback")
                short_link = ""
            finally:
                loop.close()
        except Exception as e:
            print(f"Error generating shortlink: {e}")

    # Check if user is already TMA-verified
    is_verified = False
    remaining_time = 0
    if uid and token:
        try:
            from utils import check_tma_verification, TMA_TIMEOUT
            import time as _time
            loop2 = asyncio.new_event_loop()
            asyncio.set_event_loop(loop2)
            try:
                is_verified = loop2.run_until_complete(
                    asyncio.wait_for(check_tma_verification(int(uid)), timeout=3.0)
                )
            finally:
                loop2.close()
            if is_verified:
                # Calculate remaining time
                from utils import TMA_VERIFIED
                key = int(uid)
                if key in TMA_VERIFIED:
                    val = TMA_VERIFIED[key]
                    if isinstance(val, dict):
                        verified_at = val.get("verified_at", 0)
                        elapsed = _time.time() - verified_at
                        remaining_time = max(0, int(3600 - elapsed))
                    else:
                        elapsed = _time.time() - val
                        remaining_time = max(0, int(TMA_TIMEOUT - elapsed))
        except Exception as e:
            print(f"Error checking TMA verification: {e}")

    return render_template(
        'index.html',
        monetag_zone_id = zone,
        user_id         = uid,
        token           = token,
        bot_username    = bot_username,
        file_id         = file_data,          # passed to JS for display/share
        file_deeplink   = file_data,          # used to build the bot ?start= link
        short_link      = short_link,
        is_verified     = is_verified,
        remaining_time  = remaining_time,
    )


@app.route('/tma-verify', methods=['POST'])
def tma_verify():
    """
    Called by the Mini App JS after a successful ad view.
    Validates the HMAC token and returns a deeplink that includes the file data
    so the bot can deliver the correct file immediately.
    """
    from config import TMA_SECRET_KEY, BOT_USERNAME
    import hmac as _hmac, hashlib, time as _time

    data     = request.get_json(silent=True) or {}
    uid_str  = str(data.get('uid', ''))
    token    = str(data.get('token', ''))
    file_data = str(data.get('file', ''))   # file /start param forwarded from JS
    bot_username = str(data.get('bot', BOT_USERNAME))

    # ── Validate HMAC token ──
    try:
        ts_str, sig = token.split('-', 1)
        ts = int(ts_str)
        if _time.time() - ts > 600:          # 10-minute window
            return jsonify({'ok': False, 'error': 'expired'}), 400
        raw      = f"{uid_str}:{ts_str}"
        expected = _hmac.new(TMA_SECRET_KEY.encode(), raw.encode(), hashlib.sha256).hexdigest()[:16]
        if not _hmac.compare_digest(sig, expected):
            return jsonify({'ok': False, 'error': 'invalid'}), 400
    except Exception:
        return jsonify({'ok': False, 'error': 'bad_token'}), 400

    # ── Build deeplink ──
    # If we have the file data, point directly at the file.
    # Otherwise fall back to the TMA verification callback so the bot marks
    # the user as verified and then re-delivers the pending file.
    if file_data:
        deeplink = f"https://t.me/{bot_username}?start={file_data}"
    else:
        deeplink = f"https://t.me/{bot_username}?start=tma-{uid_str}-{token}"

    return jsonify({'ok': True, 'deeplink': deeplink})

@app.route('/portal')
def portal():
    """Serve the Movie Portal TMA page."""
    return render_template('portal.html')

@app.route('/portal-data')
def portal_data():
    """API to fetch paginated posts, categories, and search results for the Portal."""
    from pymongo import MongoClient
    from config import DB_URI
    import math

    page = int(request.args.get('page', 1))
    category = request.args.get('category', 'All')
    search = request.args.get('search', '')
    limit = int(request.args.get('limit', 100))

    db_client = MongoClient(DB_URI)
    db = db_client["cloned_vjbotz"]

    query = {"is_gdrive": True}
    if category != 'All':
        query['category'] = category
    if search:
        query['title'] = {'$regex': search, '$options': 'i'}

    total_posts = db.posts.count_documents(query)
    total_pages = math.ceil(total_posts / limit) or 1
    page = max(1, min(page, total_pages))
    skip = (page - 1) * limit

    # Sort: paid/premium posts ALWAYS first, then newest
    posts_cursor = db.posts.find(query).sort(
        [('is_paid', -1), ('created_at', -1)]
    ).skip(skip).limit(limit)
    posts = []
    for doc in posts_cursor:
        posts.append({
            'id': str(doc['_id']),
            'title': doc.get('title', ''),
            'image_url': doc.get('image_url', ''),
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
            'is_gdrive': bool(doc.get('is_gdrive', False))
        })

    # Get unique categories
    categories = ['All']
    unique_cats = db.posts.distinct('category')
    for cat in unique_cats:
        if cat and cat not in categories:
            categories.append(cat)

    return jsonify({
        'posts': posts,
        'categories': categories,
        'page': page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    })

@app.route('/api/view-post', methods=['POST'])
def api_view_post():
    from pymongo import MongoClient
    from config import DB_URI
    try:
        data = request.get_json()
        post_id = data.get('post_id')
        if not post_id:
            return jsonify({"success": False, "error": "Missing post_id"}), 400
            
        db_client = MongoClient(DB_URI)
        db = db_client["cloned_vjbotz"]
        
        db.posts.update_one(
            {"_id": post_id},
            {"$inc": {"views": 10}}
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/react-post', methods=['POST'])
def api_react_post():
    from pymongo import MongoClient
    from config import DB_URI
    try:
        data = request.get_json()
        post_id = data.get('post_id')
        emoji = data.get('emoji')
        
        if not post_id or not emoji:
            return jsonify({"success": False, "error": "Missing post_id or emoji"}), 400
            
        if emoji not in ["❤️", "👍", "🔥", "💦"]:
            return jsonify({"success": False, "error": "Invalid emoji"}), 400
            
        db_client = MongoClient(DB_URI)
        db = db_client["cloned_vjbotz"]
        
        db.posts.update_one(
            {"_id": post_id},
            {"$inc": {f"reactions.{emoji}": 1}}
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500




@app.route('/api/check-vip')
def api_check_vip():
    """API endpoint to check if a user is VIP."""
    from pymongo import MongoClient
    from config import DB_URI
    import time

    uid = request.args.get('uid', '')
    bot_username = request.args.get('bot', '')

    if not uid or not bot_username:
        return jsonify({'is_vip': False})

    db_client = MongoClient(DB_URI)
    db = db_client["cloned_vjbotz"]

    bot_doc = db.bots.find_one({"username": bot_username})
    if not bot_doc:
        return jsonify({'is_vip': False})

    bot_id = bot_doc["bot_id"]
    vip_user = db.vip_users.find_one({"bot_id": int(bot_id), "user_id": int(uid)})

    is_user_vip = False
    if vip_user:
        expiry = vip_user.get("expiry")
        if expiry is None or time.time() < expiry:
            is_user_vip = True

    return jsonify({'is_vip': is_user_vip})


# ─── GDrive Video Feed (for React Native App) ────────────────────────────────

CLOUDFLARE_WORKER_URL = "https://appvideo.solankipriyanshu94.workers.dev"

def _get_gdrive_service_app():
    """Returns authenticated Google Drive service for app.py."""
    import os
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials

    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    elif os.path.exists('service_account.json'):
        creds = service_account.Credentials.from_service_account_file(
            'service_account.json', scopes=scopes
        )
    else:
        raise FileNotFoundError("No Google credentials found.")
    return build('drive', 'v3', credentials=creds)


def _list_gdrive_files_app(folder_id, page_size=50):
    """Lists .dat video files in a GDrive folder."""
    try:
        service = _get_gdrive_service_app()
        query = f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query,
            pageSize=page_size,
            fields="files(id, name, description, mimeType, createdTime, thumbnailLink, appProperties)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        print(f"GDrive list files error: {e}")
        return []


def _list_gdrive_subfolders_app(parent_folder_id):
    """Lists sub-folders in a GDrive folder."""
    try:
        service = _get_gdrive_service_app()
        query = f"'{parent_folder_id}' in parents and trashed=false and mimeType = 'application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query,
            pageSize=100,
            fields="files(id, name, description)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        print(f"GDrive list subfolders error: {e}")
        return []


def _gdrive_file_to_post_app(gfile, category_name="All"):
    """Converts a GDrive file dict to React Native app post format."""
    props = gfile.get('appProperties') or {}
    file_id = gfile['id']
    title = props.get('title') or gfile['name'].replace('.dat', '').replace('-', ' ').replace('_', ' ').title()
    thumbnail = props.get('thumbnail_url') or gfile.get('thumbnailLink') or \
        'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80'
    stream_url = f"{CLOUDFLARE_WORKER_URL}/video.mp4?fileId={file_id}"

    # Handle multi-part videos stored as comma-separated file IDs in appProperties
    raw_ids = props.get('gdrive_file_ids', '')
    if raw_ids and isinstance(raw_ids, str):
        gdrive_file_ids = [x.strip() for x in raw_ids.split(',') if x.strip()]
    elif isinstance(raw_ids, list):
        gdrive_file_ids = raw_ids
    else:
        gdrive_file_ids = [file_id]

    return {
        "id": file_id,
        "title": title,
        "category": category_name,
        "views": int(props.get('views', 0)),
        "duration": props.get('duration', '03:15'),
        "image_url": thumbnail,
        "stream_url": stream_url,
        "is_gdrive": True,
        "gdrive_file_id": file_id,
        "gdrive_file_ids": gdrive_file_ids,
        "is_paid": props.get('is_paid', 'false') == 'true',
        "bot_username": props.get('bot_username', 'ViralVideosBot'),
        "created_time": gfile.get('createdTime', ''),
        "reactions": {"❤️": 0, "👍": 0, "🔥": 0, "💦": 0},
    }


@app.route('/gdrive-portal-data')
def gdrive_portal_data():
    """
    GDrive-based video feed for React Native app.
    Lists .dat files from GDrive folder, returns stream URLs via Cloudflare Worker.
    Query params: category (All or folder ID/name), limit, page
    """
    from config import GDRIVE_FOLDER_ID
    import math

    category = request.args.get('category', 'All')
    limit = int(request.args.get('limit', 30))
    page = int(request.args.get('page', 1))

    try:
        posts = []

        if category == 'All':
            files = _list_gdrive_files_app(GDRIVE_FOLDER_ID, page_size=limit * page)
            for f in files:
                posts.append(_gdrive_file_to_post_app(f, category_name='All'))
        else:
            subfolders = _list_gdrive_subfolders_app(GDRIVE_FOLDER_ID)
            matched_folder = None
            for folder in subfolders:
                if folder['id'] == category or folder['name'].lower() == category.lower():
                    matched_folder = folder
                    break

            if matched_folder:
                files = _list_gdrive_files_app(matched_folder['id'], page_size=limit * page)
                for f in files:
                    posts.append(_gdrive_file_to_post_app(f, category_name=matched_folder['name']))
            else:
                files = _list_gdrive_files_app(GDRIVE_FOLDER_ID, page_size=limit * page)
                for f in files:
                    posts.append(_gdrive_file_to_post_app(f, category_name='All'))

        # Simple pagination: slice to current page
        start = (page - 1) * limit
        end = start + limit
        paged_posts = posts[start:end]
        total_pages = math.ceil(len(posts) / limit) if posts else 1

        return jsonify({
            "status": "ok",
            "posts": paged_posts,
            "categories": ['All'],
            "page": page,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        })

    except Exception as e:
        print(f"/gdrive-portal-data error: {e}")
        return jsonify({"error": str(e), "posts": [], "categories": ['All']}), 500


@app.route('/gdrive-folders')
def gdrive_folders_app():
    """Returns GDrive sub-folders as categories for the React Native app."""
    from config import GDRIVE_FOLDER_ID
    try:
        folders = _list_gdrive_subfolders_app(GDRIVE_FOLDER_ID)
        categories = [{"id": f['id'], "name": f['name']} for f in folders]
        return jsonify({"categories": categories})
    except Exception as e:
        return jsonify({"error": str(e), "categories": []}), 500


if __name__ == "__main__":
    app.run()
