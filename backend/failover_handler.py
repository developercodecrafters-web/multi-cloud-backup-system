from typing import Dict

from .cloud_backup import perform_cloud_backup
from .local_backup import perform_local_backup
from .logger import log_event


def handle_backup(
    src_dir: str,
    local_dest: str,
    cloud_target: str,
    cloud_prefix: str = "supply-chain-backups",
    cloud_provider: str = "aws_s3",
    cloud_auth_mode: str = "",
    cloud_even_if_local_success: bool = True,
) -> Dict[str, object]:
    """Run backup with failover logic.

    Attempt local backup first. If it fails, switch to cloud backup.
    Optionally run cloud backup even when local succeeds for redundancy.
    """
    result = {
        "local": {"success": False, "files": 0, "error": ""},
        "cloud": {"success": False, "files": 0, "error": ""},
        "failover_used": False,
    }

    log_event("Backup Started")
    local_success, files_processed, local_error = perform_local_backup(src_dir, local_dest)
    result["local"] = {
        "success": local_success,
        "files": files_processed,
        "error": local_error,
    }

    if local_success:
        log_event("Local Backup Success")
        if cloud_even_if_local_success:
            cloud_result = perform_cloud_backup(
                src_dir=src_dir,
                cloud_target=cloud_target,
                cloud_prefix=cloud_prefix,
                cloud_provider=cloud_provider,
                cloud_auth_mode=cloud_auth_mode,
            )
            result["cloud"] = {
                "success": cloud_result["success"],
                "files": cloud_result["files_uploaded"],
                "error": cloud_result["error"],
            }
            if cloud_result["success"]:
                log_event("Cloud Backup Success")
            else:
                log_event(f"Cloud Backup Failed: {cloud_result['error']}")
        return result

    # Failover path
    log_event(f"Local Backup Failed: {local_error}")
    result["failover_used"] = True

    cloud_result = perform_cloud_backup(
        src_dir=src_dir,
        cloud_target=cloud_target,
        cloud_prefix=cloud_prefix,
        cloud_provider=cloud_provider,
        cloud_auth_mode=cloud_auth_mode,
    )
    result["cloud"] = {
        "success": cloud_result["success"],
        "files": cloud_result["files_uploaded"],
        "error": cloud_result["error"],
    }

    if cloud_result["success"]:
        log_event("Cloud Backup Success (Failover)")
    else:
        log_event(f"Cloud Backup Failed (Failover): {cloud_result['error']}")

    return result
