import os
from typing import Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError


def perform_cloud_backup(src_dir: str, bucket_name: str, s3_prefix: str = "") -> Dict[str, object]:
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
