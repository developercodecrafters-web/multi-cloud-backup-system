import os
from typing import Dict

import boto3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file"


def _upload_to_s3(src_dir: str, bucket_name: str, s3_prefix: str = "") -> Dict[str, object]:
    """Upload files from src_dir to the given S3 bucket.

    Returns dict with keys: success, files_uploaded, error.
    """
    result = {"success": False, "files_uploaded": 0, "error": ""}

    if not os.path.isdir(src_dir):
        result["error"] = f"Source directory not found: {src_dir}"
        return result

    try:
        s3 = boto3.client("s3")
        files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]

        for filename in files:
            src_path = os.path.join(src_dir, filename)
            key = f"{s3_prefix}/{filename}".strip("/")
            s3.upload_file(src_path, bucket_name, key)

            # Verify upload succeeded
            s3.head_object(Bucket=bucket_name, Key=key)
            result["files_uploaded"] += 1

        result["success"] = True
        return result
    except (NoCredentialsError, PartialCredentialsError) as exc:
        result["error"] = f"AWS credentials error: {exc}"
        return result
    except (ClientError, BotoCoreError) as exc:
        result["error"] = f"AWS error: {exc}"
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result


def _build_drive_service_with_service_account() -> object:
    key_file = os.getenv("GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE", "").strip()
    if not key_file:
        raise ValueError("Missing GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE environment variable.")
    if not os.path.isfile(key_file):
        raise ValueError(f"Google service account file not found: {key_file}")

    credentials = service_account.Credentials.from_service_account_file(
        key_file,
        scopes=[DRIVE_FILE_SCOPE],
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def _build_drive_service_with_oauth() -> object:
    client_secret_file = os.getenv("GOOGLE_DRIVE_OAUTH_CLIENT_SECRET_FILE", "").strip()
    if not client_secret_file:
        raise ValueError("Missing GOOGLE_DRIVE_OAUTH_CLIENT_SECRET_FILE environment variable.")
    if not os.path.isfile(client_secret_file):
        raise ValueError(f"OAuth client secret file not found: {client_secret_file}")

    token_file = os.getenv("GOOGLE_DRIVE_OAUTH_TOKEN_FILE", "google_drive_token.json").strip()
    local_server_port = int(os.getenv("GOOGLE_DRIVE_OAUTH_LOCAL_SERVER_PORT", "8080"))
    creds = None

    if token_file and os.path.isfile(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes=[DRIVE_FILE_SCOPE])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scopes=[DRIVE_FILE_SCOPE])
            creds = flow.run_local_server(port=local_server_port)

        if token_file:
            with open(token_file, "w", encoding="utf-8") as token:
                token.write(creds.to_json())

    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _upload_to_google_drive(src_dir: str, folder_id: str, auth_mode: str = "oauth") -> Dict[str, object]:
    """Upload files from src_dir to a Google Drive folder.

    Auth mode:
    - oauth: requires GOOGLE_DRIVE_OAUTH_CLIENT_SECRET_FILE
    - service_account: requires GOOGLE_DRIVE_SERVICE_ACCOUNT_FILE
    """
    result = {"success": False, "files_uploaded": 0, "error": ""}

    if not os.path.isdir(src_dir):
        result["error"] = f"Source directory not found: {src_dir}"
        return result

    if not folder_id:
        result["error"] = "Google Drive folder ID is required."
        return result

    try:
        normalized_auth_mode = (auth_mode or "oauth").strip().lower()
        if normalized_auth_mode == "oauth":
            drive = _build_drive_service_with_oauth()
        elif normalized_auth_mode == "service_account":
            drive = _build_drive_service_with_service_account()
        else:
            result["error"] = f"Unsupported Google Drive auth mode: {auth_mode}"
            return result

        files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]

        for filename in files:
            src_path = os.path.join(src_dir, filename)
            media = MediaFileUpload(src_path, resumable=False)
            file_metadata = {"name": filename, "parents": [folder_id]}
            uploaded = drive.files().create(body=file_metadata, media_body=media, fields="id").execute()

            if uploaded.get("id"):
                result["files_uploaded"] += 1

        result["success"] = True
        return result
    except HttpError as exc:
        result["error"] = f"Google Drive API error: {exc}"
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result


def perform_cloud_backup(
    src_dir: str,
    cloud_target: str,
    cloud_prefix: str = "",
    cloud_provider: str = "aws_s3",
    cloud_auth_mode: str = "",
) -> Dict[str, object]:
    """Upload files to configured cloud provider.

    `cloud_provider` supports: aws_s3, google_drive
    `cloud_target` means bucket name for S3, folder ID for Google Drive.
    """
    provider = (cloud_provider or "").strip().lower()

    if provider == "aws_s3":
        return _upload_to_s3(src_dir, cloud_target, cloud_prefix)
    if provider == "google_drive":
        return _upload_to_google_drive(src_dir, cloud_target, cloud_auth_mode or "oauth")

    return {
        "success": False,
        "files_uploaded": 0,
        "error": f"Unsupported cloud provider: {cloud_provider}",
    }
