import os
import re
import json
from datetime import timedelta
from pathlib import Path

# Check if we have credentials for real mode
_has_credentials = "GOOGLE_SERVICE_ACCOUNT_JSON" in os.environ

# GCS bucket name (create this in your GCP console)
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "qa-calls-audio")

# Mock storage directory (persists across restarts)
MOCK_AUDIO_DIR = Path(__file__).parent.parent / ".mock_audio"
MOCK_AUDIO_DIR.mkdir(exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and invalid characters"""
    # Remove path components
    filename = os.path.basename(filename)
    # Replace invalid characters with underscores
    return re.sub(r'[^a-zA-Z0-9._-]', '_', filename)


def get_storage_client():
    """Get Google Cloud Storage client, or None for mock mode"""
    if not _has_credentials:
        return None
    try:
        from google.cloud import storage
        creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        client = storage.Client(credentials=credentials, project=creds_dict.get('project_id'))
        return client
    except (json.JSONDecodeError, ImportError, KeyError) as e:
        print(f"Storage client error: {e}")
        return None


def upload_audio(audio_bytes: bytes, filename: str, timestamp: str) -> str | None:
    """
    Upload audio file to GCS or mock storage.
    Returns the blob name on success, None on failure.
    """
    global mock_audio_storage

    # Sanitize filename and create unique blob name
    safe_filename = sanitize_filename(filename)
    blob_name = f"{timestamp.replace(' ', '_').replace(':', '-')}_{safe_filename}"

    try:
        client = get_storage_client()
        if client is not None:
            bucket = client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)

            # Determine content type from filename
            content_type = "audio/mpeg"
            if filename.lower().endswith(".wav"):
                content_type = "audio/wav"
            elif filename.lower().endswith(".m4a"):
                content_type = "audio/mp4"
            elif filename.lower().endswith(".ogg"):
                content_type = "audio/ogg"

            blob.upload_from_string(audio_bytes, content_type=content_type)
            return blob_name
        else:
            # Mock mode: store to disk (persists across restarts)
            mock_path = MOCK_AUDIO_DIR / blob_name
            mock_path.write_bytes(audio_bytes)
            return blob_name
    except Exception:
        return None


def get_audio_url(blob_name: str) -> str | None:
    """
    Get a signed URL for audio playback.
    Returns URL on success, None on failure.
    """
    if not blob_name:
        return None

    try:
        client = get_storage_client()
        if client is not None:
            bucket = client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)

            # Generate signed URL valid for 1 hour
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="GET"
            )
            return url
        else:
            # Mock mode: check if file exists on disk
            mock_path = MOCK_AUDIO_DIR / blob_name
            if mock_path.exists():
                from urllib.parse import quote
                return f"/api/audio?file={quote(blob_name)}"
            return None
    except Exception as e:
        print(f"[DEBUG] get_audio_url exception: {e}")
        return None


def get_mock_audio(blob_name: str) -> bytes | None:
    """Get audio bytes from mock storage (for local testing)"""
    mock_path = MOCK_AUDIO_DIR / blob_name
    if mock_path.exists():
        return mock_path.read_bytes()
    return None
