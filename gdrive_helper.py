import os
import uuid
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Configure logging
logger = logging.getLogger(__name__)

# Import configurations
try:
    from config import GDRIVE_FOLDER_ID, GDRIVE_SERVICE_ACCOUNT_FILE
except ImportError:
    GDRIVE_FOLDER_ID = ""
    GDRIVE_SERVICE_ACCOUNT_FILE = "service_account.json"

def upload_file_to_gdrive(local_file_path, original_filename):
    """
    Uploads a local file to Google Drive with anti-ban masking (.dat extension)
    and shares it publicly so it can be streamed via Cloudflare Worker proxy.
    
    Returns:
        tuple: (file_id, masked_filename) if successful, (None, error_message) if failed.
    """
    if not os.path.exists(local_file_path):
        return None, f"Local file does not exist: {local_file_path}"
        
    sa_path = GDRIVE_SERVICE_ACCOUNT_FILE
    if not os.path.exists(sa_path):
        return None, f"Google Service Account key file not found at: {sa_path}"
        
    if not GDRIVE_FOLDER_ID:
        return None, "GDRIVE_FOLDER_ID is not configured in config.py"

    try:
        # Load Google Credentials
        scopes = ['https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_file(sa_path, scopes=scopes)
        service = build('drive', 'v3', credentials=creds)
        
        # Mask the filename to bypass AI scanning (UUID + .dat)
        file_ext = ".dat"
        masked_filename = f"{uuid.uuid4()}{file_ext}"
        logger.info(f"Masking file: '{original_filename}' -> '{masked_filename}'")
        
        # Prepare file metadata and media upload
        file_metadata = {
            'name': masked_filename,
            'parents': [GDRIVE_FOLDER_ID]
        }
        
        # Determine appropriate chunk size (e.g. 5MB)
        chunk_size = 5 * 1024 * 1024
        media = MediaFileUpload(
            local_file_path, 
            mimetype='application/octet-stream', 
            resumable=True,
            chunksize=chunk_size
        )
        
        # Upload the file
        logger.info(f"Starting GDrive upload for {masked_filename}...")
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"GDrive Upload progress: {int(status.progress() * 100)}%")
                
        file_id = response.get('id')
        logger.info(f"Successfully uploaded to GDrive. File ID: {file_id}")
        
        # Set permission: Anyone with link can view (Reader role)
        logger.info(f"Sharing file {file_id} publicly...")
        user_permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        service.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id'
        ).execute()
        
        logger.info(f"File {file_id} is now publicly shared for streaming.")
        return file_id, masked_filename
        
    except Exception as e:
        error_msg = f"GDrive Upload Exception: {e}"
        logger.error(error_msg)
        return None, error_msg
