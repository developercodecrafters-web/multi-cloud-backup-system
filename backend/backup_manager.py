import os
import time
from datetime import datetime
from typing import Dict

from .failover_handler import handle_backup
from .performance_monitor import update_metrics
from .logger import log_event


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")
LOCAL_BACKUP_DIR = os.path.join(PROJECT_ROOT, "backup", "local_backup")


def run_backup(cloud_bucket: str, s3_prefix: str = "supply-chain-backups") -> Dict[str, object]:
    start = time.time()

    result = handle_backup(
        src_dir=DATASET_DIR,
        local_dest=LOCAL_BACKUP_DIR,
        cloud_bucket=cloud_bucket,
        s3_prefix=s3_prefix,
        cloud_even_if_local_success=True,
    )

    end = time.time()
    duration = round(end - start, 3)

    files_processed = result["local"]["files"] if result["local"]["success"] else result["cloud"]["files"]
    overall_success = result["local"]["success"] or result["cloud"]["success"]

    metrics = update_metrics(
        files_processed=files_processed,
        backup_time=duration,
        success=overall_success,
        failover_used=result["failover_used"],
        last_backup_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    log_event("Backup Completed")

    return {
        "result": result,
        "duration": duration,
        "files_processed": files_processed,
        "metrics": metrics,
    }
