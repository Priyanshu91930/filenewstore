"""
portal_server.py - Flask API Server for Viral Videos App
=========================================================
Serves video metadata from Google Drive to the React Native app.
Runs on your EC2 server.

Endpoints:
  GET /portal-data?category=All  -> Returns video list for Home / Collection
  GET /gdrive-folders             -> Lists GDrive sub-folders as categories
  GET /health                     -> Health check
"""

import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials

# ─── Config ─────────────────────────────────────────────────────────────────
try:
    from config import GDRIVE_FOLDER_ID, GDRIVE_SERVICE_ACCOUNT_FILE
except ImportError:
    GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "")
    GDRIVE_SERVICE_ACCOUNT_FILE = os.environ.get("GDRIVE_SERVICE_ACCOUNT_FILE", "service_account.json")

CLOUDFLARE_WORKER_URL = os.environ.get(
    "CLOUDFLARE_WORKER_URL",
    "https://appvideo.solankipriyanshu94.workers.dev"
)

# ─── Setup ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Allow React Native app to call this API from any IP


# ─── GDrive Service ──────────────────────────────────────────────────────────
def get_gdrive_service():
    """Returns authenticated Google Drive service."""
    scopes = ['https://www.googleapis.com/auth/drive.readonly']
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    elif os.path.exists(GDRIVE_SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(
            GDRIVE_SERVICE_ACCOUNT_FILE, scopes=scopes
        )
    else:
        raise FileNotFoundError("No Google credentials found (token.json or service_account.json).")
    return build('drive', 'v3', credentials=creds)


# ─── List files from a GDrive folder ─────────────────────────────────────────
def list_gdrive_files(folder_id, page_size=50):
    """
    Lists all .dat video files inside a specific GDrive folder.
    Returns list of dicts with id, name, etc.
    """
    try:
        service = get_gdrive_service()
        query = f"'{folder_id}' in parents and trashed=false and mimeType != 'application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query,
            pageSize=page_size,
            fields="files(id, name, description, mimeType, createdTime, modifiedTime, thumbnailLink, appProperties)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        logger.error(f"GDrive list files error: {e}")
        return []


def list_gdrive_subfolders(parent_folder_id):
    """
    Lists all sub-folders inside a GDrive folder.
    These are used as dynamic categories in the app.
    """
    try:
        service = get_gdrive_service()
        query = f"'{parent_folder_id}' in parents and trashed=false and mimeType = 'application/vnd.google-apps.folder'"
        results = service.files().list(
            q=query,
            pageSize=100,
            fields="files(id, name, description)"
        ).execute()
        return results.get('files', [])
    except Exception as e:
        logger.error(f"GDrive list subfolders error: {e}")
        return []


# ─── Map GDrive file -> App post format ──────────────────────────────────────
def gdrive_file_to_post(gfile, category_name="All", is_paid=False):
    """
    Converts a GDrive file dict to the video post format expected by the React Native app.
    Uses appProperties stored during upload for: title, thumbnail, duration, views.
    """
    props = gfile.get('appProperties') or {}
    file_id = gfile['id']

    # Title: use appProperties title, or fall back to cleaned filename
    title = props.get('title') or gfile['name'].replace('.dat', '').replace('-', ' ').replace('_', ' ').title()

    # Thumbnail: use appProperties thumbnail_url if present
    thumbnail = props.get('thumbnail_url') or gfile.get('thumbnailLink') or \
        'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80'

    # Stream URL via Cloudflare Worker
    stream_url = f"{CLOUDFLARE_WORKER_URL}/stream?fileId={file_id}"

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
        "gdrive_file_ids": props.get('gdrive_file_ids', [file_id]),  # multi-part support
        "is_paid": is_paid or props.get('is_paid', 'false') == 'true',
        "bot_username": props.get('bot_username', 'ViralVideosBot'),
        "created_time": gfile.get('createdTime', ''),
    }


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "server": "Viral Videos Portal API"})


@app.route('/gdrive-folders', methods=['GET'])
def gdrive_folders():
    """
    Returns list of GDrive sub-folders as categories.
    App uses these to populate the category chips in Collection screen.
    """
    try:
        folders = list_gdrive_subfolders(GDRIVE_FOLDER_ID)
        categories = [
            {"id": f['id'], "name": f['name'], "description": f.get('description', '')}
            for f in folders
        ]
        return jsonify({"categories": categories})
    except Exception as e:
        logger.error(f"/gdrive-folders error: {e}")
        return jsonify({"error": str(e), "categories": []}), 500


@app.route('/portal-data', methods=['GET'])
def portal_data():
    """
    Main video feed endpoint.
    Query params:
      - category: 'All' (default) or GDrive folder ID for category filtering
      - limit: number of results (default 30)
    """
    category = request.args.get('category', 'All')
    limit = int(request.args.get('limit', 30))

    try:
        posts = []

        if category == 'All':
            # Fetch from the main root GDrive folder directly
            files = list_gdrive_files(GDRIVE_FOLDER_ID, page_size=limit)
            for f in files:
                posts.append(gdrive_file_to_post(f, category_name='All'))

            # Also gather from all sub-folders if main folder is empty
            if not posts:
                subfolders = list_gdrive_subfolders(GDRIVE_FOLDER_ID)
                for folder in subfolders:
                    folder_files = list_gdrive_files(folder['id'], page_size=10)
                    for f in folder_files:
                        posts.append(gdrive_file_to_post(f, category_name=folder['name']))
                    if len(posts) >= limit:
                        break
        else:
            # Category is a GDrive folder ID (sent from app after /gdrive-folders fetch)
            # Or it's a category name — try to match sub-folder by name
            subfolders = list_gdrive_subfolders(GDRIVE_FOLDER_ID)
            matched_folder = None

            for folder in subfolders:
                if folder['id'] == category or folder['name'].lower() == category.lower():
                    matched_folder = folder
                    break

            if matched_folder:
                files = list_gdrive_files(matched_folder['id'], page_size=limit)
                for f in files:
                    posts.append(gdrive_file_to_post(f, category_name=matched_folder['name']))
            else:
                # Fallback: return root folder files
                files = list_gdrive_files(GDRIVE_FOLDER_ID, page_size=limit)
                for f in files:
                    posts.append(gdrive_file_to_post(f, category_name='All'))

        return jsonify({
            "status": "ok",
            "category": category,
            "count": len(posts),
            "posts": posts
        })

    except Exception as e:
        logger.error(f"/portal-data error: {e}")
        return jsonify({"error": str(e), "posts": []}), 500


# ─── Run ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Viral Videos Portal Server on port {port}...")
    logger.info(f"GDrive Folder ID: {GDRIVE_FOLDER_ID}")
    app.run(host='0.0.0.0', port=port, debug=False)
