import os
import shutil
from typing import Tuple


def perform_local_backup(src_dir: str, dest_dir: str) -> Tuple[bool, int, str]:
    """Copy files from src_dir to dest_dir.

    Returns (success, files_processed, error_message).
    """
    try:
        if not os.path.isdir(src_dir):
            return False, 0, f"Source directory not found: {src_dir}"

        os.makedirs(dest_dir, exist_ok=True)
        files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
        processed = 0
        for filename in files:
            src_path = os.path.join(src_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            shutil.copy2(src_path, dest_path)
            processed += 1

        return True, processed, ""
    except Exception as exc:
        return False, 0, str(exc)
