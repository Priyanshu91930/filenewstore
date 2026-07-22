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


def _get_gdrive_service():
    """Load Google credentials and return an authenticated Drive service."""
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = None

    if os.path.exists('token.json'):
        logger.info("Loading Google Drive OAuth2 User credentials from token.json...")
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    elif os.path.exists(GDRIVE_SERVICE_ACCOUNT_FILE):
        logger.info(f"Loading Google Drive Service Account credentials from {GDRIVE_SERVICE_ACCOUNT_FILE}...")
        creds = service_account.Credentials.from_service_account_file(GDRIVE_SERVICE_ACCOUNT_FILE, scopes=scopes)
    else:
        raise FileNotFoundError("Google Credentials not found. Please provide token.json or service_account.json")

    return build('drive', 'v3', credentials=creds)


def create_gdrive_folder(folder_name, parent_folder_id=None):
    """
    Creates a folder inside Google Drive (inside the main GDRIVE_FOLDER_ID by default).
    The folder name is set to a random UUID to avoid Google AI detection.

    Returns:
        tuple: (folder_id, masked_folder_name) if successful, (None, error_message) if failed.
    """
    if not GDRIVE_FOLDER_ID:
        return None, "GDRIVE_FOLDER_ID is not configured in config.py"

    try:
        service = _get_gdrive_service()

        # Use a random UUID as the folder name (anti-ban masking)
        masked_folder_name = str(uuid.uuid4())
        parent_id = parent_folder_id or GDRIVE_FOLDER_ID

        folder_metadata = {
            'name': masked_folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }

        folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()

        folder_id = folder.get('id')
        logger.info(f"Created GDrive folder '{masked_folder_name}' (original: '{folder_name}') -> ID: {folder_id}")

        # Make the folder publicly accessible
        service.permissions().create(
            fileId=folder_id,
            body={'type': 'anyone', 'role': 'reader'},
            fields='id'
        ).execute()

        return folder_id, masked_folder_name

    except Exception as e:
        error_msg = f"GDrive Folder Creation Exception: {e}"
        logger.error(error_msg)
        return None, error_msg


def _xor_encrypt_file(src_path, dst_path, key=0x5A):
    """Encrypts a file using XOR key and writes to dst_path."""
    with open(src_path, 'rb') as f_in:
        with open(dst_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(65536)
                if not chunk:
                    break
                f_out.write(bytes(b ^ key for b in chunk))


def upload_file_to_gdrive(local_file_path, original_filename, parent_folder_id=None):
    """
    Uploads a local file to Google Drive with:
    - Anti-ban masking (.dat extension + UUID name)
    - XOR encryption (key 0x5A) to prevent Google AI preview/scan
    - Public read permissions for Cloudflare Worker streaming

    Args:
        local_file_path: Local path to the video file.
        original_filename: Original file name (for logging only).
        parent_folder_id: Optional Google Drive folder ID to upload into.
                          Defaults to GDRIVE_FOLDER_ID from config.

    Returns:
        tuple: (file_id, masked_filename) if successful, (None, error_message) if failed.
    """
    if not os.path.exists(local_file_path):
        return None, f"Local file does not exist: {local_file_path}"

    if not GDRIVE_FOLDER_ID:
        return None, "GDRIVE_FOLDER_ID is not configured in config.py"

    temp_encrypted_path = None
    try:
        service = _get_gdrive_service()

        # Mask the filename: UUID + .dat
        masked_filename = f"{uuid.uuid4()}.dat"
        logger.info(f"Masking file: '{original_filename}' -> '{masked_filename}'")

        # XOR Encrypt the file before uploading
        temp_encrypted_path = f"{local_file_path}.enc"
        logger.info(f"Encrypting file with XOR (0x5A): {local_file_path} -> {temp_encrypted_path}")
        _xor_encrypt_file(local_file_path, temp_encrypted_path)

        # Set parent folder (batch folder or main folder)
        upload_parent = parent_folder_id or GDRIVE_FOLDER_ID

        # Prepare file metadata
        file_metadata = {
            'name': masked_filename,
            'parents': [upload_parent]
        }

        # Upload using MediaFileUpload with resumable upload
        chunk_size = 5 * 1024 * 1024  # 5MB chunks
        media = MediaFileUpload(
            temp_encrypted_path,
            mimetype='application/octet-stream',
            resumable=True,
            chunksize=chunk_size
        )

        logger.info(f"Starting GDrive upload for '{masked_filename}'...")
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

        # Set public read permission
        service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
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
                logger.info(f"Cleaned up temp encrypted file: {temp_encrypted_path}")
            except Exception as clean_err:
                logger.error(f"Failed to delete temp encrypted file: {clean_err}")
