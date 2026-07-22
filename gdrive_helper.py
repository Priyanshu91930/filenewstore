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
        
    if not GDRIVE_FOLDER_ID:
        return None, "GDRIVE_FOLDER_ID is not configured in config.py"

    temp_encrypted_path = None
    try:
        # Load Google Credentials
        scopes = ['https://www.googleapis.com/auth/drive']
        creds = None
        
        # Check if token.json (User OAuth2) is present - RECOMMENDED for personal accounts
        if os.path.exists('token.json'):
            logger.info("Loading Google Drive OAuth2 User credentials from token.json...")
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        # Fallback to Service Account
        elif os.path.exists(GDRIVE_SERVICE_ACCOUNT_FILE):
            logger.info(f"Loading Google Drive Service Account credentials from {GDRIVE_SERVICE_ACCOUNT_FILE}...")
            creds = service_account.Credentials.from_service_account_file(GDRIVE_SERVICE_ACCOUNT_FILE, scopes=scopes)
        else:
            return None, "Google Credentials not found. Please provide token.json or service_account.json"
            
        service = build('drive', 'v3', credentials=creds)
        
        # Mask the filename to bypass AI scanning (UUID + .dat)
        file_ext = ".dat"
        masked_filename = f"{uuid.uuid4()}{file_ext}"
        logger.info(f"Masking file: '{original_filename}' -> '{masked_filename}'")
        
        # Encrypt the file using XOR (key 0x5A) to block Google AI scans and previews
        temp_encrypted_path = f"{local_file_path}.enc"
        logger.info(f"Encrypting file with XOR: {local_file_path} -> {temp_encrypted_path}")
        try:
            with open(local_file_path, 'rb') as f_in:
                with open(temp_encrypted_path, 'wb') as f_out:
                    while True:
                        chunk = f_in.read(65536)
                        if not chunk:
                            break
                        f_out.write(bytes(b ^ 0x5A for b in chunk))
        except Exception as enc_err:
            return None, f"XOR Encryption Failed: {enc_err}"
        
        # Prepare file metadata and media upload
        file_metadata = {
            'name': masked_filename,
            'parents': [GDRIVE_FOLDER_ID]
        }
        
        # Determine appropriate chunk size (e.g. 5MB)
        chunk_size = 5 * 1024 * 1024
        media = MediaFileUpload(
            temp_encrypted_path, 
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
    finally:
        if temp_encrypted_path and os.path.exists(temp_encrypted_path):
            try:
                os.remove(temp_encrypted_path)
                logger.info(f"Cleaned up temporary encrypted file: {temp_encrypted_path}")
            except Exception as clean_err:
                logger.error(f"Failed to delete temporary encrypted file: {clean_err}")
